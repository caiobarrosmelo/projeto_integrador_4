"""
API para recebimento de dados de localização GPS do ESP32
Usa OSRM para cálculo de ETA mais preciso
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import request, jsonify, Blueprint
import logging

# Importa configurações centralizadas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_CONFIG, ETA_CONFIG, DESTINATIONS, INTERVAL_CONFIG, OSRM_CONFIG
from api.utils import (
    validate_gps_coordinates, validate_bus_line, parse_timestamp,
    create_db_connection, log_api_request,
    get_nearest_destination, calculate_adaptive_interval
)
from api.eta_osrm import (
    calculate_eta_with_osrm, get_traffic_factor_by_hour_osrm
)

# Configuração de logging
logger = logging.getLogger(__name__)

# Cria blueprint para a API de localização
location_bp = Blueprint('location', __name__)

def get_db_connection():
    """Cria conexão com o banco PostgreSQL"""
    return create_db_connection(DATABASE_CONFIG)

def save_location_data(bus_line: str, latitude: float, longitude: float, 
                      timestamp: datetime, db_connection) -> int:
    """Salva dados de localização no banco"""
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO bus_location (bus_line, timestamp_location, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(query, (bus_line, timestamp, latitude, longitude))
        location_id = cursor.fetchone()[0]
        db_connection.commit()
        logger.info(f"Localização salva: ID {location_id}, Linha {bus_line}")
        return location_id
    except Exception as e:
        logger.error(f"Erro ao salvar localização: {e}")
        db_connection.rollback()
        return None

def save_eta_prediction(location_id: int, eta_data: Dict, db_connection):
    """Salva previsão de ETA no banco"""
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO prediction_confidence 
            (location_id, predicted_arrival, confidence_percent, timestamp_prediction)
            VALUES (%s, %s, %s, %s)
        """
        predicted_arrival = datetime.fromisoformat(eta_data['estimated_arrival']) if eta_data['estimated_arrival'] else None
        cursor.execute(query, (location_id, predicted_arrival, eta_data['confidence_percent'], datetime.now()))
        db_connection.commit()
        logger.info(f"Previsão ETA salva para localização {location_id}")
    except Exception as e:
        logger.error(f"Erro ao salvar previsão ETA: {e}")
        db_connection.rollback()

def save_adaptive_interval(location_id: int, interval_seconds: int, db_connection):
    """Salva intervalo adaptativo no banco"""
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO request_interval 
            (location_id, start_time, end_time, interval_seconds)
            VALUES (%s, %s, %s, %s)
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=interval_seconds)
        cursor.execute(query, (location_id, start_time, end_time, interval_seconds))
        db_connection.commit()
        logger.info(f"Intervalo adaptativo salvo: {interval_seconds}s para localização {location_id}")
    except Exception as e:
        logger.error(f"Erro ao salvar intervalo adaptativo: {e}")
        db_connection.rollback()

def calculate_eta_with_osrm_and_history(current_lat: float, current_lon: float,
                                       target_lat: float, target_lon: float,
                                       bus_line: str, db_connection) -> Dict:
    """
    Calcula ETA usando OSRM + histórico da linha para ajustes
    """
    try:
        # 1. Calcula ETA base usando OSRM
        current_hour = datetime.now().hour
        traffic_factor = get_traffic_factor_by_hour_osrm(current_hour)
        
        osrm_result = calculate_eta_with_osrm(
            current_lat, current_lon, target_lat, target_lon, traffic_factor
        )
        
        if osrm_result['status'] != 'success':
            # Fallback para cálculo manual se OSRM falhar
            logger.warning("OSRM falhou, usando cálculo manual")
            return calculate_eta_manual_fallback(current_lat, current_lon, target_lat, target_lon, bus_line, db_connection)
        
        # 2. Ajusta baseado no histórico da linha (opcional)
        history_adjustment = get_history_adjustment(bus_line, current_hour, db_connection)
        
        # 3. Aplica ajuste histórico se disponível
        if history_adjustment != 1.0:
            base_eta = osrm_result['eta_minutes']
            adjusted_eta = base_eta * history_adjustment
            
            # Recalcula timestamp de chegada
            estimated_arrival = datetime.now() + timedelta(minutes=adjusted_eta)
            
            osrm_result.update({
                'eta_minutes': round(adjusted_eta, 1),
                'estimated_arrival': estimated_arrival.isoformat(),
                'history_adjustment': round(history_adjustment, 2),
                'base_eta_minutes': base_eta
            })
        
        return osrm_result
        
    except Exception as e:
        logger.error(f"Erro ao calcular ETA com OSRM: {e}")
        return calculate_eta_manual_fallback(current_lat, current_lon, target_lat, target_lon, bus_line, db_connection)

def get_history_adjustment(bus_line: str, hour: int, db_connection) -> float:
    """
    Obtém ajuste baseado no histórico da linha
    """
    try:
        cursor = db_connection.cursor()
        query = """
            SELECT 
                AVG(EXTRACT(EPOCH FROM (pc.actual_arrival - pc.predicted_arrival))/60) as avg_delay
            FROM prediction_confidence pc
            JOIN bus_location bl ON pc.location_id = bl.id
            WHERE bl.bus_line = %s
            AND pc.actual_arrival IS NOT NULL
            AND EXTRACT(HOUR FROM bl.timestamp_location) = %s
            AND pc.timestamp_prediction >= %s
        """
        
        since = datetime.now() - timedelta(days=7)
        cursor.execute(query, (bus_line, hour, since))
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            avg_delay = result[0]
            # Converte atraso em fator de ajuste
            if avg_delay > 0:
                # Atraso médio de 5 minutos = fator 1.1 (10% mais tempo)
                adjustment = max(0.8, 1.0 + (avg_delay / 50))
            else:
                # Adiantamento médio = fator < 1.0 (menos tempo)
                adjustment = min(1.2, 1.0 + (avg_delay / 50))
            
            return adjustment
        
        return 1.0  # Sem histórico, usa fator neutro
        
    except Exception as e:
        logger.error(f"Erro ao obter ajuste histórico: {e}")
        return 1.0

