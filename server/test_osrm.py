"""
Script de teste para API com OSRM
Testa a precisão do cálculo de ETA usando OSRM
"""

import requests
import json
import time
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:3000"

def test_osrm_eta():
    """Testa cálculo de ETA usando OSRM"""
    print("🗺️ Testando cálculo de ETA com OSRM...")
    
    # Coordenadas reais de Recife para teste
    test_cases = [
        {
            "name": "Terminal Central → Aeroporto",
            "start": (-8.0630, -34.8710),  # Terminal Central
            "end": (-8.1264, -34.9176),    # Aeroporto
            "bus_line": "L1"
        },
        {
            "name": "Shopping Recife → Praia Boa Viagem",
            "start": (-8.0476, -34.8770),  # Shopping Recife
            "end": (-8.1196, -34.9010),    # Praia Boa Viagem
            "bus_line": "L2"
        },
        {
            "name": "UFPE → Hospital Restauração",
            "start": (-8.0476, -34.9510),  # UFPE
            "end": (-8.0630, -34.9010),    # Hospital Restauração
            "bus_line": "L3"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📍 Teste {i}: {test_case['name']}")
        
        start_lat, start_lon = test_case['start']
        end_lat, end_lon = test_case['end']
        
        # Dados para enviar
        test_data = {
            "bus_line": test_case['bus_line'],
            "latitude": start_lat,
            "longitude": start_lon,
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
                
                print(f"✅ Status: {data.get('status')}")
                print(f"   Destino: {destination.get('name', 'N/A')}")
                print(f"   ETA: {eta.get('eta_minutes', 'N/A')} minutos")
                print(f"   Distância: {eta.get('distance_km', 'N/A')} km")
                print(f"   Confiança: {eta.get('confidence_percent', 'N/A')}%")
                print(f"   Fonte: {eta.get('source', 'N/A')}")
                
                if 'base_eta_minutes' in eta:
                    print(f"   ETA Base (OSRM): {eta['base_eta_minutes']} min")
                if 'history_adjustment' in eta:
                    print(f"   Ajuste Histórico: {eta['history_adjustment']}")
                    
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Aguarda entre testes
        time.sleep(1)

def test_osrm_direct():
    """Testa OSRM diretamente para comparar"""
    print("\n🔍 Testando OSRM diretamente...")
    
    # Teste direto com OSRM
    start_lat, start_lon = -8.0630, -34.8710  # Terminal Central
    end_lat, end_lon = -8.1264, -34.9176      # Aeroporto
    
    coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
    
    try:
        response = requests.get(url, params={'overview': 'false'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                
                print(f"✅ OSRM Direto:")
                print(f"   Distância: {route['distance']/1000:.2f} km")
                print(f"   Duração: {route['duration']/60:.1f} minutos")
                print(f"   Status: {data['code']}")
            else:
                print(f"❌ OSRM Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_health_check():
    """Testa health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 Testando API com OSRM...")
    print("=" * 50)
    
    # Testa se o servidor está rodando
    if not test_health_check():
        print("\n❌ Servidor não está rodando. Execute: python main.py")
        return
    
    # Executa testes
    test_osrm_eta()
    test_osrm_direct()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
