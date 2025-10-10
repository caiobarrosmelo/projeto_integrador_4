# Sistema Simplificado de Monitoramento IoT para Ônibus

## Visão Geral

Este é o sistema simplificado do projeto de monitoramento IoT para ônibus, usando um schema de banco de dados reduzido com apenas 4 tabelas básicas (`create_tables.sql`). O sistema mantém todas as funcionalidades principais mas com uma estrutura mais simples e adequada ao escopo do projeto.

## Estrutura do Banco de Dados (Schema Reduzido)

### Tabelas Principais

1. **`bus_location`** - Localizações GPS dos ônibus
   - `id` (SERIAL PRIMARY KEY)
   - `bus_line` (VARCHAR(30)) - Linha do ônibus
   - `timestamp_location` (TIMESTAMP) - Momento da leitura
   - `latitude` (DOUBLE PRECISION) - Latitude GPS
   - `longitude` (DOUBLE PRECISION) - Longitude GPS

2. **`bus_image`** - Imagens e análise de ocupação
   - `id` (SERIAL PRIMARY KEY)
   - `location_id` (INT) - Referência à localização
   - `image_data` (BYTEA) - Dados da imagem
   - `timestamp_image` (TIMESTAMP) - Momento da captura
   - `occupancy_count` (SMALLINT) - Contagem de pessoas

3. **`request_interval`** - Intervalos adaptativos
   - `id` (SERIAL PRIMARY KEY)
   - `location_id` (INT) - Referência à localização
   - `start_time` (TIMESTAMP) - Início do intervalo
   - `end_time` (TIMESTAMP) - Fim do intervalo
   - `interval_seconds` (SMALLINT) - Intervalo em segundos

4. **`prediction_confidence`** - Previsões de ETA
   - `id` (SERIAL PRIMARY KEY)
   - `location_id` (INT) - Referência à localização
   - `predicted_arrival` (TIMESTAMP) - Previsão de chegada
   - `actual_arrival` (TIMESTAMP) - Chegada real (opcional)
   - `confidence_percent` (DECIMAL(5,2)) - Confiança da previsão
   - `timestamp_prediction` (TIMESTAMP) - Momento da previsão

## APIs Simplificadas

### 1. API de Localização (`simple_location_api.py`)

**Endpoint Principal:**
- `POST /api/location` - Recebe dados GPS do ESP32

**Endpoints Auxiliares:**
- `GET /api/location/history/<bus_line>` - Histórico de localizações
- `GET /api/location/current` - Localizações atuais
- `GET /api/location/destinations` - Lista de destinos

**Funcionalidades:**
- Validação de coordenadas GPS
- Cálculo de ETA simplificado
- Intervalos adaptativos
- Modo fallback quando banco não disponível

### 2. API de Imagens (`simple_image_api.py`)

**Endpoint Principal:**
- `POST /api/image/analyze` - Análise de ocupação com YOLO

**Endpoints Auxiliares:**
- `GET /api/image/occupancy/<bus_line>` - Histórico de ocupação
- `GET /api/image/statistics` - Estatísticas gerais

**Funcionalidades:**
- Detecção de pessoas com YOLO
- Análise de ocupação (5 níveis)
- Geração de recomendações
- Modo fallback com dados simulados

### 3. API Integrada (`simple_integrated_api.py`)

**Endpoint Principal:**
- `POST /api/location-image` - Combina GPS + imagem

**Endpoints Auxiliares:**
- `GET /api/integrated/status/<bus_line>` - Status integrado

**Funcionalidades:**
- Processamento simultâneo de GPS e imagem
- ETA com impacto de ocupação
- Intervalos adaptativos inteligentes
- Recomendações integradas

## Configuração e Instalação

### 1. Dependências Python

```bash
pip install -r requirements.txt
```

### 2. Configuração do Banco de Dados

1. **Crie o banco PostgreSQL:**
```sql
CREATE DATABASE bus_monitoring;
```

2. **Execute o schema simplificado:**
```bash
psql -U postgres -d bus_monitoring -f db/create_tables.sql
```

3. **Configure as credenciais em `config.py`:**
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'bus_monitoring',
    'user': 'postgres',
    'password': 'sua_senha',
    'port': 5432
}
```

### 3. Executar o Servidor

```bash
python main.py
```

O servidor iniciará na porta 3000 com as APIs simplificadas.

## Testando o Sistema

### 1. Teste Automatizado

```bash
python test_simple_system.py
```

### 2. Teste Manual com cURL

**Enviar localização:**
```bash
curl -X POST http://localhost:3000/api/location \
  -H "Content-Type: application/json" \
  -d '{
    "bus_line": "L1",
    "latitude": -8.0630,
    "longitude": -34.8710
  }'
```

**Analisar imagem:**
```bash
curl -X POST http://localhost:3000/api/image/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "bus_line": "L1",
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  }'
```

**API integrada:**
```bash
curl -X POST http://localhost:3000/api/location-image \
  -H "Content-Type: application/json" \
  -d '{
    "bus_line": "L1",
    "latitude": -8.0630,
    "longitude": -34.8710,
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  }'
```

## Modos de Operação

### 1. Modo Banco de Dados (`simple_database`)
- Banco PostgreSQL conectado
- Dados persistidos
- Histórico completo
- Estatísticas reais

### 2. Modo Fallback (`fallback`)
- Banco não disponível
- Dados simulados
- Funcionalidades básicas
- Ideal para desenvolvimento

## Vantagens do Sistema Simplificado

### ✅ **Simplicidade**
- Apenas 4 tabelas essenciais
- Código mais limpo e fácil de manter
- Menos complexidade de configuração

### ✅ **Compatibilidade**
- Funciona com ou sem banco de dados
- Modo fallback automático
- Ideal para desenvolvimento e testes

### ✅ **Funcionalidades Completas**
- Todas as funcionalidades principais mantidas
- Análise de ocupação com YOLO
- Cálculo de ETA inteligente
- Intervalos adaptativos

### ✅ **Performance**
- Menos joins entre tabelas
- Consultas mais rápidas
- Menor uso de recursos

## Integração com ESP32

O sistema simplificado mantém total compatibilidade com o ESP32:

```cpp
// Exemplo de envio de dados integrados
void sendLocationAndImage() {
    String jsonData = "{";
    jsonData += "\"bus_line\":\"L1\",";
    jsonData += "\"latitude\":" + String(latitude, 6) + ",";
    jsonData += "\"longitude\":" + String(longitude, 6) + ",";
    jsonData += "\"image_data\":\"" + base64Image + "\"";
    jsonData += "}";
    
    http.begin("http://localhost:3000/api/location-image");
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonData);
}
```

## Monitoramento e Logs

### Logs do Sistema
- Logs detalhados de todas as operações
- Rastreamento de erros e exceções
- Métricas de performance

### Health Checks
- `GET /health` - Status geral do sistema
- `GET /api/health` - Status das APIs
- Verificação de conectividade com banco

## Próximos Passos

1. **Configurar banco de dados** (se necessário)
2. **Testar APIs** com o script de teste
3. **Integrar com ESP32** usando os endpoints
4. **Desenvolver frontend** consumindo as APIs
5. **Monitorar logs** para ajustes finos

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs do servidor
2. Execute o script de teste
3. Consulte a documentação das APIs
4. Verifique a conectividade com o banco

---

**Sistema Simplificado - Projeto Integrador 4º Semestre ADS**
*Monitoramento IoT para Ônibus com Schema Reduzido*
