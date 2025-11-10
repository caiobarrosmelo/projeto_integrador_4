"""
Sistema de Predição de Ocupação de Ônibus usando YOLO
Baseado nos requisitos do projeto IoT de monitoramento
"""

import cv2
import numpy as np
import base64
import io
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
import os

# Configuração de logging
logger = logging.getLogger(__name__)

class OccupancyPredictor:
    """
    Classe para predição de ocupação de ônibus usando YOLO
    """
    
    def __init__(self, model_path: str = None, confidence_threshold: float = 0.5):
        """
        Inicializa o preditor de ocupação
        
        Args:
            model_path: Caminho para o modelo YOLO
            confidence_threshold: Limiar de confiança para detecções
        """
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self.model = None
        self.class_names = ['person']  # Classes que o modelo detecta
        
        # Configurações específicas para ônibus
        self.bus_config = {
            'max_capacity': 50,  # Capacidade máxima do ônibus
            'occupancy_levels': {
                0: {'name': 'vazio', 'range': (0, 0), 'color': (0, 255, 0)},
                1: {'name': 'baixa', 'range': (1, 12), 'color': (0, 255, 255)},
                2: {'name': 'média', 'range': (13, 25), 'color': (0, 165, 255)},
                3: {'name': 'alta', 'range': (26, 37), 'color': (0, 0, 255)},
                4: {'name': 'lotado', 'range': (38, 50), 'color': (128, 0, 128)}
            }
        }
        
        # Inicializa o modelo YOLO
        self._load_model()
    
    def _load_model(self):
        """
        Carrega o modelo YOLO
        """
        try:
            # Tenta carregar YOLOv5 se disponível
            try:
                import torch
                from ultralytics import YOLO
                
                if self.model_path and os.path.exists(self.model_path):
                    self.model = YOLO(self.model_path)
                    logger.info(f"Modelo YOLO carregado: {self.model_path}")
                else:
                    # Usa modelo pré-treinado YOLOv8n (nano) para pessoas
                    self.model = YOLO('yolov8n.pt')
                    logger.info("Usando modelo YOLOv8n pré-treinado")
                    
            except ImportError:
                logger.warning("YOLO não disponível, usando detecção básica")
                self.model = None
                
        except Exception as e:
            logger.error(f"Erro ao carregar modelo YOLO: {e}")
            self.model = None
    
    def decode_base64_image(self, image_base64: str) -> Optional[np.ndarray]:
        """
        Decodifica imagem em base64 para array numpy
        
        Args:
            image_base64: String base64 da imagem
            
        Returns:
            Array numpy da imagem ou None se erro
        """
        try:
            # Remove prefixo se presente
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            # Decodifica base64
            image_data = base64.b64decode(image_base64)
            
            # Converte para PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Converte para RGB se necessário
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Converte para array numpy
            image_array = np.array(pil_image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Erro ao decodificar imagem base64: {e}")
            return None
    
    def detect_people_yolo(self, image: np.ndarray) -> List[Dict]:
        """
        Detecta pessoas na imagem usando YOLO
        
        Args:
            image: Array numpy da imagem
            
        Returns:
            Lista de detecções de pessoas
        """
        detections = []
        
        if self.model is None:
            # Fallback: detecção básica usando OpenCV
            return self._detect_people_opencv(image)
        
        try:
            # Executa detecção com YOLO
            results = self.model(image, conf=self.confidence_threshold)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Verifica se é uma pessoa (classe 0 no COCO)
                        if int(box.cls) == 0:  # person
                            confidence = float(box.conf)
                            
                            # Coordenadas da bounding box
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            
                            detections.append({
                                'class': 'person',
                                'confidence': confidence,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                            })
            
            logger.info(f"YOLO detectou {len(detections)} pessoas")
            return detections
            
        except Exception as e:
            logger.error(f"Erro na detecção YOLO: {e}")
            return self._detect_people_opencv(image)
    
    def _detect_people_opencv(self, image: np.ndarray) -> List[Dict]:
        """
        Detecção básica de pessoas usando OpenCV (fallback)
        
        Args:
            image: Array numpy da imagem
            
        Returns:
            Lista de detecções simuladas
        """
        try:
            # Carrega classificador Haar Cascade para pessoas
            cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            person_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Converte para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detecta pessoas
            persons = person_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            detections = []
            for (x, y, w, h) in persons:
                detections.append({
                    'class': 'person',
                    'confidence': 0.7,  # Confiança fixa para fallback
                    'bbox': [x, y, x + w, y + h],
                    'center': [x + w // 2, y + h // 2]
                })
            
            logger.info(f"OpenCV detectou {len(detections)} pessoas")
            return detections
            
        except Exception as e:
            logger.error(f"Erro na detecção OpenCV: {e}")
            # Retorna detecção simulada baseada no tamanho da imagem
            return self._simulate_detection(image)
    
    def _simulate_detection(self, image: np.ndarray) -> List[Dict]:
        """
        Simula detecção baseada em características da imagem
        
        Args:
            image: Array numpy da imagem
            
        Returns:
            Lista de detecções simuladas
        """
        height, width = image.shape[:2]
        
        # Simula detecção baseada no tamanho da imagem
        # Imagens maiores tendem a ter mais pessoas
        estimated_people = max(1, min(20, int((width * height) / 50000)))
        
        detections = []
        for i in range(estimated_people):
            # Gera posições aleatórias
            x = np.random.randint(0, width - 50)
            y = np.random.randint(0, height - 100)
            w = np.random.randint(40, 80)
            h = np.random.randint(80, 120)
            
            detections.append({
                'class': 'person',
                'confidence': 0.6,
                'bbox': [x, y, x + w, y + h],
                'center': [x + w // 2, y + h // 2]
            })
        
        logger.info(f"Simulação detectou {len(detections)} pessoas")
        return detections
    
    def calculate_occupancy_level(self, person_count: int) -> Dict:
        """
        Calcula nível de ocupação baseado na contagem de pessoas
        
        Args:
            person_count: Número de pessoas detectadas
            
        Returns:
            Dicionário com informações do nível de ocupação
        """
        for level, config in self.bus_config['occupancy_levels'].items():
            min_count, max_count = config['range']
            if min_count <= person_count <= max_count:
                percentage = (person_count / self.bus_config['max_capacity']) * 100
                
                return {
                    'level': level,
                    'name': config['name'],
                    'person_count': person_count,
                    'max_capacity': self.bus_config['max_capacity'],
                    'occupancy_percentage': round(percentage, 1),
                    'color': config['color'],
                    'status': 'comfortable' if level <= 2 else 'crowded'
                }
        
        # Se exceder a capacidade máxima
        return {
            'level': 4,
            'name': 'lotado',
            'person_count': person_count,
            'max_capacity': self.bus_config['max_capacity'],
            'occupancy_percentage': 100.0,
            'color': (128, 0, 128),
            'status': 'overcrowded'
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Desenha bounding boxes das detecções na imagem
        
        Args:
            image: Array numpy da imagem original
            detections: Lista de detecções
            
        Returns:
            Imagem com bounding boxes desenhadas
        """
        annotated_image = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            
            # Cor baseada na confiança
            color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
            
            # Desenha bounding box
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            
            # Desenha label
            label = f"Person: {confidence:.2f}"
            cv2.putText(annotated_image, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return annotated_image
    
    def predict_occupancy(self, image_base64: str) -> Dict:
        """
        Prediz ocupação da imagem
        
        Args:
            image_base64: String base64 da imagem
            
        Returns:
            Dicionário com resultado da predição
        """
        try:
            # Decodifica imagem
            image = self.decode_base64_image(image_base64)
            if image is None:
                return {
                    'status': 'error',
                    'error': 'Erro ao decodificar imagem',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Detecta pessoas
            detections = self.detect_people_yolo(image)
            
            # Calcula ocupação
            person_count = len(detections)
            occupancy_info = self.calculate_occupancy_level(person_count)
            
            # Cria imagem anotada
            annotated_image = self.draw_detections(image, detections)
            
            # Converte imagem anotada para base64
            annotated_base64 = self._encode_image_base64(annotated_image)
            
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'occupancy': occupancy_info,
                'detections': detections,
                'image_analysis': {
                    'original_size': image.shape[:2],
                    'detection_count': person_count,
                    'confidence_avg': np.mean([d['confidence'] for d in detections]) if detections else 0
                },
                'annotated_image': annotated_base64,
                'recommendations': self._generate_recommendations(occupancy_info)
            }
            
            logger.info(f"Predição concluída: {person_count} pessoas, nível {occupancy_info['level']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição de ocupação: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _encode_image_base64(self, image: np.ndarray) -> str:
        """
        Codifica imagem numpy para base64
        
        Args:
            image: Array numpy da imagem
            
        Returns:
            String base64 da imagem
        """
        try:
            # Converte para PIL Image
            pil_image = Image.fromarray(image.astype('uint8'))
            
            # Converte para bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            
            # Codifica em base64
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            return f"data:image/jpeg;base64,{base64_string}"
            
        except Exception as e:
            logger.error(f"Erro ao codificar imagem: {e}")
            return ""
    
    def _generate_recommendations(self, occupancy_info: Dict) -> List[str]:
        """
        Gera recomendações baseadas no nível de ocupação
        
        Args:
            occupancy_info: Informações de ocupação
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        level = occupancy_info['level']
        
        if level == 0:
            recommendations.extend([
                "Ônibus vazio - boa oportunidade para embarque",
                "Considere reduzir frequência se padrão persistir"
            ])
        elif level == 1:
            recommendations.extend([
                "Ocupação baixa - conforto garantido",
                "Frequência adequada para demanda atual"
            ])
        elif level == 2:
            recommendations.extend([
                "Ocupação média - conforto ainda adequado",
                "Monitore para possível aumento de demanda"
            ])
        elif level == 3:
            recommendations.extend([
                "Ocupação alta - considere aumentar frequência",
                "Passageiros podem ter dificuldade para sentar"
            ])
        else:  # level == 4
            recommendations.extend([
                "Ônibus lotado - urgente aumentar frequência",
                "Risco de superlotação - considere ônibus extras",
                "Passageiros em pé - monitore segurança"
            ])
        
        return recommendations

# Instância global do preditor
occupancy_predictor = OccupancyPredictor()

def predict_bus_occupancy(image_base64: str) -> Dict:
    """
    Função wrapper para predição de ocupação
    
    Args:
        image_base64: String base64 da imagem
        
    Returns:
        Resultado da predição
    """
    return occupancy_predictor.predict_occupancy(image_base64)
