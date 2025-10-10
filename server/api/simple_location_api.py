"""
API Simplificada para Localização - Schema Reduzido
Usa create_tables.sql (4 tabelas básicas)
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import json
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import request, jsonify, Blueprint
import os
import sys

# Adiciona o diretório server ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_simple import ETA_CONFIG, DESTINATIONS, INTERVAL_CONFIG, ML_CONFIG
from database.simple_connection import (
    get_simple_database_manager, get_simple_bus_repository,
    get_simple_occupancy_repository, get_simple_eta_repository,
    get_simple_interval_repository
)
from api.utils import (
    validate_gps_coordinates, validate_bus_line, parse_timestamp,
    calculate_distance_km, get_traffic_factor_by_hour, calculate_adaptive_interval,
    get_nearest_destination, log_api_request
)

# Configuração de logging
logger = logging.getLogger(__name__)

# Cria blueprint para a API simplificada
simple_location_bp = Blueprint('simple_location', __name__)

def calculate_simple_eta(current_lat: float, current_lon: float,
                        target_lat: float, target_lon: float,
                        occupancy_level: int = 2) -> Dict:
    """
    Calcula ETA simplificado considerando ocupação
    
    Args:
        current_lat: Latitude atual
        current_lon: Longitude atual
        target_lat: Latitude do destino
        target_lon: Longitude do destino
        occupancy_level: Nível de ocupação (0-4)
        
    Returns:
        Dicionário com ETA calculado
    """
    try:
        # Calcula distância
        distance = calculate_distance_km(current_lat, current_lon, target_lat, target_lon)
        
        # Velocidade base para ônibus urbano
        base_speed = ETA_CONFIG['default_speed_kmh']  # 20 km/h
        
        # Ajusta velocidade baseada na ocupação
        occupancy_speed_factors = {
            0: 1.0,   # Vazio - velocidade normal
            1: 0.95,  # Baixa - leve redução
            2: 0.90,  # Média - redução moderada
            3: 0.80,  # Alta - redução significativa
            4: 0.70   # Lotado - redução alta
        }
        
        occupancy_factor = occupancy_speed_factors.get(occupancy_level, 1.0)
        
        # Aplica fator de tráfego
        current_hour = datetime.now().hour
        traffic_factor = get_traffic_factor_by_hour(current_hour)
        
        # Aplica fatores de velocidade
        adjusted_speed = base_speed * traffic_factor * occupancy_factor
        
        # Calcula ETA
        eta_minutes = (distance / adjusted_speed) * 60
        estimated_arrival = datetime.now() + timedelta(minutes=eta_minutes)
        
        # Calcula confiança baseada em fatores
        base_confidence = 80.0
        confidence = base_confidence * occupancy_factor * traffic_factor
        confidence = max(50.0, min(95.0, confidence))  # Limita entre 50-95%
        
        return {
            'status': 'success',
            'eta_minutes': round(eta_minutes, 1),
            'estimated_arrival': estimated_arrival.isoformat(),
            'distance_km': round(distance, 2),
            'base_speed_kmh': base_speed,
            'adjusted_speed_kmh': round(adjusted_speed, 1),
            'confidence_percent': round(confidence, 1),
            'occupancy_impact': {
                'level': occupancy_level,
                'speed_factor': occupancy_factor,
                'speed_reduction_percent': round((1 - occupancy_factor) * 100, 1)
            },
            'traffic_factor': round(traffic_factor, 2),
            'source': 'simple_calculation'
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular ETA simplificado: {e}")
        return {
            'status': 'error',
            'eta_minutes': 999,
            'estimated_arrival': None,
            'distance_km': 0,
            'confidence_percent': 0,
            'error': str(e)
        }

@simple_location_bp.route('/location', methods=['POST'])
def receive_location():
    """
    Endpoint simplificado para receber dados de localização do ESP32
    """
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
        
        # Conecta ao banco (se disponível)
        db_manager = get_simple_database_manager()
        bus_repo = get_simple_bus_repository()
        eta_repo = get_simple_eta_repository()
        interval_repo = get_simple_interval_repository()
        
        location_id = None
        if all([db_manager, bus_repo]):
            # Salva localização no banco
            location_id = bus_repo.save_location(bus_line, latitude, longitude)
            if location_id:
                logger.info(f"Localização salva: ID {location_id}, Linha {bus_line}")
        
        # Encontra destino mais próximo
        nearest_dest = get_nearest_destination(latitude, longitude, DESTINATIONS)
        if not nearest_dest:
            return jsonify({'error': 'Nenhum destino encontrado'}), 500
        
        # Calcula ETA simplificado
        eta_data = calculate_simple_eta(
            latitude, longitude,
            nearest_dest['latitude'], nearest_dest['longitude']
        )
        
        # Salva previsão de ETA (se banco disponível)
        if location_id and eta_repo:
            try:
                predicted_arrival = datetime.fromisoformat(eta_data['estimated_arrival'])
                eta_repo.save_eta_prediction(
                    location_id, predicted_arrival, eta_data['confidence_percent']
                )
            except Exception as e:
                logger.warning(f"Erro ao salvar ETA: {e}")
        
        # Calcula intervalo adaptativo
        current_hour = datetime.now().hour
        traffic_factor = get_traffic_factor_by_hour(current_hour)
        adaptive_interval = calculate_adaptive_interval(
            INTERVAL_CONFIG['default_interval_seconds'],
            traffic_factor,
            INTERVAL_CONFIG['min_interval_seconds'],
            INTERVAL_CONFIG['max_interval_seconds']
        )
        
        # Salva intervalo adaptativo (se banco disponível)
        if location_id and interval_repo:
            try:
                interval_repo.save_interval(location_id, adaptive_interval)
            except Exception as e:
                logger.warning(f"Erro ao salvar intervalo: {e}")
        
        # Resposta para o ESP32
        response = {
            'status': 'success',
            'location_id': location_id or f"simple_{int(timestamp.timestamp())}",
            'timestamp': timestamp.isoformat(),
            'bus_line': bus_line,
            'destination': nearest_dest,
            'eta': eta_data,
            'adaptive_interval_seconds': adaptive_interval,
            'message': 'Localização recebida e ETA calculado (modo simplificado)',
            'database_connected': location_id is not None
        }
        
        # Log da requisição
        log_api_request('/api/location', 'POST', {
            'bus_line': bus_line,
            'eta_minutes': eta_data['eta_minutes'],
            'confidence': eta_data['confidence_percent']
        }, 200)
        
        logger.info(f"Localização processada: Linha {bus_line}, ETA {eta_data['eta_minutes']} min")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erro no endpoint /api/location: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@simple_location_bp.route('/location/history/<bus_line>', methods=['GET'])
def get_location_history(bus_line: str):
    """
    Endpoint para consultar histórico de localizações de uma linha
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        db_manager = get_simple_database_manager()
        bus_repo = get_simple_bus_repository()
        
        if not all([db_manager, bus_repo]):
            # Modo fallback - dados simulados
            simulated_locations = []
            base_time = datetime.now()
            
            for i in range(min(limit, 10)):
                timestamp = base_time - timedelta(minutes=i*5)
                simulated_locations.append({
                    'id': f"sim_{i}",
                    'bus_line': bus_line,
                    'latitude': -8.0630 + (i * 0.001),
                    'longitude': -34.8710 + (i * 0.001),
                    'timestamp_location': timestamp.isoformat()
                })
            
            return jsonify({
                'bus_line': bus_line,
                'count': len(simulated_locations),
                'locations': simulated_locations,
                'message': 'Dados simulados (modo fallback)',
                'mode': 'fallback'
            }), 200
        
        # Dados reais do banco
        locations = bus_repo.get_location_history(bus_line, hours, limit)
        
        return jsonify({
            'bus_line': bus_line,
            'count': len(locations),
            'locations': locations,
            'mode': 'database'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@simple_location_bp.route('/location/destinations', methods=['GET'])
def get_destinations():
    """
    Endpoint para listar destinos disponíveis
    """
    return jsonify({
        'destinations': DESTINATIONS,
        'count': len(DESTINATIONS)
    }), 200

@simple_location_bp.route('/location/current', methods=['GET'])
def get_current_locations():
    """
    Endpoint para obter localizações atuais
    """
    try:
        bus_line = request.args.get('line')
        minutes = int(request.args.get('minutes', 5))
        
        db_manager = get_simple_database_manager()
        bus_repo = get_simple_bus_repository()
        
        if not all([db_manager, bus_repo]):
            # Modo fallback - dados simulados
            simulated_locations = []
            bus_lines = ['L1', 'L2', 'L3', 'L4', 'BRT-1']
            
            for i, line in enumerate(bus_lines):
                if bus_line and line != bus_line:
                    continue
                    
                simulated_locations.append({
                    'id': f"current_{i}",
                    'bus_line': line,
                    'latitude': -8.0630 + (i * 0.001),
                    'longitude': -34.8710 + (i * 0.001),
                    'timestamp_location': datetime.now().isoformat()
                })
            
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'count': len(simulated_locations),
                'locations': simulated_locations,
                'mode': 'fallback'
            }), 200
        
        # Dados reais do banco
        locations = bus_repo.get_current_locations(bus_line, minutes)
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'count': len(locations),
            'locations': locations,
            'mode': 'database'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar localizações atuais: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@simple_location_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    """
    db_manager = get_simple_database_manager()
    db_connected = db_manager and db_manager.test_connection()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database_connected': db_connected,
        'mode': 'simple',
        'features': [
            'Localização GPS',
            'Cálculo de ETA',
            'Intervalos adaptativos',
            'Histórico de localizações'
        ]
    }), 200

# Exporta o blueprint para uso no main.py
app = simple_location_bp
