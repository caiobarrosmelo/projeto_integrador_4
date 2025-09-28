"""
Teste simples para verificar se OSRM está funcionando
"""

import requests
import json

def test_osrm_simple():
    """Teste simples do OSRM"""
    print("🗺️ Testando OSRM...")
    
    # Coordenadas: Terminal Central → Aeroporto (Recife)
    start_lat, start_lon = -8.0630, -34.8710  # Terminal Central
    end_lat, end_lon = -8.1264, -34.9176      # Aeroporto
    
    # Formato OSRM: longitude,latitude;longitude,latitude
    coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
    
    try:
        response = requests.get(url, params={'overview': 'false'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                
                print(f"✅ OSRM funcionando!")
                print(f"   Distância: {route['distance']/1000:.2f} km")
                print(f"   Duração: {route['duration']/60:.1f} minutos")
                print(f"   Status: {data['code']}")
                
                # Calcula ETA com fator de tráfego
                base_duration = route['duration'] / 60  # em minutos
                traffic_factor = 1.3  # Pico manhã
                eta_minutes = base_duration * traffic_factor
                
                print(f"\n📊 Cálculo de ETA:")
                print(f"   ETA Base: {base_duration:.1f} min")
                print(f"   Fator Tráfego: {traffic_factor}")
                print(f"   ETA Final: {eta_minutes:.1f} min")
                
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

def test_google_maps_comparison():
    """Compara com Google Maps (manual)"""
    print("\n🗺️ Comparação com Google Maps:")
    print("   Terminal Central → Aeroporto (Recife)")
    print("   Google Maps: ~15-20 minutos (sem tráfego)")
    print("   Google Maps: ~25-30 minutos (com tráfego)")
    print("   OSRM: ~13.8 minutos (base)")

if __name__ == "__main__":
    print("🧪 Teste Simples - OSRM vs Cálculo Manual")
    print("=" * 50)
    
    if test_osrm_simple():
        test_google_maps_comparison()
        
        print("\n💡 Vantagens do OSRM:")
        print("   ✅ Mais preciso que distância em linha reta")
        print("   ✅ Considera vias reais, semáforos, curvas")
        print("   ✅ Gratuito e confiável")
        print("   ✅ Atualizado com OpenStreetMap")
        print("   ✅ API simples e rápida")
        
        print("\n📈 Próximos passos:")
        print("   1. Integrar OSRM na API")
        print("   2. Adicionar histórico da linha")
        print("   3. Implementar fallback manual")
        print("   4. Testar com dados reais do ESP32")
    
    print("\n✅ Teste concluído!")
