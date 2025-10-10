"""
Utilitários compartilhados para as APIs
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import json
import logging
import math
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

def validate_gps_coordinates(latitude: float, longitude: float) -> bool:
    """
    Valida se as coordenadas GPS são válidas
    """
    return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)

def validate_bus_line(bus_line: str) -> bool:
    """
    Valida formato da linha de ônibus
    """
    if not bus_line or len(bus_line.strip()) == 0:
        return False
    
    # Remove espaços e converte para maiúsculo
    bus_line = bus_line.strip().upper()
    
    # Verifica se tem formato válido (ex: L1, 101, BRT-1)
    if len(bus_line) < 1 or len(bus_line) > 10:
        return False
    
    return True

def parse_timestamp(timestamp_str: Optional[str]) -> datetime:
    """
    Converte string de timestamp para datetime
    Suporta vários formatos
    """
    if not timestamp_str:
        return datetime.now()
    
    try:
        # Remove 'Z' se presente e adiciona timezone
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        try:
            # Tenta formato Unix timestamp
            timestamp = int(timestamp_str)
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            logger.warning(f"Timestamp inválido: {timestamp_str}, usando timestamp atual")
            return datetime.now()

def create_db_connection(config: Dict[str, Any]):
    """
    Cria conexão com banco PostgreSQL
    """
    try:
        connection = psycopg2.connect(**config)
        return connection
    except Exception as e:
        logger.error(f"Erro ao conectar com banco: {e}")
        return None

def execute_query(connection, query: str, params: tuple = None, fetch: bool = False):
    """
    Executa query no banco de dados
    """
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            connection.commit()
            cursor.close()
            return True
            
    except Exception as e:
        logger.error(f"Erro ao executar query: {e}")
        connection.rollback()
        return None

def format_response(status: str, data: Dict = None, message: str = None, error: str = None) -> Dict:
    """
    Formata resposta padronizada da API
    """
    response = {
        'status': status,
        'timestamp': datetime.now().isoformat()
    }
    
    if data:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    return response

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distância entre dois pontos GPS em quilômetros
    Usa fórmula de Haversine
    """
    # Raio da Terra em km
    R = 6371
    
    # Converte graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Diferenças
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def get_traffic_factor_by_hour(hour: int) -> float:
    """
    Retorna fator de tráfego baseado no horário
    """
    if 7 <= hour <= 9:      # Pico manhã
        return 0.6
    elif 12 <= hour <= 14:  # Almoço
        return 0.8
    elif 17 <= hour <= 19:  # Pico tarde
        return 0.5
    elif 19 <= hour <= 23:  # Noite
        return 1.1
    else:                   # Madrugada
        return 1.0

def validate_json_payload(required_fields: list, data: Dict) -> Tuple[bool, str]:
    """
    Valida se payload JSON tem campos obrigatórios
    Retorna (is_valid, error_message)
    """
    for field in required_fields:
        if field not in data:
            return False, f"Campo obrigatório ausente: {field}"
        
        if data[field] is None or (isinstance(data[field], str) and len(data[field].strip()) == 0):
            return False, f"Campo obrigatório vazio: {field}"
    
    return True, ""

def sanitize_bus_line(bus_line: str) -> str:
    """
    Sanitiza linha de ônibus (remove espaços, converte para maiúsculo)
    """
    return bus_line.strip().upper()

def log_api_request(endpoint: str, method: str, data: Dict = None, response_status: int = None):
    """
    Log padronizado para requisições da API
    """
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'timestamp': datetime.now().isoformat()
    }
    
    if data:
        log_data['request_data'] = data
    
    if response_status:
        log_data['response_status'] = response_status
    
    logger.info(f"API Request: {json.dumps(log_data)}")

def calculate_adaptive_interval(current_interval: int, traffic_factor: float, 
                               min_interval: int = 10, max_interval: int = 300) -> int:
    """
    Calcula intervalo adaptativo baseado no fator de tráfego
    """
    new_interval = int(current_interval * traffic_factor)
    
    # Garante que está dentro dos limites
    new_interval = max(min_interval, min(new_interval, max_interval))
    
    return new_interval

def determine_occupancy_level(passenger_count: int, max_capacity: int = 50) -> int:
    """
    Determina nível de ocupação (0-4) baseado na contagem de passageiros
    """
    if passenger_count == 0:
        return 0  # Vazio
    elif passenger_count <= max_capacity * 0.25:
        return 1  # Baixa
    elif passenger_count <= max_capacity * 0.5:
        return 2  # Média
    elif passenger_count <= max_capacity * 0.75:
        return 3  # Alta
    else:
        return 4  # Lotado

def validate_image_data(image_base64: str, max_size_mb: int = 5) -> Tuple[bool, str]:
    """
    Valida dados de imagem em Base64
    """
    if not image_base64:
        return False, "Dados de imagem não fornecidos"
    
    # Calcula tamanho aproximado em MB
    size_bytes = len(image_base64) * 3 / 4  # Base64 é ~33% maior que binário
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > max_size_mb:
        return False, f"Imagem muito grande: {size_mb:.1f}MB (máximo: {max_size_mb}MB)"
    
    return True, ""

def get_nearest_destination(latitude: float, longitude: float, destinations: Dict) -> Dict:
    """
    Encontra o destino mais próximo baseado nas coordenadas GPS
    """
    min_distance = float('inf')
    nearest_dest = None
    
    for dest_id, dest_info in destinations.items():
        distance = calculate_distance_km(
            latitude, longitude,
            dest_info['latitude'], dest_info['longitude']
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest_dest = {
                'id': dest_id,
                'name': dest_info['name'],
                'latitude': dest_info['latitude'],
                'longitude': dest_info['longitude'],
                'type': dest_info['type'],
                'distance_km': round(distance, 2)
            }
    
    return nearest_dest