"""
Servidor principal para APIs de monitoramento de ônibus IoT
Baseado nos requisitos do projeto integrador
"""

import os
import sys
import logging
from flask import Flask
from flask_cors import CORS

# Adiciona o diretório server ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_simple import API_CONFIG, LOGGING_CONFIG, CORS_CONFIG

# Configuração de logging primeiro
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

# Importa APIs simplificadas (schema reduzido)
from api.simple_location_api import simple_location_bp
from api.simple_image_api import simple_image_bp
from api.simple_integrated_api import simple_integrated_bp

# Tenta inicializar banco de dados simplificado
try:
    from database.simple_connection import initialize_simple_database
    from config_simple import DATABASE_CONFIG
    
    if initialize_simple_database(DATABASE_CONFIG):
        logger.info("Banco de dados simplificado inicializado")
        DATABASE_MODE = "simple_database"
    else:
        logger.warning("Falha ao conectar com banco - usando modo fallback")
        DATABASE_MODE = "fallback"
        
except ImportError as e:
    logger.warning("Erro ao inicializar banco simplificado: %s", e)
    logger.info("Usando modo fallback (sem banco de dados)")
    DATABASE_MODE = "fallback"

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Habilita CORS para permitir requisições do frontend
    CORS(app, 
         origins=CORS_CONFIG['origins'],
         methods=CORS_CONFIG['methods'],
         allow_headers=CORS_CONFIG['allow_headers'])
    
    # Registra blueprints das APIs simplificadas
    app.register_blueprint(simple_location_bp, url_prefix='/api')
    app.register_blueprint(simple_image_bp, url_prefix='/api')
    app.register_blueprint(simple_integrated_bp, url_prefix='/api')
    
    # Health check global
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'bus-monitoring-api',
            'version': '1.0.0',
            'description': 'API de monitoramento IoT para ônibus'
        }, 200
    
    # Endpoint de informações do projeto
    @app.route('/')
    def project_info():
        return {
            'project': 'Sistema de Monitoramento IoT para Ônibus',
            'description': 'Projeto Integrador - 4º Semestre ADS',
            'features': [
                'Coleta de dados GPS em tempo real',
                'Cálculo de ETA inteligente',
                'Detecção de ocupação com YOLO',
                'Intervalos adaptativos de requisição',
                'Aprendizado de padrões de atraso'
            ],
        'endpoints': {
            'location': '/api/location',
            'location_history': '/api/location/history/<bus_line>',
            'location_current': '/api/location/current',
            'destinations': '/api/location/destinations',
            'image_analysis': '/api/image/analyze',
            'occupancy_history': '/api/image/occupancy/<bus_line>',
            'occupancy_statistics': '/api/image/statistics',
            'integrated': '/api/location-image',
            'integrated_status': '/api/integrated/status/<bus_line>',
            'health': '/api/health'
        }
        }, 200
    
    return app

if __name__ == '__main__':
    logger.info("Iniciando servidor de monitoramento de ônibus IoT...")
    logger.info("Projeto Integrador - 4º Semestre ADS")
    
    app = create_app()
    
    # Inicia o servidor
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
