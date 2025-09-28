# Servidor de Monitoramento IoT para Ônibus

API backend para recebimento de dados GPS do ESP32 e cálculo de ETA em tempo real, baseado nos requisitos do Projeto Integrador do 4º semestre de ADS.

## 🚀 Funcionalidades

- **Recebimento de dados GPS**: Endpoint para receber localização do ESP32 via GPRS
- **Cálculo de ETA inteligente**: Algoritmo baseado em histórico de velocidade e padrões de tráfego
- **Aprendizado de padrões de atraso**: ML que aprende padrões de atraso por linha e horário
- **Sistema de confiança**: Avalia a precisão das previsões (0-95%)
- **Intervalos adaptativos**: Ajusta frequência de requisições baseado no tráfego
- **Histórico de localizações**: Consulta de dados históricos por linha
- **Destinos dinâmicos**: Sistema de paradas e terminais configuráveis

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- Dependências Python (ver `requirements.txt`)

## 🛠️ Instalação

1. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

2. **Configure o banco PostgreSQL**:
```sql
-- Execute o script de criação das tabelas
\i db/create_tables.sql
```

3. **Configure as variáveis de ambiente** (opcional):
```bash
export DB_HOST=localhost
export DB_NAME=bus_monitoring
export DB_USER=postgres
export DB_PASSWORD=sua_senha
export API_PORT=3000
```

## 🏃‍♂️ Executando o Servidor

```bash
# Desenvolvimento
python main.py

# Produção (com gunicorn)
gunicorn -w 4 -b 0.0.0.0:3000 main:app
```

O servidor estará disponível em: `http://localhost:3000`

## 📡 Endpoints da API

### 1. Informações do Projeto
```http
GET /
```

### 2. Health Check
```http
GET /health
```

### 3. Receber Localização (ESP32)
```http
POST /api/location
Content-Type: application/json

{
  "bus_line": "L1",
  "latitude": -8.0630,
  "longitude": -34.8710,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Resposta**:
```json
{
  "status": "success",
  "location_id": 123,
  "destination": {
    "id": "terminal_central",
    "name": "Terminal Central",
    "latitude": -8.0630,
    "longitude": -34.8710,
    "type": "terminal",
    "distance_km": 0.5
  },
  "eta": {
    "eta_minutes": 15.5,
    "estimated_arrival": "2024-01-01T10:15:30Z",
    "distance_km": 5.2,
    "avg_speed_kmh": 20.1,
    "adjusted_speed_kmh": 18.5,
    "confidence_percent": 85.3,
    "traffic_factor": 0.8,
    "delay_factor": 0.95
  },
  "adaptive_interval_seconds": 25,
  "message": "Localização recebida e ETA calculado"
}
```

### 4. Histórico de Localizações
```http
GET /api/location/history/L1?limit=50&hours=24
```

### 5. Destinos Disponíveis
```http
GET /api/location/destinations
```

## 🧮 Algoritmo de ETA com OSRM

O sistema calcula ETA usando **OSRM (Open Source Routing Machine)** para máxima precisão:

1. **OSRM**: Roteamento baseado em vias reais do OpenStreetMap
2. **Distância real**: Considera vias, semáforos, curvas (não linha reta)
3. **Fator de tráfego**: Ajuste por horário do dia
4. **Aprendizado de atraso**: ML que aprende padrões históricos de atraso
5. **Fallback manual**: Cálculo manual se OSRM falhar
6. **Confiança**: 90% (OSRM) ou 60% (fallback)

### Fatores de Tráfego (Recife)
- **7h-9h**: 0.6 (pico manhã)
- **12h-14h**: 0.8 (almoço)
- **17h-19h**: 0.5 (pico tarde)
- **19h-23h**: 1.1 (noite)
- **Outros**: 1.0 (normal)

### OSRM (Open Source Routing Machine)
- **Servidor**: `http://router.project-osrm.org` (público e gratuito)
- **Precisão**: Considera vias reais, semáforos, curvas
- **Performance**: Resposta em ~100ms
- **Confiabilidade**: 90% de confiança nas previsões
- **Fallback**: Cálculo manual se OSRM falhar

### Aprendizado de Padrões de Atraso
- Analisa previsões vs chegadas reais dos últimos 7 dias
- Aprende padrões específicos por linha e horário
- Ajusta velocidade baseado em atrasos históricos
- Melhora precisão ao longo do tempo

## 🧪 Testando a API

### Teste Completo de Integração OSRM
```bash
python test_integration.py
```

### Teste Simples OSRM
```bash
python test_simple.py
```

### Teste Básico
```bash
python test_api.py
```

### Executar Servidor
```bash
python main.py  # Agora usa receive_location_osrm.py
```

### Endpoint para ESP32 (mesmo formato)
```http
POST /api/location
{
  "bus_line": "L1",
  "latitude": -8.0630,
  "longitude": -34.8710
}
```
O script irá:
- Testar health check
- Verificar informações do projeto
- Enviar dados simulados do ESP32
- Verificar destinos disponíveis
- Simular movimento do ônibus

## 📊 Estrutura do Banco

### Tabelas Principais
- `bus_location`: Localizações GPS
- `bus_image`: Imagens capturadas (para YOLO)
- `prediction_confidence`: Previsões de ETA com confiança
- `request_interval`: Intervalos adaptativos

## 🔧 Configuração

Edite `config.py` para ajustar:
- Coordenadas de destinos em Recife
- Fatores de tráfego por horário
- Configurações de ETA e ML
- Parâmetros do banco

## 📝 Logs

Logs são salvos em:
- Console (desenvolvimento)
- Arquivo `server.log` (produção)

Níveis: DEBUG, INFO, WARNING, ERROR

## 🚨 Troubleshooting

### Erro de Conexão com Banco
```bash
# Verifique se PostgreSQL está rodando
sudo systemctl status postgresql

# Teste conexão
psql -h localhost -U postgres -d bus_monitoring
```

### Porta em Uso
```bash
# Mude a porta no config.py ou use variável de ambiente
export API_PORT=3001
```

### Dependências
```bash
# Reinstale dependências
pip install -r requirements.txt --force-reinstall
```

## 🔄 Próximos Passos

1. ✅ **Implementar API de imagens** (`receive_image.py`)
2. ✅ **Integrar YOLO** para detecção de ocupação
3. ✅ **Sistema de paradas dinâmicas**
4. ✅ **Cache Redis** para performance
5. ✅ **Monitoramento com Prometheus**

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Logs do servidor
2. Status do banco de dados
3. Conectividade de rede
4. Configurações de ambiente

## 🎯 Contexto do Projeto

Este servidor faz parte do **Projeto Integrador do 4º semestre de ADS** e implementa:

- **IoT**: Coleta de dados via ESP32 + GPS + Câmera
- **Cloud Computing**: Processamento na nuvem
- **Machine Learning**: YOLO para detecção + aprendizado de padrões
- **Banco de Dados**: PostgreSQL com estrutura modular
- **APIs REST**: Integração com frontend e ESP32
- **Tempo Real**: Cálculo de ETA e intervalos adaptativos
