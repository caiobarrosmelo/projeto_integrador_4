"""
Configurações do servidor de monitoramento de ônibus IoT
Baseado nos requisitos do projeto integrador
"""

import os
from typing import Dict, Any

# Configurações do banco de dados PostgreSQL
DATABASE_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'bus_monitoring'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

# Configurações da API
API_CONFIG: Dict[str, Any] = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', '3000')),
    'debug': os.getenv('API_DEBUG', 'True').lower() == 'true'
}

# Configurações de ETA e algoritmo de previsão
ETA_CONFIG: Dict[str, Any] = {
    'default_speed_kmh': 20.0,      # Velocidade padrão para ônibus urbano
    'max_speed_kmh': 60.0,          # Velocidade máxima considerada
    'min_speed_kmh': 2.0,           # Velocidade mínima considerada
    'history_hours': 2,             # Horas de histórico para calcular velocidade
    'min_data_points': 3,           # Mínimo de pontos para calcular velocidade
    'max_data_points': 20,          # Máximo de pontos para calcular velocidade
    'confidence_threshold': 70.0,   # Limiar mínimo de confiança para previsões
    'update_interval_seconds': 30   # Intervalo padrão de atualização
}

# Configurações do OSRM
OSRM_CONFIG: Dict[str, Any] = {
    'server_url': 'http://router.project-osrm.org',  # Servidor OSRM público
    'profile': 'driving',           # Perfil de roteamento (driving, walking, cycling)
    'timeout_seconds': 10,          # Timeout para requisições
    'max_retries': 3,               # Máximo de tentativas em caso de falha
    'fallback_enabled': True,       # Habilita fallback para cálculo manual
    'confidence_osrm': 90.0,        # Confiança do OSRM (alta)
    'confidence_fallback': 60.0     # Confiança do fallback manual (média)
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
    'praia_boa_viagem': {
        'name': 'Praia de Boa Viagem',
        'latitude': -8.1196,
        'longitude': -34.9010,
        'type': 'parada'
    },
    'universidade_federal': {
        'name': 'Universidade Federal de Pernambuco',
        'latitude': -8.0476,
        'longitude': -34.9510,
        'type': 'parada'
    },
    'hospital_restauracao': {
        'name': 'Hospital da Restauração',
        'latitude': -8.0630,
        'longitude': -34.9010,
        'type': 'parada'
    }
}

# Fatores de tráfego por horário (baseado em padrões de Recife)
TRAFFIC_FACTORS: Dict[str, float] = {
    'rush_morning': 0.6,        # 7h-9h (pico manhã)
    'normal_morning': 0.8,      # 9h-12h
    'lunch': 0.7,               # 12h-14h (almoço)
    'normal_afternoon': 0.9,    # 14h-17h
    'rush_evening': 0.5,        # 17h-19h (pico tarde)
    'night': 1.1,               # 19h-23h (noite)
    'late_night': 1.2           # 23h-7h (madrugada)
}

# Configurações de intervalos adaptativos
INTERVAL_CONFIG: Dict[str, Any] = {
    'min_interval_seconds': 10,     # Intervalo mínimo entre requisições
    'max_interval_seconds': 300,    # Intervalo máximo (5 minutos)
    'default_interval_seconds': 30, # Intervalo padrão
    'high_traffic_factor': 0.8,     # Reduz intervalo em tráfego alto
    'low_traffic_factor': 1.2       # Aumenta intervalo em tráfego baixo
}

# Configurações de Machine Learning
ML_CONFIG: Dict[str, Any] = {
    'yolo_model_path': 'ml/yolov5',
    'confidence_threshold': 0.5,    # Limiar de confiança para detecção
    'occupancy_levels': {           # Níveis de ocupação (0-4)
        0: 'vazio',
        1: 'baixa',
        2: 'média',
        3: 'alta',
        4: 'lotado'
    },
    'max_occupancy_count': 50       # Máximo de pessoas consideradas
}

# Configurações de logging
LOGGING_CONFIG: Dict[str, str] = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.getenv('LOG_FILE', 'server.log')
}

# Configurações de CORS para frontend
CORS_CONFIG: Dict[str, Any] = {
    'origins': [
        'http://localhost:3000',    # Next.js dev server
        'http://localhost:3001',    # Next.js alt port
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001'
    ],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization']
}

# Configurações de validação
VALIDATION_CONFIG: Dict[str, Any] = {
    'max_bus_line_length': 10,
    'min_bus_line_length': 1,
    'gps_precision': 6,             # Casas decimais para GPS
    'max_image_size_mb': 5,         # Tamanho máximo de imagem
    'allowed_image_formats': ['jpeg', 'jpg', 'png']
}