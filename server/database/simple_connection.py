"""
Sistema de Conexão Simplificado com Banco de Dados
Adaptado para usar create_tables.sql (schema reduzido)
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import psycopg2
import psycopg2.extras
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

# Configuração de logging
logger = logging.getLogger(__name__)

# ============================================================
#                GERENCIADOR DE BANCO DE DADOS
# ============================================================

class SimpleDatabaseManager:
    """
    Gerenciador simplificado de conexões com banco de dados PostgreSQL
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Conecta ao banco de dados."""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config['port'],
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.info("Conexão com banco de dados estabelecida")
        except Exception as e:
            logger.error(f"Erro ao conectar com banco: {e}")
            self.connection = None
    
    @contextmanager
    def get_cursor(self):
        """Obtém cursor com rollback automático em caso de erro."""
        if not self.connection:
            raise Exception("Banco de dados não conectado")
        
        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Erro no cursor: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: Tuple = None, fetch: bool = False):
        """Executa query com ou sem retorno."""
        if not self.connection:
            return None
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    return [dict(row) for row in cursor.fetchall()]
                self.connection.commit()
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return None
    
    def test_connection(self) -> bool:
        """Testa se o banco responde."""
        try:
            result = self.execute_query("SELECT 1", fetch=True)
            return result is not None and len(result) > 0
        except:
            return False
    
    def get_database_info(self):
        """Retorna lista de tabelas e contagem de registros."""
        try:
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            tables_result = self.execute_query(tables_query, fetch=True)
            tables = [t['table_name'] for t in tables_result] if tables_result else []

            table_counts = {}
            for t in tables:
                try:
                    count_q = f"SELECT COUNT(*) as count FROM {t}"
                    res = self.execute_query(count_q, fetch=True)
                    table_counts[t] = res[0]['count'] if res else 0
                except:
                    table_counts[t] = 0

            return {
                'tables': tables,
                'table_counts': table_counts,
                'total_records': sum(table_counts.values()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações do banco: {e}")
            return {'error': str(e)}

# ============================================================
#               REPOSITÓRIO DE LOCALIZAÇÃO
# ============================================================

class SimpleBusLocationRepository:
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_location(self, bus_line: str, latitude: float, longitude: float):
        query = """
            INSERT INTO bus_location 
            (bus_line, latitude, longitude, timestamp_location)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        params = (bus_line, latitude, longitude, datetime.now())
        res = self.db.execute_query(query, params, fetch=True)
        return res[0]['id'] if res else None
    
    def get_current_locations(self, bus_line: str = None, minutes: int = 5):
        query = """
            SELECT * FROM bus_location 
            WHERE timestamp_location > %s
        """
        params = [datetime.now() - timedelta(minutes=minutes)]

        if bus_line:
            query += " AND bus_line = %s"
            params.append(bus_line)

        query += " ORDER BY timestamp_location DESC LIMIT 50"
        return self.db.execute_query(query, tuple(params), fetch=True) or []
    
    def get_location_history(self, bus_line: str, hours: int = 24, limit: int = 100):
        query = """
            SELECT * FROM bus_location 
            WHERE bus_line = %s
            AND timestamp_location > %s
            ORDER BY timestamp_location DESC
            LIMIT %s
        """
        params = (bus_line, datetime.now() - timedelta(hours=hours), limit)
        return self.db.execute_query(query, params, fetch=True) or []

# ============================================================
#               REPOSITÓRIO DE OCUPAÇÃO
# ============================================================

