"""
Teste rápido para verificar se tudo está funcionando
"""

import requests
import time

def test_osrm_direct():
    """Testa OSRM diretamente"""
    print("🗺️ Testando OSRM diretamente...")
    
    try:
        # Coordenadas: Terminal Central → Aeroporto (Recife)
        start_lat, start_lon = -8.0630, -34.8710
        end_lat, end_lon = -8.1264, -34.9176
        
        coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
        
        response = requests.get(url, params={'overview': 'false'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                
                print(f"✅ OSRM funcionando!")
                print(f"   Distância: {route['distance']/1000:.2f} km")
                print(f"   Duração: {route['duration']/60:.1f} minutos")
                
                # Testa com fator de tráfego
                base_duration = route['duration'] / 60
                traffic_factor = 1.3  # Pico manhã
                eta_minutes = base_duration * traffic_factor
                
                print(f"   ETA com tráfego: {eta_minutes:.1f} minutos")
                return True
            else:
                print(f"❌ OSRM Error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_api_components():
    """Testa componentes da API"""
    print("\n🔧 Testando componentes da API...")
    
    try:
        # Testa importação dos módulos
        from api.eta_osrm import OSRMETA, calculate_eta_with_osrm
        from api.receive_location_osrm import location_bp
        from config import OSRM_CONFIG, DESTINATIONS
        
        print("✅ Módulos importados com sucesso")
        print(f"   OSRM Server: {OSRM_CONFIG['server_url']}")
        print(f"   Destinos: {len(DESTINATIONS)}")
        
        # Testa instância OSRM
        osrm = OSRMETA()
        print(f"   OSRM Profile: {osrm.profile}")
        print(f"   OSRM Timeout: {osrm.timeout}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_eta_calculation():
    """Testa cálculo de ETA"""
    print("\n📊 Testando cálculo de ETA...")
    
    try:
        from api.eta_osrm import calculate_eta_with_osrm
        
        # Coordenadas de teste
        start_lat, start_lon = -8.0630, -34.8710  # Terminal Central
        end_lat, end_lon = -8.1264, -34.9176      # Aeroporto
        
        result = calculate_eta_with_osrm(start_lat, start_lon, end_lat, end_lon, 1.3)
        
        if result['status'] == 'success':
            print("✅ Cálculo de ETA funcionando!")
            print(f"   ETA: {result['eta_minutes']} minutos")
            print(f"   Distância: {result['distance_km']} km")
            print(f"   Confiança: {result['confidence_percent']}%")
            print(f"   Fonte: {result['source']}")
            return True
        else:
            print(f"❌ Erro no cálculo: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste Rápido - Integração OSRM")
    print("=" * 50)
    
    tests = [
        test_osrm_direct,
        test_api_components,
        test_eta_calculation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos Testes:")
    print(f"   OSRM Direto: {'✅' if results[0] else '❌'}")
    print(f"   Componentes API: {'✅' if results[1] else '❌'}")
    print(f"   Cálculo ETA: {'✅' if results[2] else '❌'}")
    
    if all(results):
        print("\n🎉 Integração OSRM funcionando perfeitamente!")
        print("\n💡 Próximos passos:")
        print("   1. Executar servidor: python main.py")
        print("   2. Testar endpoints: python test_integration.py")
        print("   3. Integrar com ESP32")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
