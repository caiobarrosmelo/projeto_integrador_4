"""
Módulo para cálculo de ETA usando OSRM (Open Source Routing Machine)
Muito mais preciso que cálculos manuais baseados em distância
"""

import requests
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

# Importa configurações centralizadas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OSRM_CONFIG

logger = logging.getLogger(__name__)

class OSRMETA:
    """Classe para cálculo de ETA usando OSRM"""
    
    def __init__(self, osrm_server: str = None, profile: str = None):
        self.osrm_server = osrm_server or OSRM_CONFIG['server_url']
        self.profile = profile or OSRM_CONFIG['profile']
        self.timeout = OSRM_CONFIG['timeout_seconds']
        self.max_retries = OSRM_CONFIG['max_retries']
        
    def get_route_info(self, start_lat: float, start_lon: float, 
                      end_lat: float, end_lon: float) -> Dict:
        """
        Obtém informações de rota do OSRM
        Retorna: distância, duração, instruções
        """
        try:
            # Formato: longitude,latitude;longitude,latitude
            coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
            
            url = f"{self.osrm_server}/route/v1/{self.profile}/{coordinates}"
            
            params = {
                'overview': 'false',  # Não retorna geometria da rota
                'steps': 'false',     # Não retorna instruções detalhadas
                'alternatives': 'false'  # Apenas a rota mais rápida
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    
                    return {
                        'distance_meters': route['distance'],
                        'duration_seconds': route['duration'],
                        'duration_minutes': round(route['duration'] / 60, 1),
                        'status': 'success'
                    }
                else:
                    logger.error(f"OSRM error: {data.get('message', 'Unknown error')}")
                    return {'status': 'error', 'message': data.get('message', 'OSRM error')}
            else:
                logger.error(f"OSRM HTTP error: {response.status_code}")
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OSRM request error: {e}")
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            logger.error(f"OSRM unexpected error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_eta_with_traffic_factor(self, start_lat: float, start_lon: float,
                                   end_lat: float, end_lon: float,
                                   traffic_factor: float = 1.0) -> Dict:
        """
        Calcula ETA considerando fator de tráfego
        """
        route_info = self.get_route_info(start_lat, start_lon, end_lat, end_lon)
        
        if route_info['status'] != 'success':
            return route_info
        
        # Aplica fator de tráfego
        base_duration = route_info['duration_seconds']
        adjusted_duration = base_duration * traffic_factor
        
        # Calcula timestamp de chegada
        estimated_arrival = datetime.now() + timedelta(seconds=adjusted_duration)
        
        return {
            'status': 'success',
            'eta_minutes': round(adjusted_duration / 60, 1),
            'base_eta_minutes': round(base_duration / 60, 1),
            'estimated_arrival': estimated_arrival.isoformat(),
            'distance_km': round(route_info['distance_meters'] / 1000, 2),
            'traffic_factor': traffic_factor,
            'confidence_percent': OSRM_CONFIG['confidence_osrm'],  # OSRM é muito confiável
            'source': 'OSRM'
        }
    
    def get_multiple_routes(self, coordinates: list) -> Dict:
        """
        Calcula rota com múltiplos waypoints
        Útil para rotas de ônibus com várias paradas
        """
        try:
            # Formato: lon1,lat1;lon2,lat2;lon3,lat3
            coord_string = ';'.join([f"{lon},{lat}" for lat, lon in coordinates])
            
            url = f"{self.osrm_server}/route/v1/{self.profile}/{coord_string}"
            
            params = {
                'overview': 'false',
                'steps': 'false',
                'alternatives': 'false'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    
                    return {
                        'status': 'success',
                        'total_distance_km': round(route['distance'] / 1000, 2),
                        'total_duration_minutes': round(route['duration'] / 60, 1),
                        'waypoints': data.get('waypoints', [])
                    }
                else:
                    return {'status': 'error', 'message': data.get('message', 'OSRM error')}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"OSRM multiple routes error: {e}")
            return {'status': 'error', 'message': str(e)}

# Instância global do OSRM
osrm_eta = OSRMETA()

def calculate_eta_with_osrm(current_lat: float, current_lon: float,
                           target_lat: float, target_lon: float,
                           traffic_factor: float = 1.0) -> Dict:
    """
    Função helper para calcular ETA usando OSRM
    """
    return osrm_eta.get_eta_with_traffic_factor(
        current_lat, current_lon, target_lat, target_lon, traffic_factor
    )

def get_traffic_factor_by_hour_osrm(hour: int) -> float:
    """
    Fator de tráfego baseado no horário (para usar com OSRM)
    OSRM já considera algumas condições de tráfego, então os fatores são menores
    """
    if 7 <= hour <= 9:      # Pico manhã
        return 1.3
    elif 12 <= hour <= 14:  # Almoço
        return 1.1
    elif 17 <= hour <= 19:  # Pico tarde
        return 1.4
    elif 19 <= hour <= 23:  # Noite
        return 0.9
    else:                   # Madrugada
        return 0.8
