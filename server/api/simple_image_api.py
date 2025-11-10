"""
API Simplificada para Análise de Imagens - Schema Reduzido
Usa create_tables.sql (4 tabelas básicas)
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import request, jsonify, Blueprint
import os
import sys

# Adiciona o diretório server ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_simple import ML_CONFIG, VALIDATION_CONFIG
from ml.occupancy_predictor import predict_bus_occupancy
from database.simple_connection import (
    get_simple_database_manager, get_simple_occupancy_repository
)
from api.utils import validate_json_payload, log_api_request

# Configuração de logging
logger = logging.getLogger(__name__)

# Cria blueprint para a API simplificada de imagens
simple_image_bp = Blueprint('simple_image', __name__)

def validate_image_data(image_base64: str) -> tuple[bool, str]:
    """
    Valida dados de imagem em Base64
    
    Args:
        image_base64: String base64 da imagem
        
    Returns:
        (is_valid, error_message)
    """
    if not image_base64:
        return False, "Dados de imagem não fornecidos"
    
    # Verifica se tem prefixo data:image
    if not image_base64.startswith('data:image/'):
        return False, "Formato de imagem inválido - deve começar com 'data:image/'"
    
    # Calcula tamanho aproximado em MB
    size_bytes = len(image_base64) * 3 / 4  # Base64 é ~33% maior que binário
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > VALIDATION_CONFIG['max_image_size_mb']:
        return False, f"Imagem muito grande: {size_mb:.1f}MB (máximo: {VALIDATION_CONFIG['max_image_size_mb']}MB)"
    
    return True, ""

def save_simple_image_analysis(location_id: int, image_base64: str, 
                              analysis_result: Dict) -> Dict:
    """
    Salva resultado da análise de imagem (schema simplificado)
    
    Args:
        location_id: ID da localização associada
        image_base64: Imagem original em base64
        analysis_result: Resultado da análise
        
    Returns:
        Dicionário com informações do salvamento
    """
    try:
        db_manager = get_simple_database_manager()
        occupancy_repo = get_simple_occupancy_repository()
        
        if not all([db_manager, occupancy_repo]):
            # Modo fallback - simula salvamento
            timestamp = datetime.now()
            image_record = {
                'id': f"img_{int(timestamp.timestamp())}",
                'location_id': location_id,
                'timestamp': timestamp.isoformat(),
                'occupancy_count': analysis_result.get('occupancy', {}).get('person_count', 0),
                'status': 'analyzed_fallback'
            }
            
            logger.info(f"Análise de imagem salva (simulado): {image_record['id']}")
            
            return {
                'status': 'success',
                'image_id': image_record['id'],
                'saved_at': timestamp.isoformat(),
                'message': 'Análise salva com sucesso (modo fallback)'
            }
        
        # Salva no banco real
        import base64
        
        # Decodifica imagem para bytes
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        image_data = base64.b64decode(image_base64)
        
        # Salva imagem
        image_id = occupancy_repo.save_image_analysis(
            location_id, 
            image_data, 
            analysis_result.get('occupancy', {}).get('person_count', 0)
        )
        
        if image_id:
            return {
                'status': 'success',
                'image_id': image_id,
                'saved_at': datetime.now().isoformat(),
                'message': 'Análise salva com sucesso no banco'
            }
        else:
            return {
                'status': 'error',
                'error': 'Falha ao salvar no banco'
            }
        
    except Exception as e:
        logger.error(f"Erro ao salvar análise de imagem: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

@simple_image_bp.route('/image/analyze', methods=['POST'])
def analyze_bus_image():
    """
    Endpoint simplificado para análise de imagem de ocupação do ônibus
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400
        
        data = request.get_json()
        
        # Valida campos obrigatórios
        required_fields = ['bus_line', 'image_data']
        is_valid, error_msg = validate_json_payload(required_fields, data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Extrai dados
        bus_line = data['bus_line'].strip().upper()
        image_base64 = data['image_data']
        
        # Campos opcionais
        location_id = data.get('location_id')
        timestamp_str = data.get('timestamp')
        
        # Valida timestamp se fornecido
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Valida dados da imagem
        is_valid, error_msg = validate_image_data(image_base64)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        logger.info(f"Iniciando análise de imagem para linha {bus_line}")
        
        # Executa análise de ocupação com YOLO
        analysis_result = predict_bus_occupancy(image_base64)
        
        if analysis_result['status'] != 'success':
            return jsonify({
                'error': 'Erro na análise de imagem',
                'details': analysis_result.get('error', 'Erro desconhecido')
            }), 500
        
        # Salva resultado da análise
        save_result = save_simple_image_analysis(location_id, image_base64, analysis_result)
        
        # Resposta para o ESP32
        response = {
            'status': 'success',
            'bus_line': bus_line,
            'timestamp': timestamp.isoformat(),
            'image_id': save_result.get('image_id'),
            'occupancy': analysis_result['occupancy'],
            'detections': {
                'count': len(analysis_result['detections']),
                'confidence_avg': analysis_result['image_analysis']['confidence_avg']
            },
            'recommendations': analysis_result['recommendations'],
            'annotated_image': analysis_result['annotated_image'],
            'message': 'Análise de ocupação concluída (modo simplificado)',
            'database_connected': save_result.get('status') == 'success'
        }
        
        # Log da requisição
        log_api_request('/api/image/analyze', 'POST', {
            'bus_line': bus_line,
            'image_size': len(image_base64),
            'occupancy_level': analysis_result['occupancy']['level']
        }, 200)
        
        logger.info(f"Análise concluída: {analysis_result['occupancy']['person_count']} pessoas, nível {analysis_result['occupancy']['level']}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erro no endpoint /api/image/analyze: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@simple_image_bp.route('/image/occupancy/<bus_line>', methods=['GET'])
def get_occupancy_history(bus_line: str):
    """
    Endpoint para consultar histórico de ocupação de uma linha
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        db_manager = get_simple_database_manager()
        occupancy_repo = get_simple_occupancy_repository()
        
        if not all([db_manager, occupancy_repo]):
            # Modo fallback - dados simulados
            simulated_data = []
            base_time = datetime.now()
            
            for i in range(min(limit, 10)):
                timestamp = base_time - timedelta(minutes=i*30)
                
                # Simula diferentes níveis de ocupação
                occupancy_levels = [0, 1, 2, 3, 4]
                level = occupancy_levels[i % len(occupancy_levels)]
                
                simulated_data.append({
                    'id': f"img_{int(timestamp.timestamp())}",
                    'bus_line': bus_line,
                    'timestamp': timestamp.isoformat(),
                    'occupancy_count': level * 10 + (i % 5),
                    'occupancy_level': level,
                    'occupancy_name': ML_CONFIG['occupancy_levels'][level]
                })
            
            return jsonify({
                'bus_line': bus_line,
                'count': len(simulated_data),
                'occupancy_history': simulated_data,
                'summary': {
                    'avg_occupancy_level': sum(d['occupancy_level'] for d in simulated_data) / len(simulated_data),
                    'max_occupancy_level': max(d['occupancy_level'] for d in simulated_data),
                    'total_analyzes': len(simulated_data)
                },
                'message': 'Histórico de ocupação (dados simulados)',
                'mode': 'fallback'
            }), 200
        
        # Dados reais do banco
        stats = occupancy_repo.get_occupancy_statistics(bus_line, hours)
        
        # Converte para formato esperado pelo front-end
        occupancy_history = []
        if 'by_occupancy' in stats:
            for level, data in stats['by_occupancy'].items():
                occupancy_history.append({
                    'occupancy_level': level,
                    'occupancy_name': ML_CONFIG['occupancy_levels'].get(level, f'Nível {level}'),
                    'count': data['count'],
                    'avg_occupancy_count': data['avg_occupancy']
                })
        
        response = {
            'bus_line': bus_line,
            'count': stats['total_analyses'],
            'occupancy_history': occupancy_history,
            'summary': {
                'total_analyses': stats['total_analyses'],
                'avg_occupancy_level': 2.0,  # Calculado se necessário
                'max_occupancy_level': 4
            },
            'mode': 'database'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de ocupação: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@simple_image_bp.route('/image/statistics', methods=['GET'])
def get_occupancy_statistics():
    """
    Endpoint para estatísticas gerais de ocupação
    """
    try:
        db_manager = get_simple_database_manager()
        occupancy_repo = get_simple_occupancy_repository()
        
        if not all([db_manager, occupancy_repo]):
            # Estatísticas simuladas
            stats = {
                'total_analyzes': 150,
                'bus_lines_active': 5,
                'avg_occupancy_level': 2.3,
                'occupancy_distribution': {
                    'vazio': 15,
                    'baixa': 35,
                    'média': 45,
                    'alta': 30,
                    'lotado': 25
                },
                'last_updated': datetime.now().isoformat(),
                'mode': 'fallback'
            }
        else:
            # Estatísticas reais do banco
            stats = occupancy_repo.get_occupancy_statistics(hours=24)
            
            # Converte para formato esperado
            stats.update({
                'bus_lines_active': len(stats.get('by_line', {})),
                'avg_occupancy_level': 2.0,  # Calculado se necessário
                'last_updated': datetime.now().isoformat(),
                'mode': 'database'
            })
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@simple_image_bp.route('/health', methods=['GET'])
def image_health_check():
    """
    Endpoint de health check para API de imagens
    """
    db_manager = get_simple_database_manager()
    db_connected = db_manager and db_manager.test_connection()
    
    return jsonify({
        'status': 'healthy',
        'service': 'simple-image-analysis-api',
        'timestamp': datetime.now().isoformat(),
        'database_connected': db_connected,
        'ml_model': 'YOLO (fallback mode)',
        'features': [
            'Detecção de pessoas',
            'Análise de ocupação',
            'Geração de recomendações',
            'Histórico de ocupação'
        ]
    }), 200

# Exporta o blueprint para uso no main.py
app = simple_image_bp
