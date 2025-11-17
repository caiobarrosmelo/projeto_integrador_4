from typing import List, Dict, Optional
from .simple_connection import get_simple_database_manager


class SimpleBusRepository:
    """
    Repositório responsável por consultar localizações de ônibus
    usando o SimpleDatabaseManager.
    """

    def __init__(self):
        self.db = get_simple_database_manager()

    def get_current_locations(self, bus_line: Optional[str] = None, minutes: int = 5) -> List[Dict]:
        """
        Retorna localizações de ônibus dentro do intervalo de tempo especificado.

        :param bus_line: Opcional — filtra por uma linha específica.
        :param minutes: Intervalo (em minutos) considerado "recente".
        """
        if not self.db:
            print("Erro: conexão get_simple_database_manager() retornou None.")
            return []

        try:
            # base da query
            query = """
                SELECT 
                    id,
                    bus_line,
                    latitude,
                    longitude,
                    timestamp_location
                FROM bus_location
                WHERE timestamp_location >= NOW() - INTERVAL %s MINUTE
            """

            params = [minutes]

            # filtro por linha se fornecido
            if bus_line:
                query += " AND bus_line = %s"
                params.append(bus_line)

            # ordenar do mais recente para o mais antigo
            query += " ORDER BY timestamp_location DESC"

            rows = self.db.fetch_all(query, params)

            return [
                {
                    "id": row["id"],
                    "bus_line": row["bus_line"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "timestamp_location": row["timestamp_location"].isoformat()
                }
                for row in rows
            ]

        except Exception as e:
            print("Erro no SimpleBusRepository.get_current_locations:", e)
            return []

