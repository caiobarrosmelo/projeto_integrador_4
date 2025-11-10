"""
API Integrada Simplificada - Schema Reduzido
Combina localização GPS com análise de imagens usando create_tables.sql
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
from ml.occupancy_predictor import predict_bus_occupancy
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

# Cria blueprint para a API integrada simplificada
simple_integrated_bp = Blueprint('simple_integrated', __name__)

def calculate_eta_with_occupancy_impact(current_lat: float, current_lon: float,
                                      target_lat: float, target_lon: float,
                                      occupancy_level: int, traffic_factor: float) -> Dict:
    """
    Calcula ETA considerando impacto da ocupação (versão simplificada)
    
    Args:
        current_lat: Latitude atual
        current_lon: Longitude atual
        target_lat: Latitude do destino
        target_lon: Longitude do destino
        occupancy_level: Nível de ocupação (0-4)
        traffic_factor: Fator de tráfego
        
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
        
        # Aplica fatores de velocidade
        adjusted_speed = base_speed * traffic_factor * occupancy_factor
        
        # Calcula ETA
        eta_minutes = (distance / adjusted_speed) * 60
        estimated_arrival = datetime.now() + timedelta(minutes=eta_minutes)
        
        # Calcula confiança considerando ocupação
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
            'source': 'simple_integrated_calculation'
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular ETA com ocupação: {e}")
        return {
            'status': 'error',
            'eta_minutes': 999,
            'estimated_arrival': None,
            'distance_km': 0,
            'confidence_percent': 0,
            'error': str(e)
        }

