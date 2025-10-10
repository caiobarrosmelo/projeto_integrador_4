# Guia de Integração Completa
## Sistema de Monitoramento IoT para Ônibus

Este documento descreve a integração completa entre Front-end, Back-end, Banco de Dados e APIs do sistema de monitoramento de ônibus.

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FRONT-END     │    │   BACK-END       │    │   BANCO DE      │
│   (Next.js)     │◄──►│   (Flask)        │◄──►│   DADOS         │
│                 │    │                  │    │   (PostgreSQL)  │
│ • Dashboard     │    │ • APIs REST      │    │                 │
│ • Componentes   │    │ • ML/YOLO        │    │ • Localizações  │
│ • Hooks         │    │ • ETA/Confiança  │    │ • Imagens       │
│ • Estado        │    │ • Integração     │    │ • Análises      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ESP32         │    │   SISTEMA ML     │    │   MONITORAMENTO │
│                 │    │                  │    │                 │
│ • GPS           │    │ • YOLO           │    │ • Logs          │
│ • Câmera        │    │ • ETA Confidence │    │ • Métricas      │
│ • WiFi          │    │ • Occupancy      │    │ • Alertas       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Estrutura de Arquivos

```
projeto_integrador_4/
├── client/                          # Front-end (Next.js)
│   ├── app/
│   │   ├── page.tsx                 # Página principal
│   │   └── dashboard/
│   │       └── page.tsx             # Dashboard integrado
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── BusCard.tsx          # Card de ônibus
│   │   │   └── SystemMetrics.tsx    # Métricas do sistema
│   │   └── ui/                      # Componentes UI
│   └── lib/
│       └── api.ts                   # Cliente API
├── server/                          # Back-end (Flask)
│   ├── api/
│   │   ├── dashboard_api.py         # API do dashboard
│   │   ├── receive_image.py         # API de imagens
│   │   ├── integrated_location_image.py # API integrada
│   │   └── utils.py                 # Utilitários
│   ├── database/
│   │   └── connection.py            # Conexão com banco
│   ├── ml/
│   │   ├── occupancy_predictor.py   # Preditor de ocupação
│   │   └── eta_confidence.py        # Confiança de ETA
│   ├── db/
│   │   └── complete_schema.sql      # Schema do banco
│   ├── main.py                      # Servidor principal
│   └── test_integration.py          # Testes de integração
└── INTEGRATION_GUIDE.md             # Este arquivo
```

## 🚀 Instalação e Configuração

### 1. Back-end (Flask)

```bash
cd server

# Instalar dependências básicas
pip install flask flask-cors opencv-python Pillow numpy requests

# Instalar dependências completas (com YOLO)
pip install -r requirements_ml.txt

# Configurar banco de dados (opcional)
# 1. Instalar PostgreSQL
# 2. Criar banco 'bus_monitoring'
# 3. Executar schema: psql -d bus_monitoring -f db/complete_schema.sql

# Executar servidor
python main.py
```

### 2. Front-end (Next.js)

```bash
cd client

# Instalar dependências
npm install

# Configurar variáveis de ambiente
# Criar arquivo .env.local com:
# NEXT_PUBLIC_API_URL=http://localhost:3000

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build
npm start
```

### 3. Banco de Dados (PostgreSQL)

```bash
# Instalar PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Windows: Baixar do site oficial
# macOS: brew install postgresql

# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE bus_monitoring;
CREATE USER bus_user WITH PASSWORD 'bus_password';
GRANT ALL PRIVILEGES ON DATABASE bus_monitoring TO bus_user;
\q

# Executar schema
psql -h localhost -U bus_user -d bus_monitoring -f server/db/complete_schema.sql
```

## 🔧 Configuração das APIs

### Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check principal |
| `/api/health` | GET | Health check da API |
| `/api/dashboard/data` | GET | Dados completos do dashboard |
| `/api/dashboard/buses` | GET | Ônibus ativos |
| `/api/dashboard/occupancy` | GET | Dados de ocupação |
| `/api/dashboard/metrics` | GET | Métricas do sistema |
| `/api/location` | POST | Enviar localização GPS |
| `/api/image/analyze` | POST | Analisar imagem |
| `/api/location-image` | POST | API integrada (GPS + Imagem) |
| `/api/integrated/status/<line>` | GET | Status integrado por linha |

### Configuração do CORS

```python
# server/config.py
CORS_CONFIG = {
    'origins': [
        'http://localhost:3000',    # Next.js dev
        'http://localhost:3001',    # Next.js alt
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001'
    ],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization']
}
```

## 📊 Fluxo de Dados

### 1. Dados do ESP32 → Back-end

```json
{
  "bus_line": "L1",
  "latitude": -8.0630,
  "longitude": -34.8710,
  "image_data": "data:image/jpeg;base64,/9j/4AAQ...",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Processamento no Back-end

1. **Validação**: Coordenadas GPS, formato da imagem
2. **Análise de Imagem**: YOLO detecta pessoas
3. **Cálculo de Ocupação**: Nível 0-4 baseado na contagem
4. **Cálculo de ETA**: Considerando ocupação e tráfego
5. **Confiança**: ML calcula confiança da previsão
6. **Salvamento**: Dados salvos no banco (se disponível)

### 3. Resposta para ESP32

```json
{
  "status": "success",
  "bus_line": "L1",
  "occupancy": {
    "level": 2,
    "name": "média",
    "person_count": 18,
    "confidence": 85.5
  },
  "eta": {
    "eta_minutes": 12.5,
    "confidence_percent": 78.2
  },
  "adaptive_interval_seconds": 30,
  "recommendations": [
    "Ocupação média - conforto adequado",
    "ETA: 12.5 min com boa confiança"
  ]
}
```

### 4. Front-end → Dashboard

```typescript
// client/lib/api.ts
const { data, loading, error } = useDashboardData();

