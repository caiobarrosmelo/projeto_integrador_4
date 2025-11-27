#!/usr/bin/env python3
"""
Script de Inicialização do Sistema Simplificado
Sistema de Monitoramento IoT para Ônibus - Schema Reduzido
"""
import sys
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ é necessário. Versão atual: %s", sys.version)
        return False
    logger.info("Python %s detectado", sys.version.split()[0])
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import flask
        import psycopg2
        import PIL
        import numpy
        logger.info("Dependências principais verificadas")
        return True
    except ImportError as e:
        logger.error("Dependência não encontrada: %s", e)
        logger.info("Execute: pip install -r requirements.txt")
        return False

def check_database_connection():
    """Verifica se o banco de dados está disponível"""
    try:
        from config_simple import DATABASE_CONFIG
        import psycopg2
        
        conn = psycopg2.connect(**DATABASE_CONFIG)
        conn.close()
        logger.info("Conexão com banco de dados: OK")
        return True
    except Exception as e:
        logger.warning("Banco de dados não disponível: %s", e)
        logger.info("Sistema funcionará em modo fallback")
        return False

def create_database_schema():
    """Cria o schema do banco de dados se necessário"""
    try:
        from config_simple import DATABASE_CONFIG
        import psycopg2
        
        # Conecta ao banco
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # Verifica se as tabelas existem
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('bus_location', 'bus_image', 'request_interval', 'prediction_confidence')
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if len(existing_tables) < 4:
            logger.info("Criando schema do banco de dados...")
            
            # Lê e executa o script SQL
            schema_path = Path(__file__).parent / 'db' / 'create_tables.sql'
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                cursor.execute(schema_sql)
                conn.commit()
                logger.info("Schema criado com sucesso")
            else:
                logger.error("Arquivo create_tables.sql não encontrado")
                return False
        else:
            logger.info("Schema do banco já existe")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error("Erro ao criar schema: %s", e)
        return False

def start_server():
    """Inicia o servidor Flask"""
    try:
        logger.info("Iniciando servidor...")
        logger.info("Sistema Simplificado de Monitoramento IoT para Ônibus")
        logger.info("Schema Reduzido (create_tables.sql)")
        logger.info("=" * 50)
        
        # Importa e executa o main
        from main import create_app
        
        app = create_app()
        app.run(
            host='0.0.0.0',
            port=3000,
            debug=True
        )
        
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error("Erro ao iniciar servidor: %s", e)
        return False

def main():
    """Função principal"""
    logger.info("=== SISTEMA SIMPLIFICADO DE MONITORAMENTO IoT ===")
    logger.info("Projeto Integrador - 4º Semestre ADS")
    logger.info("=" * 50)
    
    # Verificações iniciais
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        return 1
    
    # Verifica banco de dados
    db_available = check_database_connection()
    
    if db_available:
        # Tenta criar schema se necessário
        create_database_schema()
    else:
        logger.info("Modo fallback ativado - sem banco de dados")
    
    # Inicia servidor
    logger.info("Iniciando servidor na porta 3000...")
    logger.info("Acesse: http://localhost:3000")
    logger.info("Health check: http://localhost:3000/health")
    logger.info("=" * 50)
    
    start_server()
    return 0

if __name__ == '__main__':
    sys.exit(main())
