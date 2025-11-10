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
import json

# Configuração de logging
logger = logging.getLogger(__name__)

class SimpleDatabaseManager:
    """
    Gerenciador simplificado de conexões com banco de dados PostgreSQL
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            config: Configurações do banco de dados
        """
        self.config = config
        self.connection = None
        self._connect()
    
    def _connect(self):
        """
        Conecta ao banco de dados
        """
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
        """
        Context manager para obter cursor do banco
        """
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
    
    def execute_query(self, query: str, params: Tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
        """
        Executa uma query no banco de dados
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            fetch: Se deve retornar resultados
            
        Returns:
            Lista de resultados ou None
        """
        if not self.connection:
            return None
            
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    self.connection.commit()
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return None
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            result = self.execute_query("SELECT 1", fetch=True)
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Obtém informações básicas do banco de dados
        
        Returns:
            Dicionário com informações do banco
        """
        try:
            # Informações das tabelas
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            tables_result = self.execute_query(tables_query, fetch=True)
            tables = [t['table_name'] for t in tables_result] if tables_result else []
            
            # Contagem de registros por tabela
            table_counts = {}
            for table in tables:
                try:
                    count_query = f"SELECT COUNT(*) as count FROM {table}"
                    count_result = self.execute_query(count_query, fetch=True)
                    if count_result:
                        table_counts[table] = count_result[0]['count']
                except:
                    table_counts[table] = 0
            
            return {
                'tables': tables,
                'table_counts': table_counts,
                'total_records': sum(table_counts.values()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do banco: {e}")
            return {'error': str(e)}

class SimpleBusLocationRepository:
    """
    Repositório simplificado para operações com localizações de ônibus
    """
    
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_location(self, bus_line: str, latitude: float, longitude: float) -> Optional[int]:
        """
        Salva localização de ônibus
        
        Args:
            bus_line: Linha do ônibus
            latitude: Latitude GPS
            longitude: Longitude GPS
            
        Returns:
            ID da localização salva ou None
        """
        query = """
            INSERT INTO bus_location 
            (bus_line, latitude, longitude, timestamp_location)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        params = (bus_line, latitude, longitude, datetime.now())
        result = self.db.execute_query(query, params, fetch=True)
        return result[0]['id'] if result else None
    
    def get_current_locations(self, bus_line: str = None, minutes: int = 5) -> List[Dict]:
        """
        Obtém localizações atuais dos ônibus
        
        Args:
            bus_line: Linha específica (opcional)
            minutes: Últimos X minutos
            
        Returns:
            Lista de localizações
        """
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
    
    def get_location_history(self, bus_line: str, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Obtém histórico de localizações
        
        Args:
            bus_line: Linha do ônibus
            hours: Últimas X horas
            limit: Limite de registros
            
        Returns:
            Lista de localizações históricas
        """
        query = """
            SELECT * FROM bus_location 
            WHERE bus_line = %s
            AND timestamp_location > %s
            ORDER BY timestamp_location DESC
            LIMIT %s
        """
        
        params = (bus_line, datetime.now() - timedelta(hours=hours), limit)
        return self.db.execute_query(query, params, fetch=True) or []

class SimpleOccupancyRepository:
    """
    Repositório simplificado para operações com análise de ocupação
    """
    
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_image_analysis(self, location_id: int, image_data: bytes, 
                          occupancy_count: int = None) -> Optional[int]:
        """
        Salva análise de imagem
        
        Args:
            location_id: ID da localização
            image_data: Dados da imagem
            occupancy_count: Contagem de ocupação
            
        Returns:
            ID da imagem salva ou None
        """
        query = """
            INSERT INTO bus_image
            (location_id, image_data, timestamp_image, occupancy_count)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        params = (location_id, image_data, datetime.now(), occupancy_count)
        result = self.db.execute_query(query, params, fetch=True)
        return result[0]['id'] if result else None
    
    def get_occupancy_statistics(self, bus_line: str = None, hours: int = 24) -> Dict[str, Any]:
        """
        Obtém estatísticas de ocupação
        
        Args:
            bus_line: Linha específica (opcional)
            hours: Últimas X horas
            
        Returns:
            Estatísticas de ocupação
        """
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
        
        # Processa resultados
        statistics = {
            'total_analyses': sum(r['count'] for r in results),
            'by_occupancy': {},
            'by_line': {}
        }
        
        for result in results:
            occupancy = result['occupancy_count']
            line = result['bus_line']
            count = result['count']
            avg = result['avg_occupancy']
            
            # Por ocupação
            if occupancy not in statistics['by_occupancy']:
                statistics['by_occupancy'][occupancy] = {
                    'count': 0,
                    'avg_occupancy': 0
                }
            statistics['by_occupancy'][occupancy]['count'] += count
            statistics['by_occupancy'][occupancy]['avg_occupancy'] += avg
            
            # Por linha
            if line not in statistics['by_line']:
                statistics['by_line'][line] = {
                    'total_analyses': 0,
                    'avg_occupancy': 0
                }
            statistics['by_line'][line]['total_analyses'] += count
            statistics['by_line'][line]['avg_occupancy'] += avg
        
        return statistics

class SimpleETARepository:
    """
    Repositório simplificado para operações com previsões de ETA
    """
    
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_eta_prediction(self, location_id: int, predicted_arrival: datetime,
                          confidence_percent: float) -> Optional[int]:
        """
        Salva previsão de ETA
        
        Args:
            location_id: ID da localização
            predicted_arrival: Previsão de chegada
            confidence_percent: Confiança da previsão
            
        Returns:
            ID da previsão salva ou None
        """
        query = """
            INSERT INTO prediction_confidence
            (location_id, predicted_arrival, confidence_percent, timestamp_prediction)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        params = (location_id, predicted_arrival, confidence_percent, datetime.now())
        result = self.db.execute_query(query, params, fetch=True)
        return result[0]['id'] if result else None
    
    def update_actual_arrival(self, prediction_id: int, actual_arrival: datetime):
        """
        Atualiza chegada real de uma previsão
        
        Args:
            prediction_id: ID da previsão
            actual_arrival: Chegada real
        """
        query = """
            UPDATE prediction_confidence 
            SET actual_arrival = %s
            WHERE id = %s
        """
        
        params = (actual_arrival, prediction_id)
        self.db.execute_query(query, params)
    
    def get_eta_statistics(self, bus_line: str = None, days: int = 7) -> Dict[str, Any]:
        """
        Obtém estatísticas de ETA
        
        Args:
            bus_line: Linha específica (opcional)
            days: Últimos X dias
            
        Returns:
            Estatísticas de ETA
        """
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
        
        # Calcula estatísticas básicas
        confidence_values = [r['confidence_percent'] for r in results if r['confidence_percent']]
        
        statistics = {
            'total_predictions': len(results),
            'avg_confidence_percent': sum(confidence_values) / len(confidence_values) if confidence_values else 0,
            'by_line': {}
        }
        
        # Agrupa por linha
        for result in results:
            line = result['bus_line']
            if line not in statistics['by_line']:
                statistics['by_line'][line] = {
                    'count': 0,
                    'avg_confidence': 0
                }
            statistics['by_line'][line]['count'] += 1
            if result['confidence_percent']:
                statistics['by_line'][line]['avg_confidence'] += result['confidence_percent']
        
        # Calcula médias por linha
        for line in statistics['by_line']:
            count = statistics['by_line'][line]['count']
            if count > 0:
                statistics['by_line'][line]['avg_confidence'] /= count
        
        return statistics

class SimpleIntervalRepository:
    """
    Repositório simplificado para operações com intervalos adaptativos
    """
    
    def __init__(self, db_manager: SimpleDatabaseManager):
        self.db = db_manager
    
    def save_interval(self, location_id: int, interval_seconds: int) -> Optional[int]:
        """
        Salva intervalo adaptativo
        
        Args:
            location_id: ID da localização
            interval_seconds: Intervalo em segundos
            
        Returns:
            ID do intervalo salvo ou None
        """
        query = """
            INSERT INTO request_interval
            (location_id, start_time, end_time, interval_seconds)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=interval_seconds)
        params = (location_id, start_time, end_time, interval_seconds)
        
        result = self.db.execute_query(query, params, fetch=True)
        return result[0]['id'] if result else None

# Instâncias globais
simple_db_manager = None
simple_bus_repo = None
simple_occupancy_repo = None
simple_eta_repo = None
simple_interval_repo = None

def initialize_simple_database(config: Dict[str, Any]) -> bool:
    """
    Inicializa o sistema simplificado de banco de dados
    
    Args:
        config: Configurações do banco
        
    Returns:
        True se inicializado com sucesso
    """
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
        else:
            logger.error("Falha ao conectar com banco de dados")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao inicializar banco simplificado: {e}")
        return False

def get_simple_database_manager() -> Optional[SimpleDatabaseManager]:
    """Retorna o gerenciador simplificado de banco"""
    return simple_db_manager

def get_simple_bus_repository() -> Optional[SimpleBusLocationRepository]:
    """Retorna o repositório simplificado de localizações"""
    return simple_bus_repo

def get_simple_occupancy_repository() -> Optional[SimpleOccupancyRepository]:
    """Retorna o repositório simplificado de ocupação"""
    return simple_occupancy_repo

def get_simple_eta_repository() -> Optional[SimpleETARepository]:
    """Retorna o repositório simplificado de ETA"""
    return simple_eta_repo

def get_simple_interval_repository() -> Optional[SimpleIntervalRepository]:
    """Retorna o repositório simplificado de intervalos"""
    return simple_interval_repo