class SimpleOccupancyRepository:
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_image_analysis(self, location_id: int, image_data: bytes, occupancy_count: int = None):
        query = """
            INSERT INTO bus_image
            (location_id, image_data, timestamp_image, occupancy_count)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        params = (location_id, image_data, datetime.now(), occupancy_count)
        res = self.db.execute_query(query, params, fetch=True)
        return res[0]['id'] if res else None
    
    def get_occupancy_statistics(self, bus_line: str = None, hours: int = 24):
        query = """
            SELECT 
                bi.occupancy_count,
                COUNT(*) as count,
                AVG(bi.occupancy_count) as avg_occupancy,
                bl.bus_line
            FROM bus_image bi
            JOIN bus_location bl ON bi.location_id = bl.id
            WHERE bi.timestamp_image > %s
            AND bi.occupancy_count IS NOT NULL
        """
        params = [datetime.now() - timedelta(hours=hours)]

        if bus_line:
            query += " AND bl.bus_line = %s"
            params.append(bus_line)

        query += """
            GROUP BY bi.occupancy_count, bl.bus_line
            ORDER BY bl.bus_line, bi.occupancy_count
        """
        results = self.db.execute_query(query, tuple(params), fetch=True) or []

        stats = {
            'total_analyses': sum(r['count'] for r in results),
            'by_occupancy': {},
            'by_line': {}
        }

        for r in results:
            occ = r['occupancy_count']
            line = r['bus_line']
            count = r['count']
            avg = r['avg_occupancy']

            stats['by_occupancy'].setdefault(occ, {'count': 0, 'avg_occupancy': 0})
            stats['by_occupancy'][occ]['count'] += count
            stats['by_occupancy'][occ]['avg_occupancy'] += avg

            stats['by_line'].setdefault(line, {'total_analyses': 0, 'avg_occupancy': 0})
            stats['by_line'][line]['total_analyses'] += count
            stats['by_line'][line]['avg_occupancy'] += avg

        return stats

# ============================================================
#                   REPOSITÓRIO DE ETA
# ============================================================

class SimpleETARepository:
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_eta_prediction(self, location_id: int, predicted_arrival: datetime,
                            confidence_percent: float):
        query = """
            INSERT INTO prediction_confidence
            (location_id, predicted_arrival, confidence_percent, timestamp_prediction)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        params = (location_id, predicted_arrival, confidence_percent, datetime.now())
        res = self.db.execute_query(query, params, fetch=True)
        return res[0]['id'] if res else None
    
    def update_actual_arrival(self, prediction_id: int, actual_arrival: datetime):
        query = """
            UPDATE prediction_confidence 
            SET actual_arrival = %s
            WHERE id = %s
        """
        self.db.execute_query(query, (actual_arrival, prediction_id))
    
    def get_eta_statistics(self, bus_line: str = None, days: int = 7):
        query = """
            SELECT 
                pc.confidence_percent,
                pc.predicted_arrival,
                pc.actual_arrival,
                bl.bus_line
            FROM prediction_confidence pc
            JOIN bus_location bl ON pc.location_id = bl.id
            WHERE pc.timestamp_prediction > %s
        """
        params = [datetime.now() - timedelta(days=days)]

        if bus_line:
            query += " AND bl.bus_line = %s"
            params.append(bus_line)

        results = self.db.execute_query(query, tuple(params), fetch=True) or []

        if not results:
            return {'error': 'Nenhum dado de ETA encontrado'}

        conf_values = [r['confidence_percent'] for r in results if r['confidence_percent']]

        stats = {
            'total_predictions': len(results),
            'avg_confidence_percent': sum(conf_values) / len(conf_values) if conf_values else 0,
            'by_line': {}
        }

        for r in results:
            line = r['bus_line']
            stats['by_line'].setdefault(line, {'count': 0, 'avg_confidence': 0})
            stats['by_line'][line]['count'] += 1
            if r['confidence_percent']:
                stats['by_line'][line]['avg_confidence'] += r['confidence_percent']

        for line in stats['by_line']:
            stats['by_line'][line]['avg_confidence'] /= stats['by_line'][line]['count']

        return stats

# ============================================================
#           REPOSITÓRIO DE INTERVALOS ADAPTATIVOS
# ============================================================

class SimpleIntervalRepository:
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_interval(self, location_id: int, interval_seconds: int):
        query = """
            INSERT INTO request_interval
            (location_id, start_time, end_time, interval_seconds)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=interval_seconds)
        params = (location_id, start_time, end_time, interval_seconds)
        res = self.db.execute_query(query, params, fetch=True)
        return res[0]['id'] if res else None

# ============================================================
#              INSTÂNCIAS GLOBAIS E INICIALIZAÇÃO
# ============================================================

simple_db_manager = None
simple_bus_repo = None
simple_occupancy_repo = None
simple_eta_repo = None
simple_interval_repo = None

def initialize_simple_database(config: Dict[str, Any]) -> bool:
    global simple_db_manager, simple_bus_repo, simple_occupancy_repo, simple_eta_repo, simple_interval_repo
    
    try:
        simple_db_manager = SimpleDatabaseManager(config)
        
        if simple_db_manager.test_connection():
            simple_bus_repo = SimpleBusLocationRepository(simple_db_manager)
            simple_occupancy_repo = SimpleOccupancyRepository(simple_db_manager)
            simple_eta_repo = SimpleETARepository(simple_db_manager)
            simple_interval_repo = SimpleIntervalRepository(simple_db_manager)
            
            logger.info("Sistema simplificado de banco de dados inicializado")
            return True
        
        logger.error("Falha ao conectar com banco de dados")
        return False
    
    except Exception as e:
        logger.error(f"Erro ao inicializar banco simplificado: {e}")
        return False

def get_simple_database_manager():
    return simple_db_manager

def get_simple_bus_repository():
    return simple_bus_repo

def get_simple_occupancy_repository():
    return simple_occupancy_repo

def get_simple_eta_repository():
    return simple_eta_repo

def get_simple_interval_repository():
    return simple_interval_repo
