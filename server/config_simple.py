"""
Configurações Simplificadas do Sistema de Monitoramento IoT
Schema Reduzido - Baseado nos requisitos do projeto integrador
"""

import os
from typing import Dict, Any

# Configurações do banco de dados PostgreSQL
# Observação:
# - Os valores padrão abaixo são pensados para um ambiente local simples.
# - Em produção (ou em ambientes de avaliação) SEMPRE configure as variáveis
#   de ambiente: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD e DB_PORT.
DATABASE_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'bus_monitoring'),
    # Por padrão usamos o usuário postgres em desenvolvimento local.
    # Se você criou outro usuário (ex: bus_user), ajuste via variável de ambiente.
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'MinhaSenhaReal123'),
    # Porta padrão do PostgreSQL (local). Pode ser sobrescrita via DB_PORT.
    'port': int(os.getenv('DB_PORT', '5432')),
}

# Configurações da API
# Padrão: Flask em http://0.0.0.0:3000
# O frontend Next.js, em desenvolvimento, roda em http://localhost:3001.
# Se você alterar a porta aqui, lembre-se de atualizar também NEXT_PUBLIC_API_URL
# no frontend (client/.env.local).
API_CONFIG: Dict[str, Any] = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', '3000')),
    'debug': os.getenv('API_DEBUG', 'True').lower() == 'true',
}

# Configurações de ETA simplificado
ETA_CONFIG: Dict[str, Any] = {
    'default_speed_kmh': 20.0,      # Velocidade padrão para ônibus urbano
    'confidence_osrm': 90.0,        # Confiança do OSRM (alta)
    'confidence_fallback': 60.0,    # Confiança do fallback manual (média)
    'confidence_simple': 80.0       # Confiança do cálculo simplificado
}

# Coordenadas de destinos/paradas importantes (Recife)
DESTINATIONS: Dict[str, Dict[str, Any]] = {
    'terminal_central': {
        'name': 'Terminal Central',
        'latitude': -8.0630,
        'longitude': -34.8710,
        'type': 'terminal'
    },
    'aeroporto': {
        'name': 'Aeroporto Internacional do Recife',
        'latitude': -8.1264,
        'longitude': -34.9176,
        'type': 'terminal'
    },
    'shopping_recife': {
        'name': 'Shopping Recife',
        'latitude': -8.0476,
        'longitude': -34.8770,
        'type': 'parada'
    },
    'boa_viagem': {
        'name': 'Praia de Boa Viagem',
        'latitude': -8.1196,
        'longitude': -34.9010,
        'type': 'parada'
    }
}

# Configurações de intervalos adaptativos
INTERVAL_CONFIG: Dict[str, Any] = {
    'default_interval_seconds': 30,     # Intervalo padrão
    'min_interval_seconds': 10,         # Intervalo mínimo
    'max_interval_seconds': 120,        # Intervalo máximo
    'traffic_factor_weight': 0.3,       # Peso do fator de tráfego
    'occupancy_factor_weight': 0.2      # Peso do fator de ocupação
}

# Configurações de Machine Learning (YOLO)
ML_CONFIG: Dict[str, Any] = {
    'yolo_model_path': 'ml/yolov5',     # Caminho do modelo YOLO
    'confidence_threshold': 0.5,        # Limiar de confiança para detecções
    'max_occupancy_count': 50,          # Capacidade máxima do ônibus
    'occupancy_levels': {               # Níveis de ocupação
        0: 'Vazio',
        1: 'Baixa',
        2: 'Média',
        3: 'Alta',
        4: 'Lotado'
    }
}

# Configurações de validação
VALIDATION_CONFIG: Dict[str, Any] = {
    'max_image_size_mb': 5.0,           # Tamanho máximo da imagem em MB
    'min_latitude': -8.2,               # Limite mínimo de latitude (Recife)
    'max_latitude': -7.9,               # Limite máximo de latitude
    'min_longitude': -35.0,             # Limite mínimo de longitude
    'max_longitude': -34.8,             # Limite máximo de longitude
    'bus_line_pattern': r'^[A-Z0-9\-]+$'  # Padrão para linha de ônibus
}

# Configurações de logging
LOGGING_CONFIG: Dict[str, Any] = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Configurações de CORS
# Em produção, adicione FRONTEND_URL como variável de ambiente
# Exemplo: FRONTEND_URL=https://seu-frontend.onrender.com
frontend_url = os.getenv('FRONTEND_URL', '')
cors_origins = [
    'http://localhost:3000', 
    'http://localhost:3001', 
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001'
]
if frontend_url:
    cors_origins.append(frontend_url)
    # Também adiciona variante sem protocolo se necessário
    if not frontend_url.startswith('http'):
        cors_origins.append(f'https://{frontend_url}')
        cors_origins.append(f'http://{frontend_url}')

CORS_CONFIG: Dict[str, Any] = {
    'origins': cors_origins,
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization']
}

# Configurações de tráfego por horário (simplificado)
TRAFFIC_FACTORS: Dict[int, float] = {
    0: 1.0,   # 00:00 - 01:00 (madrugada)
    1: 1.0,   # 01:00 - 02:00
    2: 1.0,   # 02:00 - 03:00
    3: 1.0,   # 03:00 - 04:00
    4: 1.0,   # 04:00 - 05:00
    5: 1.0,   # 05:00 - 06:00
    6: 0.9,   # 06:00 - 07:00 (início do dia)
    7: 0.7,   # 07:00 - 08:00 (pico manhã)
    8: 0.6,   # 08:00 - 09:00 (pico manhã)
    9: 0.8,   # 09:00 - 10:00
    10: 0.9,  # 10:00 - 11:00
    11: 0.9,  # 11:00 - 12:00
    12: 0.8,  # 12:00 - 13:00 (almoço)
    13: 0.8,  # 13:00 - 14:00
    14: 0.9,  # 14:00 - 15:00
    15: 0.9,  # 15:00 - 16:00
    16: 0.8,  # 16:00 - 17:00
    17: 0.6,  # 17:00 - 18:00 (pico tarde)
    18: 0.7,  # 18:00 - 19:00 (pico tarde)
    19: 0.8,  # 19:00 - 20:00
    20: 0.9,  # 20:00 - 21:00
    21: 0.9,  # 21:00 - 22:00
    22: 1.0,  # 22:00 - 23:00
    23: 1.0   # 23:00 - 00:00
}

# Função para obter fator de tráfego por horário
def get_traffic_factor_by_hour(hour: int) -> float:
    """
    Retorna o fator de tráfego para um horário específico
    
    Args:
        hour: Hora do dia (0-23)
        
    Returns:
        Fator de tráfego (0.0 = parado, 1.0 = livre)
    """
    return TRAFFIC_FACTORS.get(hour, 1.0)

# Configurações de desenvolvimento
DEV_CONFIG: Dict[str, Any] = {
    'enable_fallback_mode': True,       # Habilita modo fallback
    'simulate_database': False,         # Simula banco quando não disponível
    'mock_ml_responses': False,         # Simula respostas de ML
    'verbose_logging': True             # Logs detalhados
}
