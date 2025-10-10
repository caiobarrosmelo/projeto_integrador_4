"""
Script de teste para a API de localização
Simula requisições do ESP32 para testar o funcionamento
Baseado nos requisitos do projeto IoT
"""

import requests
import json
import time
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:3000"

def test_health_check():
    """Testa o endpoint de health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_project_info():
    """Testa informações do projeto"""
    print("\n📋 Testando informações do projeto...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_location_endpoint():
    """Testa o endpoint de localização"""
    print("\n🚌 Testando endpoint de localização...")
    
    # Dados simulados do ESP32 (conforme requisitos)
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
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro no teste de localização: {e}")
        return False

def test_destinations():
    """Testa endpoint de destinos"""
    print("\n🎯 Testando endpoint de destinos...")
    try:
        response = requests.get(f"{BASE_URL}/api/location/destinations")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simulate_esp32_data():
    """Simula múltiplas requisições do ESP32"""
    print("\n🔄 Simulando dados do ESP32...")
    
    # Coordenadas simulando movimento do ônibus em Recife
    coordinates = [
        (-8.0630, -34.8710),  # Terminal Central
        (-8.0625, -34.8705),  # Movimento 1
        (-8.0620, -34.8700),  # Movimento 2
        (-8.0615, -34.8695),  # Movimento 3
        (-8.0610, -34.8690),  # Movimento 4
    ]
    
    for i, (lat, lon) in enumerate(coordinates):
        print(f"\n📍 Enviando localização {i+1}/5...")
        
        test_data = {
            "bus_line": "L1",
            "latitude": lat,
            "longitude": lon,
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
                eta = data.get('eta', {})
                destination = data.get('destination', {})
                
                print(f"✅ ETA: {eta.get('eta_minutes', 'N/A')} min")
                print(f"   Destino: {destination.get('name', 'N/A')}")
                print(f"   Confiança: {eta.get('confidence_percent', 'N/A')}%")
                print(f"   Distância: {eta.get('distance_km', 'N/A')} km")
                print(f"   Intervalo adaptativo: {data.get('adaptive_interval_seconds', 'N/A')}s")
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Aguarda 2 segundos entre requisições
        time.sleep(2)

def main():
    """Função principal de teste"""
    print("🧪 Iniciando testes da API de monitoramento IoT...")
    print("=" * 60)
    
    # Testa se o servidor está rodando
    if not test_health_check():
        print("\n❌ Servidor não está rodando. Execute: python main.py")
        return
    
    # Executa testes
    tests = [
        test_project_info,
        test_destinations,
        test_location_endpoint,
        simulate_esp32_data
    ]
    
    for test in tests:
        try:
            test()
        except KeyboardInterrupt:
            print("\n⏹️ Testes interrompidos pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
