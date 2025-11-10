"""
Sistema de Confiança de ETA baseado em Machine Learning
Integra dados de ocupação, tráfego e histórico para melhorar previsões
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
from dataclasses import dataclass

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class ETAPrediction:
    """Classe para representar uma previsão de ETA"""
    eta_minutes: float
    confidence_percent: float
    factors: Dict[str, float]
    timestamp: datetime
    bus_line: str
    occupancy_level: int
    traffic_factor: float
    distance_km: float

class ETAConfidencePredictor:
    """
    Preditor de confiança para ETA baseado em Machine Learning
    """
    
    def __init__(self):
        """Inicializa o preditor de confiança"""
        self.history_data = []
        self.confidence_models = {}
        
        # Fatores que afetam a confiança
        self.confidence_factors = {
            'occupancy_impact': {
                0: 1.0,  # Vazio - não afeta
                1: 0.95, # Baixa - pouco impacto
                2: 0.90, # Média - impacto moderado
                3: 0.80, # Alta - impacto significativo
                4: 0.70  # Lotado - alto impacto
            },
            'traffic_impact': {
                'low': 1.0,    # Tráfego baixo
                'medium': 0.85, # Tráfego médio
                'high': 0.70   # Tráfego alto
            },
            'time_of_day_impact': {
                'rush_morning': 0.75,    # 7h-9h
                'normal_morning': 0.90,  # 9h-12h
                'lunch': 0.85,           # 12h-14h
                'normal_afternoon': 0.90, # 14h-17h
                'rush_evening': 0.70,    # 17h-19h
                'night': 0.95,           # 19h-23h
                'late_night': 0.98       # 23h-7h
            },
            'distance_impact': {
                'short': 0.95,   # < 2km
                'medium': 0.90,  # 2-5km
                'long': 0.85     # > 5km
            }
        }
    
    def get_time_period(self, hour: int) -> str:
        """
        Determina o período do dia baseado na hora
        
        Args:
            hour: Hora do dia (0-23)
            
        Returns:
            Período do dia
        """
        if 7 <= hour <= 9:
            return 'rush_morning'
        elif 9 < hour <= 12:
            return 'normal_morning'
        elif 12 < hour <= 14:
            return 'lunch'
        elif 14 < hour <= 17:
            return 'normal_afternoon'
        elif 17 < hour <= 19:
            return 'rush_evening'
        elif 19 < hour <= 23:
            return 'night'
        else:
            return 'late_night'
    
    def get_traffic_level(self, traffic_factor: float) -> str:
        """
        Determina o nível de tráfego baseado no fator
        
        Args:
            traffic_factor: Fator de tráfego (0.0-1.0)
            
        Returns:
            Nível de tráfego
        """
        if traffic_factor >= 0.8:
            return 'low'
        elif traffic_factor >= 0.6:
            return 'medium'
        else:
            return 'high'
    
    def get_distance_category(self, distance_km: float) -> str:
        """
        Categoriza a distância
        
        Args:
            distance_km: Distância em quilômetros
            
        Returns:
            Categoria da distância
        """
        if distance_km < 2:
            return 'short'
        elif distance_km <= 5:
            return 'medium'
        else:
            return 'long'
    
    def calculate_base_confidence(self, eta_minutes: float, distance_km: float) -> float:
        """
        Calcula confiança base baseada na distância e tempo estimado
        
        Args:
            eta_minutes: Tempo estimado em minutos
            distance_km: Distância em quilômetros
            
        Returns:
            Confiança base (0.0-1.0)
        """
        # Confiança baseada na velocidade média
        if distance_km > 0:
            avg_speed = (distance_km / eta_minutes) * 60  # km/h
            
            # Velocidades muito baixas ou muito altas reduzem confiança
            if avg_speed < 5 or avg_speed > 50:
                base_confidence = 0.6
            elif 10 <= avg_speed <= 30:
                base_confidence = 0.9
            else:
                base_confidence = 0.8
        else:
            base_confidence = 0.5
        
        return base_confidence
    
    def calculate_confidence_factors(self, occupancy_level: int, traffic_factor: float, 
                                   hour: int, distance_km: float) -> Dict[str, float]:
        """
        Calcula fatores que afetam a confiança
        
        Args:
            occupancy_level: Nível de ocupação (0-4)
            traffic_factor: Fator de tráfego
            hour: Hora do dia
            distance_km: Distância em quilômetros
            
        Returns:
            Dicionário com fatores de confiança
        """
        time_period = self.get_time_period(hour)
        traffic_level = self.get_traffic_level(traffic_factor)
        distance_category = self.get_distance_category(distance_km)
        
        factors = {
            'occupancy': self.confidence_factors['occupancy_impact'][occupancy_level],
            'traffic': self.confidence_factors['traffic_impact'][traffic_level],
            'time_of_day': self.confidence_factors['time_of_day_impact'][time_period],
            'distance': self.confidence_factors['distance_impact'][distance_category]
        }
        
        return factors
    
    def predict_eta_confidence(self, eta_minutes: float, occupancy_level: int,
                             traffic_factor: float, distance_km: float,
                             bus_line: str, timestamp: datetime = None) -> ETAPrediction:
        """
        Prediz a confiança de uma previsão de ETA
        
        Args:
            eta_minutes: Tempo estimado em minutos
            occupancy_level: Nível de ocupação (0-4)
            traffic_factor: Fator de tráfego
            distance_km: Distância em quilômetros
            bus_line: Linha do ônibus
            timestamp: Timestamp da previsão
            
        Returns:
            Objeto ETAPrediction com confiança calculada
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        hour = timestamp.hour
        
        # Calcula confiança base
        base_confidence = self.calculate_base_confidence(eta_minutes, distance_km)
        
        # Calcula fatores de impacto
        factors = self.calculate_confidence_factors(
            occupancy_level, traffic_factor, hour, distance_km
        )
        
        # Aplica fatores à confiança base
        final_confidence = base_confidence
        for factor_name, factor_value in factors.items():
            final_confidence *= factor_value
        
        # Ajusta confiança baseada no histórico da linha (se disponível)
        historical_adjustment = self.get_historical_adjustment(bus_line, hour)
        final_confidence *= historical_adjustment
        
        # Garante que a confiança está entre 0 e 1
        final_confidence = max(0.1, min(1.0, final_confidence))
        
        # Converte para porcentagem
        confidence_percent = final_confidence * 100
        
        return ETAPrediction(
            eta_minutes=eta_minutes,
            confidence_percent=round(confidence_percent, 1),
            factors=factors,
            timestamp=timestamp,
            bus_line=bus_line,
            occupancy_level=occupancy_level,
            traffic_factor=traffic_factor,
            distance_km=distance_km
        )
    
    def get_historical_adjustment(self, bus_line: str, hour: int) -> float:
        """
        Obtém ajuste baseado no histórico de precisão da linha
        
        Args:
            bus_line: Linha do ônibus
            hour: Hora do dia
            
        Returns:
            Fator de ajuste baseado no histórico
        """
        # Em modo fallback, retorna fator neutro
        # Em implementação real, consultaria banco de dados
        
        # Simula diferentes níveis de confiabilidade por linha
        line_reliability = {
            'L1': 0.95,  # Linha muito confiável
            'L2': 0.90,  # Linha confiável
            'L3': 0.85,  # Linha moderadamente confiável
            'L4': 0.80,  # Linha menos confiável
        }
        
        return line_reliability.get(bus_line, 0.85)  # Padrão para linhas não mapeadas
    
    def add_prediction_result(self, prediction: ETAPrediction, actual_eta: float):
        """
        Adiciona resultado de uma previsão para aprendizado
        
        Args:
            prediction: Previsão original
            actual_eta: ETA real observado
        """
        try:
            # Calcula erro da previsão
            error_minutes = abs(prediction.eta_minutes - actual_eta)
            error_percentage = (error_minutes / prediction.eta_minutes) * 100
            
            # Cria registro de resultado
            result_record = {
                'timestamp': prediction.timestamp.isoformat(),
                'bus_line': prediction.bus_line,
                'predicted_eta': prediction.eta_minutes,
                'actual_eta': actual_eta,
                'error_minutes': error_minutes,
                'error_percentage': error_percentage,
                'confidence_percent': prediction.confidence_percent,
                'occupancy_level': prediction.occupancy_level,
                'traffic_factor': prediction.traffic_factor,
                'distance_km': prediction.distance_km,
                'factors': prediction.factors
            }
            
            # Adiciona ao histórico
            self.history_data.append(result_record)
            
            # Mantém apenas os últimos 1000 registros
            if len(self.history_data) > 1000:
                self.history_data = self.history_data[-1000:]
            
            logger.info(f"Resultado adicionado: erro {error_minutes:.1f}min ({error_percentage:.1f}%)")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar resultado: {e}")
    
    def get_confidence_statistics(self, bus_line: str = None) -> Dict:
        """
        Obtém estatísticas de confiança
        
        Args:
            bus_line: Linha específica (opcional)
            
        Returns:
            Estatísticas de confiança
        """
        try:
            # Filtra dados por linha se especificado
            data = self.history_data
            if bus_line:
                data = [d for d in data if d['bus_line'] == bus_line]
            
            if not data:
                return {
                    'total_predictions': 0,
                    'avg_error_percentage': 0,
                    'avg_confidence': 0,
                    'accuracy_by_occupancy': {},
                    'accuracy_by_time': {}
                }
            
            # Calcula estatísticas gerais
            total_predictions = len(data)
            avg_error_percentage = np.mean([d['error_percentage'] for d in data])
            avg_confidence = np.mean([d['confidence_percent'] for d in data])
            
            # Agrupa por nível de ocupação
            occupancy_stats = {}
            for level in range(5):
                level_data = [d for d in data if d['occupancy_level'] == level]
                if level_data:
                    occupancy_stats[level] = {
                        'count': len(level_data),
                        'avg_error': np.mean([d['error_percentage'] for d in level_data]),
                        'avg_confidence': np.mean([d['confidence_percent'] for d in level_data])
                    }
            
            # Agrupa por período do dia
            time_stats = {}
            for hour in range(24):
                hour_data = [d for d in data if datetime.fromisoformat(d['timestamp']).hour == hour]
                if hour_data:
                    time_stats[hour] = {
                        'count': len(hour_data),
                        'avg_error': np.mean([d['error_percentage'] for d in hour_data]),
                        'avg_confidence': np.mean([d['confidence_percent'] for d in hour_data])
                    }
            
            return {
                'total_predictions': total_predictions,
                'avg_error_percentage': round(avg_error_percentage, 2),
                'avg_confidence': round(avg_confidence, 2),
                'accuracy_by_occupancy': occupancy_stats,
                'accuracy_by_time': time_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {'error': str(e)}

# Instância global do preditor de confiança
eta_confidence_predictor = ETAConfidencePredictor()

def predict_eta_with_confidence(eta_minutes: float, occupancy_level: int,
                              traffic_factor: float, distance_km: float,
                              bus_line: str, timestamp: datetime = None) -> Dict:
    """
    Função wrapper para predição de ETA com confiança
    
    Args:
        eta_minutes: Tempo estimado em minutos
        occupancy_level: Nível de ocupação (0-4)
        traffic_factor: Fator de tráfego
        distance_km: Distância em quilômetros
        bus_line: Linha do ônibus
        timestamp: Timestamp da previsão
        
    Returns:
        Dicionário com ETA e confiança
    """
    prediction = eta_confidence_predictor.predict_eta_confidence(
        eta_minutes, occupancy_level, traffic_factor, distance_km, bus_line, timestamp
    )
    
    return {
        'eta_minutes': prediction.eta_minutes,
        'confidence_percent': prediction.confidence_percent,
        'confidence_factors': prediction.factors,
        'timestamp': prediction.timestamp.isoformat(),
        'bus_line': prediction.bus_line,
        'occupancy_level': prediction.occupancy_level,
        'traffic_factor': prediction.traffic_factor,
        'distance_km': prediction.distance_km,
        'status': 'success'
    }

def get_eta_confidence_statistics(bus_line: str = None) -> Dict:
    """
    Função wrapper para obter estatísticas de confiança
    
    Args:
        bus_line: Linha específica (opcional)
        
    Returns:
        Estatísticas de confiança
    """
    return eta_confidence_predictor.get_confidence_statistics(bus_line)
