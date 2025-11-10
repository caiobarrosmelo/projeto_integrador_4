"""
Script de teste simplificado para o sistema de Machine Learning
Testa análise de ocupação e API integrada
"""

import requests
import json
import time
import base64
import io
from datetime import datetime
from PIL import Image, ImageDraw
import numpy as np

# URL base da API
BASE_URL = "http://localhost:3000"

def create_test_image(width=640, height=480, person_count=5):
    """Cria uma imagem de teste simulando pessoas no ônibus"""
    # Cria imagem em branco
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Desenha algumas pessoas como retângulos
    for i in range(person_count):
        # Posição aleatória
        x = np.random.randint(50, width - 100)
        y = np.random.randint(50, height - 150)
        w = np.random.randint(30, 60)
        h = np.random.randint(80, 120)
        
        # Desenha pessoa (retângulo)
        draw.rectangle([x, y, x + w, y + h], fill='blue', outline='darkblue', width=2)
        
        # Adiciona cabeça (círculo)
        head_size = w // 3
        draw.ellipse([x + w//2 - head_size//2, y - head_size, 
                     x + w//2 + head_size//2, y], fill='pink', outline='darkblue')
    
    # Converte para base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    image_bytes = buffer.getvalue()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    return f"data:image/jpeg;base64,{base64_string}"

def test_health_check():
    """Testa health check"""
    print("[HEALTH] Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Servidor funcionando: {data.get('service', 'N/A')}")
            return True
        else:
            print(f"[ERRO] Servidor com problema: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Servidor não está rodando: {e}")
        return False

def test_image_analysis():
    """Testa análise de imagem"""
    print("\n[IMAGEM] Testando análise de imagem...")
    
    # Cria imagem de teste com 8 pessoas
    test_image = create_test_image(person_count=8)
    
    test_data = {
        "bus_line": "L1",
        "image_data": test_image,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/image/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            occupancy = data.get('occupancy', {})
            detections = data.get('detections', {})
            
            print(f"[OK] Análise concluída:")
            print(f"   Nível de ocupação: {occupancy.get('level', 'N/A')} ({occupancy.get('name', 'N/A')})")
            print(f"   Pessoas detectadas: {occupancy.get('person_count', 'N/A')}")
            print(f"   Porcentagem: {occupancy.get('occupancy_percentage', 'N/A')}%")
            print(f"   Confiança média: {detections.get('confidence_avg', 'N/A')}")
            
            return data
        else:
            print(f"[ERRO] Erro: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro no teste de análise: {e}")
        return None

def test_integrated_api():
    """Testa API integrada (localização + imagem)"""
    print("\n[INTEGRADO] Testando API integrada...")
    
    # Cria imagem de teste
    test_image = create_test_image(person_count=12)
    
    test_data = {
        "bus_line": "L1",
        "latitude": -8.0630,
        "longitude": -34.8710,
        "image_data": test_image,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/location-image",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            occupancy = data.get('occupancy', {})
            eta = data.get('eta', {})
            traffic = data.get('traffic', {})
            
            print(f"[OK] Análise integrada concluída:")
            print(f"   Localização: {data.get('location', {}).get('destination', {}).get('name', 'N/A')}")
            print(f"   Ocupação: {occupancy.get('level', 'N/A')} ({occupancy.get('name', 'N/A')})")
            print(f"   ETA: {eta.get('eta_minutes', 'N/A')} min")
            print(f"   Confiança ETA: {eta.get('confidence_percent', 'N/A')}%")
            print(f"   Tráfego: {traffic.get('level', 'N/A')} (fator: {traffic.get('factor', 'N/A')})")
            print(f"   Intervalo adaptativo: {data.get('adaptive_interval_seconds', 'N/A')}s")
            
            return data
        else:
            print(f"[ERRO] Erro: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro no teste integrado: {e}")
        return None

def test_occupancy_history():
    """Testa histórico de ocupação"""
    print("\n[HISTORICO] Testando histórico de ocupação...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/image/occupancy/L1")
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            history = data.get('occupancy_history', [])
            summary = data.get('summary', {})
            
            print(f"[OK] Histórico obtido:")
            print(f"   Total de análises: {data.get('count', 'N/A')}")
            print(f"   Nível médio: {summary.get('avg_occupancy_level', 'N/A')}")
            print(f"   Nível máximo: {summary.get('max_occupancy_level', 'N/A')}")
            
            return data
        else:
            print(f"[ERRO] Erro: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro no teste de histórico: {e}")
        return None

def main():
    """Função principal de teste"""
    print("=== TESTE DO SISTEMA DE MACHINE LEARNING ===")
    print("Sistema de Monitoramento IoT para Onibus")
    print("=" * 50)
    
    # Verifica se o servidor está rodando
    if not test_health_check():
        print("\n[ERRO] Servidor não está rodando. Execute: python main.py")
        return
    
    # Executa testes
    tests = [
        ("Análise de Imagem", test_image_analysis),
        ("API Integrada", test_integrated_api),
        ("Histórico de Ocupação", test_occupancy_history)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n--- {test_name} ---")
            test_func()
        except KeyboardInterrupt:
            print(f"\n[INTERROMPIDO] Teste '{test_name}' interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n[ERRO] Erro inesperado em '{test_name}': {e}")
    
    print("\n=== TESTES CONCLUIDOS ===")
    print("Recursos testados:")
    print("  - Detecção de ocupação com YOLO")
    print("  - Cálculo de ETA com impacto de ocupação")
    print("  - Sistema de confiança baseado em ML")
    print("  - Intervalos adaptativos inteligentes")
    print("  - Análise integrada de localização e imagem")

if __name__ == "__main__":
    main()
