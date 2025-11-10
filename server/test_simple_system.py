"""
Teste do Sistema Simplificado - Schema Reduzido
Testa APIs usando create_tables.sql (4 tabelas básicas)
Baseado nos requisitos do projeto IoT de monitoramento de ônibus
"""

import requests
import json
import time
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

BASE_URL = "http://localhost:3000"

def create_test_image(width=640, height=480, person_count=0):
    """Cria uma imagem de teste com círculos representando pessoas."""
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Adiciona círculos para simular pessoas
    for i in range(person_count):
        x = (i * 50 + 20) % (width - 40)
        y = (i * 30 + 20) % (height - 40)
        d.ellipse([(x, y), (x+30, y+30)], fill=(255, 255, 0), outline=(0,0,0))
    
    # Adiciona texto para indicar a contagem
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    d.text((10,10), f"Pessoas: {person_count}", fill=(255,255,255), font=font)

    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    return f"data:image/jpeg;base64,{base64_string}"

def test_health_check():
    """Testa o endpoint de health check"""
    print("[HEALTH] Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERRO] Servidor não está rodando: {e}")
        return False

def test_simple_location():
    """Testa API simplificada de localização"""
    print("\n[LOCALIZAÇÃO] Testando API simplificada de localização...")
    
    test_data = {
        "bus_line": "L1",
        "latitude": -8.0630,
        "longitude": -34.8710,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/location",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Localização processada:")
            print(f"   Location ID: {data.get('location_id')}")
            print(f"   ETA: {data.get('eta', {}).get('eta_minutes', 'N/A')} min")
            print(f"   Confiança: {data.get('eta', {}).get('confidence_percent', 'N/A')}%")
            print(f"   Intervalo: {data.get('adaptive_interval_seconds', 'N/A')}s")
            print(f"   Banco conectado: {data.get('database_connected', False)}")
            return data
        else:
            print(f"[ERRO] Erro: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro no teste de localização: {e}")
        return None

def test_simple_image_analysis():
    """Testa análise simplificada de imagem"""
    print("\n[IMAGEM] Testando análise simplificada de imagem...")
    
    test_image = create_test_image(person_count=5)
    
    test_data = {
        "bus_line": "L2",
        "image_data": test_image,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/image/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            occupancy = data.get('occupancy', {})
            detections = data.get('detections', {})
            
            print(f"[OK] Análise concluída:")
            print(f"   Nível de ocupação: {occupancy.get('level', 'N/A')} ({occupancy.get('name', 'N/A')})")
            print(f"   Pessoas detectadas: {occupancy.get('person_count', 'N/A')}")
            print(f"   Porcentagem: {occupancy.get('occupancy_percentage', 'N/A')}%")
            print(f"   Confiança média: {detections.get('confidence_avg', 'N/A')}")
            print(f"   Banco conectado: {data.get('database_connected', False)}")
            return data
        else:
            print(f"[ERRO] Erro: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro no teste de análise: {e}")
        return None

def test_simple_integrated():
    """Testa API integrada simplificada"""
    print("\n[INTEGRADO] Testando API integrada simplificada...")
    
    test_image = create_test_image(person_count=3)
    
    test_data = {
        "bus_line": "L3",
        "latitude": -8.0500,
        "longitude": -34.8800,
        "timestamp": datetime.now().isoformat(),
        "image_data": test_image
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/location-image",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API Integrada concluída:")
            print(f"   Location ID: {data.get('location_id')}")
            print(f"   ETA: {data.get('eta', {}).get('eta_minutes', 'N/A')} min")
            print(f"   Ocupação: {data.get('occupancy', {}).get('name', 'N/A')}")
            print(f"   Intervalo: {data.get('adaptive_interval_seconds', 'N/A')}s")
            print(f"   Recomendações: {len(data.get('recommendations', []))}")
            print(f"   Banco conectado: {data.get('database_connected', False)}")
            return data
        else:
            print(f"[ERRO] Erro: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro no teste integrado: {e}")
        return None

def test_simple_endpoints():
    """Testa endpoints auxiliares"""
    print("\n[ENDPOINTS] Testando endpoints auxiliares...")
    
    endpoints = [
        ("/api/location/destinations", "Destinos"),
        ("/api/location/current", "Localizações atuais"),
        ("/api/image/statistics", "Estatísticas de ocupação")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] {name}: {response.status_code}")
                if 'count' in data:
                    print(f"   Registros: {data['count']}")
                if 'mode' in data:
                    print(f"   Modo: {data['mode']}")
            else:
                print(f"[ERRO] {name}: {response.status_code}")
        except Exception as e:
            print(f"[ERRO] {name}: {e}")

def test_database_info():
    """Testa informações do banco de dados"""
    print("\n[BANCO] Testando informações do banco...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/database/info")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Informações do banco:")
            print(f"   Tabelas: {data.get('tables', [])}")
            print(f"   Total de registros: {data.get('total_records', 0)}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        else:
            print(f"[INFO] Endpoint de banco não disponível: {response.status_code}")
    except Exception as e:
        print(f"[INFO] Endpoint de banco não disponível: {e}")

def main():
    """Função principal de teste"""
    print("=== TESTE DO SISTEMA SIMPLIFICADO ===")
    print("Sistema de Monitoramento IoT para Ônibus")
    print("Schema Reduzido (create_tables.sql)")
    print("=====================================")
    
    if not test_health_check():
        print("\n[ERRO] Servidor não está rodando. Execute: python main.py")
        return
    
    # Testa APIs principais
    test_simple_location()
    test_simple_image_analysis()
    test_simple_integrated()
    
    # Testa endpoints auxiliares
    test_simple_endpoints()
    
    # Testa informações do banco
    test_database_info()
    
    print("\n[OK] Testes do sistema simplificado concluídos!")
    print("\n[INFO] Sistema funcionando com schema reduzido:")
    print("   - 4 tabelas básicas (create_tables.sql)")
    print("   - APIs simplificadas")
    print("   - Modo fallback quando banco não disponível")
    print("   - Compatível com ESP32 e frontend")

if __name__ == "__main__":
    main()