@simple_integrated_bp.route('/location-image', methods=['POST'])
def receive_location_and_image():
    """
    Endpoint integrado simplificado para receber localização GPS e imagem do ESP32
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400
        
        data = request.get_json()
        
        # Valida campos obrigatórios
        required_fields = ['bus_line', 'latitude', 'longitude', 'image_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400
        
        # Extrai dados
        bus_line = data['bus_line'].strip().upper()
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        image_base64 = data['image_data']
        
        # Campos opcionais
        location_id = data.get('location_id')
        timestamp_str = data.get('timestamp')
        
        # Valida timestamp se fornecido
        if timestamp_str:
            try:
                timestamp = parse_timestamp(timestamp_str)
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Validações
        if not validate_gps_coordinates(latitude, longitude):
            return jsonify({'error': 'Coordenadas GPS inválidas'}), 400
        
        if not validate_bus_line(bus_line):
            return jsonify({'error': 'Linha de ônibus inválida'}), 400
        
        logger.info(f"Processando localização e imagem para linha {bus_line}")
        
        # 1. Analisa ocupação da imagem
        occupancy_analysis = predict_bus_occupancy(image_base64)
        
        if occupancy_analysis['status'] != 'success':
            return jsonify({
                'error': 'Erro na análise de ocupação',
                'details': occupancy_analysis.get('error', 'Erro desconhecido')
            }), 500
        
        occupancy_info = occupancy_analysis['occupancy']
        occupancy_level = occupancy_info['level']
        
        # 2. Encontra destino mais próximo
        nearest_dest = get_nearest_destination(latitude, longitude, DESTINATIONS)
        if not nearest_dest:
            return jsonify({'error': 'Nenhum destino encontrado'}), 500
        
        # 3. Calcula fator de tráfego
        current_hour = datetime.now().hour
        traffic_factor = get_traffic_factor_by_hour(current_hour)
        
        # 4. Calcula ETA considerando ocupação
        eta_data = calculate_eta_with_occupancy_impact(
            latitude, longitude,
            nearest_dest['latitude'], nearest_dest['longitude'],
            occupancy_level, traffic_factor
        )
        
        # 5. Conecta ao banco (se disponível)
        db_manager = get_simple_database_manager()
        bus_repo = get_simple_bus_repository()
        occupancy_repo = get_simple_occupancy_repository()
        eta_repo = get_simple_eta_repository()
        interval_repo = get_simple_interval_repository()
        
        saved_location_id = location_id
        if all([db_manager, bus_repo]) and not location_id:
            # Salva localização no banco
            saved_location_id = bus_repo.save_location(bus_line, latitude, longitude)
            if saved_location_id:
                logger.info(f"Localização salva: ID {saved_location_id}")
        
        # 6. Salva análise de imagem (se banco disponível)
        if saved_location_id and occupancy_repo:
            try:
                import base64
                if ',' in image_base64:
                    image_base64_clean = image_base64.split(',')[1]
                else:
                    image_base64_clean = image_base64
                image_data = base64.b64decode(image_base64_clean)
                
                occupancy_repo.save_image_analysis(
                    saved_location_id, image_data, occupancy_info['person_count']
                )
            except Exception as e:
                logger.warning(f"Erro ao salvar análise de imagem: {e}")
        
        # 7. Salva previsão de ETA (se banco disponível)
        if saved_location_id and eta_repo:
            try:
                predicted_arrival = datetime.fromisoformat(eta_data['estimated_arrival'])
                eta_repo.save_eta_prediction(
                    saved_location_id, predicted_arrival, eta_data['confidence_percent']
                )
            except Exception as e:
                logger.warning(f"Erro ao salvar ETA: {e}")
        
        # 8. Calcula intervalo adaptativo baseado na ocupação
        occupancy_interval_factors = {
            0: 1.2,  # Vazio - intervalo maior
            1: 1.1,  # Baixa - intervalo ligeiramente maior
            2: 1.0,  # Média - intervalo normal
            3: 0.8,  # Alta - intervalo menor
            4: 0.6   # Lotado - intervalo muito menor
        }
        
        occupancy_interval_factor = occupancy_interval_factors.get(occupancy_level, 1.0)
        base_interval = INTERVAL_CONFIG['default_interval_seconds']
        adaptive_interval = int(base_interval * occupancy_interval_factor)
        
        # Garante limites
        adaptive_interval = max(
            INTERVAL_CONFIG['min_interval_seconds'],
            min(adaptive_interval, INTERVAL_CONFIG['max_interval_seconds'])
        )
        
        # 9. Salva intervalo adaptativo (se banco disponível)
        if saved_location_id and interval_repo:
            try:
                interval_repo.save_interval(saved_location_id, adaptive_interval)
            except Exception as e:
                logger.warning(f"Erro ao salvar intervalo: {e}")
        
        # 10. Gera recomendações integradas
        recommendations = generate_simple_recommendations(
            occupancy_info, eta_data, traffic_factor, adaptive_interval
        )
        
        # 11. Resposta integrada para o ESP32
        response = {
            'status': 'success',
            'location_id': saved_location_id or f"simple_{int(timestamp.timestamp())}",
            'timestamp': timestamp.isoformat(),
            'bus_line': bus_line,
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'destination': nearest_dest
            },
            'occupancy': occupancy_info,
            'eta': eta_data,
            'adaptive_interval_seconds': adaptive_interval,
            'traffic': {
                'factor': traffic_factor,
                'level': 'high' if traffic_factor < 0.7 else 'medium' if traffic_factor < 0.9 else 'low'
            },
            'recommendations': recommendations,
            'annotated_image': occupancy_analysis['annotated_image'],
            'message': 'Análise integrada concluída (modo simplificado)',
            'database_connected': saved_location_id is not None
        }
        
        # Log da requisição
        log_api_request('/api/location-image', 'POST', {
            'bus_line': bus_line,
            'occupancy_level': occupancy_level,
            'eta_minutes': eta_data['eta_minutes'],
            'confidence': eta_data['confidence_percent']
        }, 200)
        
        logger.info(f"Análise integrada concluída: {occupancy_level} pessoas, ETA {eta_data['eta_minutes']}min")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erro no endpoint /api/location-image: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

def generate_simple_recommendations(occupancy_info: Dict, eta_data: Dict, 
                                  traffic_factor: float, interval: int) -> List[str]:
    """
    Gera recomendações integradas simplificadas
    
    Args:
        occupancy_info: Informações de ocupação
        eta_data: Dados de ETA
        traffic_factor: Fator de tráfego
        interval: Intervalo adaptativo
        
    Returns:
        Lista de recomendações
    """
    recommendations = []
    
    # Recomendações baseadas na ocupação
    occupancy_level = occupancy_info['level']
    if occupancy_level >= 3:
        recommendations.append("🚌 Ocupação alta - considere aumentar frequência de ônibus")
        recommendations.append("⏰ Intervalo reduzido para monitoramento mais frequente")
    
    # Recomendações baseadas no ETA
    eta_minutes = eta_data['eta_minutes']
    confidence = eta_data['confidence_percent']
    
    if confidence < 70:
        recommendations.append("⚠️ Baixa confiança na previsão - condições de tráfego instáveis")
    
    if eta_minutes > 30:
        recommendations.append("🕐 ETA alto - verifique se há problemas na rota")
    
    # Recomendações baseadas no tráfego
    if traffic_factor < 0.7:
        recommendations.append("🚦 Tráfego intenso - ETA pode variar significativamente")
    
    # Recomendações específicas por nível de ocupação
    if occupancy_level == 4:  # Lotado
        recommendations.extend([
            "🚨 Ônibus lotado - urgente aumentar frequência",
            "👥 Passageiros em pé - monitore segurança"
        ])
    elif occupancy_level == 0:  # Vazio
        recommendations.extend([
            "💡 Ônibus vazio - boa oportunidade para embarque",
            "📊 Considere reduzir frequência se padrão persistir"
        ])
    
    return recommendations

@simple_integrated_bp.route('/integrated/status/<bus_line>', methods=['GET'])
def get_integrated_status(bus_line: str):
    """
    Endpoint para status integrado de uma linha de ônibus
    """
    try:
        db_manager = get_simple_database_manager()
        bus_repo = get_simple_bus_repository()
        
        if not all([db_manager, bus_repo]):
            # Dados simulados para demonstração
            current_time = datetime.now()
            
            # Simula dados baseados no horário
            hour = current_time.hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Horários de pico
                occupancy_level = 3
                traffic_factor = 0.6
            else:
                occupancy_level = 2
                traffic_factor = 0.8
            
            status = {
                'bus_line': bus_line,
                'timestamp': current_time.isoformat(),
                'current_status': {
                    'occupancy_level': occupancy_level,
                    'occupancy_name': ML_CONFIG['occupancy_levels'][occupancy_level],
                    'traffic_factor': traffic_factor,
                    'avg_eta_minutes': 15 + (occupancy_level * 5),
                    'confidence_percent': 85 - (occupancy_level * 5)
                },
                'recommendations': [
                    f"Monitoramento ativo - nível de ocupação {ML_CONFIG['occupancy_levels'][occupancy_level]}",
                    f"ETA médio: {15 + (occupancy_level * 5)} minutos",
                    "Sistema funcionando normalmente"
                ],
                'next_update_seconds': 30,
                'mode': 'simple_fallback'
            }
        else:
            # Dados reais do banco
            locations = bus_repo.get_current_locations(bus_line, minutes=5)
            
            if locations:
                latest_location = locations[0]
                status = {
                    'bus_line': bus_line,
                    'timestamp': latest_location['timestamp_location'].isoformat(),
                    'current_status': {
                        'last_location': {
                            'latitude': latest_location['latitude'],
                            'longitude': latest_location['longitude']
                        },
                        'last_update': latest_location['timestamp_location'].isoformat()
                    },
                    'recommendations': [
                        "Dados em tempo real do banco",
                        "Sistema funcionando com persistência"
                    ],
                    'mode': 'simple_database'
                }
            else:
                status = {
                    'bus_line': bus_line,
                    'timestamp': datetime.now().isoformat(),
                    'current_status': {
                        'message': 'Nenhuma localização recente encontrada'
                    },
                    'recommendations': [
                        "Aguardando dados do ESP32",
                        "Verifique se o dispositivo está conectado"
                    ],
                    'mode': 'simple_database'
                }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar status integrado: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@simple_integrated_bp.route('/health', methods=['GET'])
def integrated_health_check():
    """
    Endpoint de health check para API integrada
    """
    db_manager = get_simple_database_manager()
    db_connected = db_manager and db_manager.test_connection()
    
    return jsonify({
        'status': 'healthy',
        'service': 'simple-integrated-location-image-api',
        'timestamp': datetime.now().isoformat(),
        'database_connected': db_connected,
        'features': [
            'Análise de ocupação com YOLO',
            'Cálculo de ETA com impacto de ocupação',
            'Intervalos adaptativos inteligentes',
            'Recomendações integradas',
            'Monitoramento em tempo real'
        ],
        'ml_models': {
            'occupancy_detection': 'YOLO (fallback mode)',
            'eta_calculation': 'Simplified algorithm',
            'traffic_analysis': 'Time-based patterns'
        }
    }), 200

# Exporta o blueprint para uso no main.py
app = simple_integrated_bp