// Dados recebidos:
{
  "timestamp": "2024-01-15T10:30:00",
  "system_status": {
    "database_connected": true,
    "total_active_buses": 5
  },
  "current_buses": [...],
  "occupancy_summary": {...},
  "eta_summary": {...},
  "system_metrics": {...}
}
```

## 🔄 Modos de Operação

### 1. Modo Completo (Com Banco de Dados)

- ✅ Todas as funcionalidades
- ✅ Persistência de dados
- ✅ Histórico completo
- ✅ Métricas avançadas
- ✅ Análise de tendências

### 2. Modo Fallback (Sem Banco de Dados)

- ✅ APIs funcionais
- ✅ Análise de imagens
- ✅ Cálculo de ETA
- ✅ Dashboard básico
- ❌ Sem persistência
- ❌ Dados simulados

## 🧪 Testes de Integração

### Executar Testes Completos

```bash
cd server
python test_integration.py
```

### Testes Disponíveis

1. **Health Checks**: Verifica se todas as APIs estão funcionando
2. **Dashboard API**: Testa endpoints do dashboard
3. **Workflow Integrado**: Simula fluxo completo ESP32 → API → Resposta
4. **Endpoints da API**: Testa todos os endpoints disponíveis
5. **Integração com Banco**: Verifica conexão e operações
6. **Integração com Front-end**: Valida estrutura de dados

### Exemplo de Saída

```
=== TESTE DE INTEGRAÇÃO COMPLETA ===
✅ Health Checks: PASSOU
✅ API do Dashboard: PASSOU
✅ Workflow Integrado: PASSOU
✅ Endpoints da API: PASSOU
✅ Integração com Banco: PASSOU
✅ Integração com Front-end: PASSOU

Total: 6/6 testes passaram
🎉 TODOS OS TESTES PASSARAM!
```

## 📱 Uso do Front-end

### 1. Dashboard Principal

```typescript
// Acesse: http://localhost:3001/dashboard
// Funcionalidades:
// - Visão geral do sistema
// - Ônibus em tempo real
// - Análise de ocupação
// - Métricas do sistema
```

### 2. Componentes Disponíveis

```typescript
// BusCard - Card de ônibus individual
<BusCard bus={busData} showDetails={true} />

// SystemMetrics - Métricas do sistema
<SystemMetricsComponent 
  metrics={systemMetrics}
  databaseInfo={dbInfo}
  isConnected={true}
/>

// Hooks personalizados
const { data, loading, error } = useDashboardData();
const { data: buses } = useCurrentBuses('L1');
const { data: occupancy } = useOccupancyData();
```

### 3. Atualização Automática

```typescript
// Atualização automática configurada:
// - Dashboard: 30 segundos
// - Ônibus: 30 segundos  
// - Métricas: 60 segundos
// - Manual: Botão "Atualizar"
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Servidor não inicia
```bash
# Verificar dependências
pip install flask flask-cors

# Verificar porta
# Padrão: http://localhost:3000
```

#### 2. Front-end não conecta
```bash
# Verificar CORS
# Verificar URL da API
# Verificar se servidor está rodando
```

#### 3. Banco de dados não conecta
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar credenciais
# Modo fallback será ativado automaticamente
```

#### 4. YOLO não funciona
```bash
# Instalar dependências ML
pip install ultralytics torch

# Sistema usará fallback automaticamente
```

### Logs e Debug

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs do sistema
tail -f server.log
```

## 📈 Monitoramento

### Métricas Disponíveis

- **Requisições**: Total por dia, tempo médio de resposta
- **Erros**: Taxa de erro, tipos de erro
- **Sistema**: CPU, memória, conexões ativas
- **Banco**: Tabelas, registros, pool de conexões
- **ML**: Precisão das detecções, confiança média

### Alertas

- Taxa de erro > 5%
- Tempo de resposta > 1s
- Uso de memória > 80%
- Banco desconectado
- YOLO não disponível

## 🚀 Deploy

### Desenvolvimento

```bash
# Back-end
cd server
python main.py

# Front-end
cd client
npm run dev
```

### Produção

```bash
# Back-end
cd server
gunicorn -w 4 -b 0.0.0.0:3000 main:app

# Front-end
cd client
npm run build
npm start
```

### Docker (Opcional)

```dockerfile
# Dockerfile para back-end
FROM python:3.9
COPY server/ /app
WORKDIR /app
RUN pip install -r requirements_ml.txt
EXPOSE 3000
CMD ["python", "main.py"]
```

## 📚 Recursos Adicionais

### Documentação

- [README_ML.md](server/README_ML.md) - Sistema de Machine Learning
- [complete_schema.sql](server/db/complete_schema.sql) - Schema do banco
- [requirements_ml.txt](server/requirements_ml.txt) - Dependências ML

### APIs

- [Dashboard API](server/api/dashboard_api.py) - API do dashboard
- [Image API](server/api/receive_image.py) - API de imagens
- [Integrated API](server/api/integrated_location_image.py) - API integrada

### Front-end

- [API Client](client/lib/api.ts) - Cliente API
- [Dashboard](client/app/dashboard/page.tsx) - Dashboard
- [Components](client/components/dashboard/) - Componentes

---

**Desenvolvido para o Projeto Integrador - 4º Semestre ADS**  
**Sistema de Monitoramento IoT para Ônibus**
