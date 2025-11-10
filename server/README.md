# 🖥️ Backend - Servidor Flask

API backend para recebimento de dados GPS do ESP32 e cálculo de ETA em tempo real.

## 📋 Índice

- [Início Rápido](#-início-rápido)
- [Estrutura](#-estrutura)
- [Configuração](#-configuração)
- [APIs](#-apis)
- [Banco de Dados](#-banco-de-dados)
- [Machine Learning](#-machine-learning)

---

## ⚡ Início Rápido

```bash
# 1. Instalar dependências
pip install -r requirements_simple.txt

# 2. Executar servidor
python main.py

# 3. Testar
curl http://localhost:3000/health
```

---

## 📁 Estrutura

```
server/
├── main.py                    # ⭐ Entry point - inicia o servidor
├── config_simple.py           # Configurações centralizadas
├── env.example                 # Template de variáveis de ambiente
│
├── api/                       # Endpoints HTTP
│   ├── dashboard_api.py       # API do dashboard (frontend)
│   ├── simple_location_api.py # API de localização GPS
│   ├── simple_image_api.py    # API de análise de imagens
│   ├── simple_integrated_api.py # API integrada (GPS + Imagem)
│   └── utils.py               # Utilitários compartilhados
│
├── database/                  # Acesso a dados
│   └── simple_connection.py   # Conexão e repositórios
│
├── ml/                        # Machine Learning
│   ├── occupancy_predictor.py # Predição de ocupação (YOLO)
│   └── eta_confidence.py      # Cálculo de confiança de ETA
│
└── db/                        # Scripts SQL
    └── create_tables.sql      # Schema do banco de dados
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Copie `env.example` para `.env`:

```bash
cp env.example .env
```

Edite `.env` com suas configurações:

```env
# Banco de Dados (Opcional)
DB_HOST=localhost
DB_NAME=bus_monitoring
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_PORT=5432

# API
API_HOST=0.0.0.0
API_PORT=3000
DEBUG=True
```

### Configuração no Código

Todas as configurações estão em `config_simple.py`:

- `DATABASE_CONFIG` - Configurações do PostgreSQL
- `API_CONFIG` - Configurações do servidor Flask
- `ETA_CONFIG` - Configurações de cálculo de ETA
- `ML_CONFIG` - Configurações de Machine Learning
- `CORS_CONFIG` - Configurações de CORS

---

## 🔌 APIs

### Health Check

```http
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "service": "bus-monitoring-api",
  "version": "1.0.0"
}
```

### Receber Localização

```http
POST /api/location
Content-Type: application/json

{
  "bus_line": "L1",
  "latitude": -8.0630,
  "longitude": -34.8710,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Analisar Imagem

```http
POST /api/image/analyze
Content-Type: application/json

{
  "bus_line": "L1",
  "image_data": "data:image/jpeg;base64,..."
}
```

### API Integrada (GPS + Imagem)

```http
POST /api/location-image
Content-Type: application/json

{
  "bus_line": "L1",
  "latitude": -8.0630,
  "longitude": -34.8710,
  "image_data": "data:image/jpeg;base64,..."
}
```

### Dashboard APIs

```http
GET /api/dashboard/data        # Dados completos
GET /api/dashboard/buses       # Ônibus ativos
GET /api/dashboard/occupancy   # Dados de ocupação
GET /api/dashboard/metrics     # Métricas do sistema
```

---

## 🗄️ Banco de Dados

### Schema

O banco usa 4 tabelas principais:

1. **bus_location** - Localizações GPS
2. **bus_image** - Imagens capturadas
3. **bus_eta** - Previsões de ETA
4. **bus_interval** - Intervalos adaptativos

### Setup

```bash
# 1. Criar banco
createdb bus_monitoring

# 2. Executar schema
psql -d bus_monitoring -f db/create_tables.sql
```

### Modo Fallback

Se o banco não estiver disponível:
- Sistema continua funcionando
- Usa dados simulados
- Logs indicam "Modo Fallback"

---

## 🤖 Machine Learning

### Ocupação (YOLO)

O sistema detecta pessoas em imagens usando YOLO:

```python
from ml.occupancy_predictor import predict_bus_occupancy

result = predict_bus_occupancy(image_data)
# Retorna: level (0-4), person_count, confidence
```

### ETA Confidence

Calcula confiança das previsões de ETA:

```python
from ml.eta_confidence import calculate_eta_confidence

confidence = calculate_eta_confidence(
    distance_km=5.2,
    speed_kmh=25.0,
    occupancy_level=2
)
```

---

## 🚀 Executando

### Desenvolvimento

```bash
python main.py
```

### Produção (com Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 main:app
```

---

## 🧪 Testes

```bash
# Testar APIs
python test_simple_system.py

# Testar integração
python test_integration.py
```

---

## 📝 Logs

Logs são exibidos no console. Para salvar em arquivo:

```python
# Em config_simple.py
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'server.log'  # Salvar em arquivo
}
```

---

## 🔧 Troubleshooting

### Erro: "Module not found"

```bash
pip install -r requirements_simple.txt
```

### Erro: "Port 3000 already in use"

Mude a porta em `config_simple.py`:
```python
API_CONFIG = {
    'port': 5000  # Mudar porta
}
```

### Erro: "Database connection failed"

O sistema funciona sem banco! Se quiser usar:
1. Verifique se PostgreSQL está rodando
2. Verifique credenciais em `.env`
3. Execute `create_tables.sql`

---

## 📚 Mais Informações

- **Guia Completo**: `../GUIA_EXECUCAO_LOCAL.md`
- **Integração**: `../INTEGRATION_GUIDE.md`
- **Arquitetura**: `../ARQUITETURA.md`

---

**Pronto para usar!** 🚀
