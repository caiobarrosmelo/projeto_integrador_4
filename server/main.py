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

from config import API_CONFIG, LOGGING_CONFIG, CORS_CONFIG
from api.receive_location_osrm import location_bp

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)

logger = logging.getLogger(__name__)

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Habilita CORS para permitir requisições do frontend
    CORS(app, 
         origins=CORS_CONFIG['origins'],
         methods=CORS_CONFIG['methods'],
         allow_headers=CORS_CONFIG['allow_headers'])
    
    # Registra blueprints das APIs
    app.register_blueprint(location_bp, url_prefix='/api')
    
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
                'history': '/api/location/history/<bus_line>',
                'destinations': '/api/location/destinations',
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