def calculate_eta_manual_fallback(current_lat: float, current_lon: float,
                                 target_lat: float, target_lon: float,
                                 bus_line: str, db_connection) -> Dict:
    """
    Fallback para cálculo manual se OSRM falhar
    """
    try:
        # Cálculo manual simples baseado em distância
        from api.utils import calculate_distance_km, get_traffic_factor_by_hour
        
        distance = calculate_distance_km(current_lat, current_lon, target_lat, target_lon)
        current_hour = datetime.now().hour
        traffic_factor = get_traffic_factor_by_hour(current_hour)
        
        # Velocidade média para ônibus urbano
        avg_speed = 20.0  # km/h
        adjusted_speed = avg_speed * traffic_factor
        
        eta_minutes = (distance / adjusted_speed) * 60
        estimated_arrival = datetime.now() + timedelta(minutes=eta_minutes)
        
        return {
            'status': 'success',
            'eta_minutes': round(eta_minutes, 1),
            'estimated_arrival': estimated_arrival.isoformat(),
            'distance_km': round(distance, 2),
            'avg_speed_kmh': avg_speed,
            'adjusted_speed_kmh': round(adjusted_speed, 1),
            'confidence_percent': OSRM_CONFIG['confidence_fallback'],  # Menor confiança para cálculo manual
            'traffic_factor': round(traffic_factor, 2),
            'source': 'manual_fallback'
        }
        
    except Exception as e:
        logger.error(f"Erro no fallback manual: {e}")
        return {
            'status': 'error',
            'eta_minutes': 999,
            'estimated_arrival': None,
            'distance_km': 0,
            'confidence_percent': 0,
            'error': str(e)
        }

@location_bp.route('/location', methods=['POST'])
def receive_location():
    """Endpoint para receber dados de localização do ESP32 usando OSRM"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400
        
        data = request.get_json()
        
        # Valida campos obrigatórios
        required_fields = ['bus_line', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400
        
        # Extrai dados
        bus_line = data['bus_line'].strip().upper()
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        # Usa timestamp do ESP32 se fornecido
        if 'timestamp' in data:
            try:
                timestamp = parse_timestamp(data['timestamp'])
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Validações
        if not validate_gps_coordinates(latitude, longitude):
            return jsonify({'error': 'Coordenadas GPS inválidas'}), 400
        
        if not validate_bus_line(bus_line):
            return jsonify({'error': 'Linha de ônibus inválida'}), 400
        
        # Conecta ao banco
        db_connection = get_db_connection()
        if not db_connection:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Salva localização
        location_id = save_location_data(bus_line, latitude, longitude, timestamp, db_connection)
        if not location_id:
            return jsonify({'error': 'Erro ao salvar localização'}), 500
        
        # Encontra destino mais próximo
        nearest_dest = get_nearest_destination(latitude, longitude, DESTINATIONS)
        if not nearest_dest:
            return jsonify({'error': 'Nenhum destino encontrado'}), 500
        
        # Calcula ETA usando OSRM
        eta_data = calculate_eta_with_osrm_and_history(
            latitude, longitude, 
            nearest_dest['latitude'], nearest_dest['longitude'], 
            bus_line, db_connection
        )
        
        # Salva previsão no banco
        save_eta_prediction(location_id, eta_data, db_connection)
        
        # Calcula intervalo adaptativo
        current_hour = datetime.now().hour
        traffic_factor = get_traffic_factor_by_hour_osrm(current_hour)
        adaptive_interval = calculate_adaptive_interval(
            INTERVAL_CONFIG['default_interval_seconds'],
            traffic_factor,
            INTERVAL_CONFIG['min_interval_seconds'],
            INTERVAL_CONFIG['max_interval_seconds']
        )
        
        # Salva intervalo adaptativo
        save_adaptive_interval(location_id, adaptive_interval, db_connection)
        
        # Resposta para o ESP32
        response = {
            'status': 'success',
            'location_id': location_id,
            'destination': nearest_dest,
            'eta': eta_data,
            'adaptive_interval_seconds': adaptive_interval,
            'message': 'Localização recebida e ETA calculado com OSRM'
        }
        
        # Log da requisição
        log_api_request('/api/location', 'POST', data, 200)
        
        db_connection.close()
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erro no endpoint /api/location: {e}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

@location_bp.route('/location/history/<bus_line>', methods=['GET'])
def get_location_history(bus_line: str):
    """Endpoint para consultar histórico de localizações de uma linha"""
    try:
        limit = request.args.get('limit', 50, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        db_connection = get_db_connection()
        if not db_connection:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cursor = db_connection.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT id, latitude, longitude, timestamp_location
            FROM bus_location 
            WHERE bus_line = %s 
            AND timestamp_location >= %s
            ORDER BY timestamp_location DESC
            LIMIT %s
        """
        
        since = datetime.now() - timedelta(hours=hours)
        cursor.execute(query, (bus_line, since, limit))
        locations = cursor.fetchall()
        
        db_connection.close()
        
        return jsonify({
            'bus_line': bus_line,
            'count': len(locations),
            'locations': [dict(loc) for loc in locations]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@location_bp.route('/location/destinations', methods=['GET'])
def get_destinations():
    """Endpoint para listar destinos disponíveis"""
    return jsonify({
        'destinations': DESTINATIONS,
        'count': len(DESTINATIONS)
    }), 200

@location_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

# Exporta o blueprint para uso no main.py
app = location_bp
