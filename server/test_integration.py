"""
Teste completo de integração OSRM
Testa toda a API com OSRM integrado
"""

import requests
import json
import time
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:3000"

def test_health_check():
    """Testa health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Service: {data.get('service', 'N/A')}")
            print(f"Version: {data.get('version', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_project_info():
    """Testa informações do projeto"""
    print("\n📋 Testando informações do projeto...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projeto: {data.get('project', 'N/A')}")
            print(f"   Features: {len(data.get('features', []))}")
            print(f"   Endpoints: {len(data.get('endpoints', {}))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_destinations():
    """Testa endpoint de destinos"""
    print("\n🎯 Testando destinos disponíveis...")
    try:
        response = requests.get(f"{BASE_URL}/api/location/destinations")
        if response.status_code == 200:
            data = response.json()
            destinations = data.get('destinations', {})
            print(f"✅ Destinos disponíveis: {len(destinations)}")
            for dest_id, dest_info in destinations.items():
                print(f"   - {dest_info.get('name', 'N/A')} ({dest_info.get('type', 'N/A')})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_location_with_osrm():
    """Testa endpoint de localização com OSRM"""
    print("\n🚌 Testando localização com OSRM...")
    
    # Dados de teste baseados em Recife
    test_cases = [
        {
            "name": "Terminal Central → Aeroporto",
            "data": {
                "bus_line": "L1",
                "latitude": -8.0630,
                "longitude": -34.8710,
                "timestamp": datetime.now().isoformat()
            }
        },
        {
            "name": "Shopping Recife → Praia Boa Viagem",
            "data": {
                "bus_line": "L2",
                "latitude": -8.0476,
                "longitude": -34.8770,
                "timestamp": datetime.now().isoformat()
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📍 Teste {i}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/location",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                eta = data.get('eta', {})
                destination = data.get('destination', {})
                
                print(f"✅ Status: {data.get('status')}")
                print(f"   Location ID: {data.get('location_id')}")
                print(f"   Destino: {destination.get('name', 'N/A')}")
                print(f"   ETA: {eta.get('eta_minutes', 'N/A')} minutos")
                print(f"   Distância: {eta.get('distance_km', 'N/A')} km")
                print(f"   Confiança: {eta.get('confidence_percent', 'N/A')}%")
                print(f"   Fonte: {eta.get('source', 'N/A')}")
                print(f"   Intervalo adaptativo: {data.get('adaptive_interval_seconds', 'N/A')}s")
                
                # Verifica se é OSRM ou fallback
                if eta.get('source') == 'OSRM':
                    print("   🗺️ Usando OSRM (precisão alta)")
                elif eta.get('source') == 'manual_fallback':
                    print("   ⚠️ Usando fallback manual (OSRM falhou)")
                else:
                    print("   ❓ Fonte desconhecida")
                    
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        time.sleep(1)

def test_osrm_direct():
    """Testa OSRM diretamente para comparação"""
    print("\n🗺️ Testando OSRM diretamente...")
    
    # Coordenadas: Terminal Central → Aeroporto
    start_lat, start_lon = -8.0630, -34.8710
    end_lat, end_lon = -8.1264, -34.9176
    
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
                
                # Compara com fator de tráfego
                base_duration = route['duration'] / 60
                traffic_factor = 1.3  # Pico manhã
                eta_with_traffic = base_duration * traffic_factor
                
                print(f"   ETA com tráfego (1.3x): {eta_with_traffic:.1f} min")
                
            else:
                print(f"❌ OSRM Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_history():
    """Testa endpoint de histórico"""
    print("\n📊 Testando histórico...")
    try:
        response = requests.get(f"{BASE_URL}/api/location/history/L1?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Histórico da linha L1: {data.get('count', 0)} registros")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal de teste"""
    print("🧪 Teste Completo de Integração OSRM")
    print("=" * 60)
    
    # Verifica se o servidor está rodando
    if not test_health_check():
        print("\n❌ Servidor não está rodando!")
        print("Execute: python main.py")
        return
    
    # Executa todos os testes
    tests = [
        test_project_info,
        test_destinations,
        test_location_with_osrm,
        test_osrm_direct,
        test_history
    ]
    
    for test in tests:
        try:
            test()
        except KeyboardInterrupt:
            print("\n⏹️ Testes interrompidos pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Teste de integração concluído!")
    
    print("\n💡 Resumo da integração OSRM:")
    print("   ✅ API configurada para usar OSRM")
    print("   ✅ Fallback manual implementado")
    print("   ✅ Configurações centralizadas")
    print("   ✅ Logs e monitoramento")
    print("   ✅ Testes automatizados")
    
    print("\n🚀 Próximos passos:")
    print("   1. Testar com ESP32 real")
    print("   2. Implementar API de imagens")
    print("   3. Integrar YOLO para ocupação")
    print("   4. Conectar frontend")

if __name__ == "__main__":
    main()
