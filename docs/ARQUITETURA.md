# 🏗️ Arquitetura do Sistema

Este documento explica como o sistema funciona internamente e como os componentes se comunicam.

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        CAMADA DE HARDWARE                    │
│  ┌──────────────┐                                           │
│  │    ESP32     │  Coleta GPS e Imagens                     │
│  │  (Arduino)   │  Envia via HTTP POST                      │
│  └──────┬───────┘                                           │
└─────────┼───────────────────────────────────────────────────┘
          │ HTTP POST
          │ JSON + Base64
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAMADA DE BACKEND                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Flask API Server                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │ Location │  │  Image   │  │Dashboard │          │  │
│  │  │   API    │  │   API    │  │   API    │          │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │  │
│  │       │            │              │                 │  │
│  │       └────────────┴──────────────┘                 │  │
│  │                    │                                  │  │
│  │  ┌─────────────────▼─────────────────┐              │  │
│  │  │      Services Layer               │              │  │
│  │  │  • Location Service               │              │  │
│  │  │  • Occupancy Service              │              │  │
│  │  │  • ETA Service                    │              │  │
│  │  └─────────────────┬─────────────────┘              │  │
│  │                    │                                  │  │
│  │  ┌─────────────────▼─────────────────┐              │  │
│  │  │   Machine Learning Layer          │              │  │
│  │  │  • YOLO (Occupancy Detection)      │              │  │
│  │  │  • ETA Confidence Calculator       │              │  │
│  │  └─────────────────┬─────────────────┘              │  │
│  └────────────────────┼──────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────────────▼────────────────────┐                │
│  │      Database Layer (PostgreSQL)        │                │
│  │  • bus_location                         │                │
│  │  • bus_image                            │                │
│  │  • bus_eta                              │                │
│  │  • bus_interval                         │                │
│  └─────────────────────────────────────────┘                │
└────────────────────────────────────────────────────────────────┘
          │ HTTP GET/POST
          │ JSON
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAMADA DE FRONTEND                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Next.js Application                    │  │
│  │  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │   Pages      │  │  Components   │               │  │
│  │  │  • Dashboard │  │  • BusCard    │               │  │
│  │  │  • Home      │  │  • Metrics    │               │  │
│  │  └──────┬───────┘  └──────┬────────┘               │  │
│  │         │                 │                          │  │
│  │  ┌──────▼─────────────────▼──────┐                 │  │
│  │  │      API Client (api.ts)       │                 │  │
│  │  │  • useDashboardData()          │                 │  │
│  │  │  • useCurrentBuses()           │                 │  │
│  │  │  • useOccupancyData()          │                 │  │
│  │  └────────────────────────────────┘                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Dados

### 1. Coleta de Dados (ESP32 → Backend)

```
ESP32 → HTTP POST → Flask API → Validação → Processamento → Banco de Dados
```

**Detalhamento:**
1. ESP32 coleta GPS e captura imagem
2. Envia via HTTP POST para `/api/location-image`
3. Backend valida dados recebidos
4. Processa imagem com YOLO (se disponível)
5. Calcula ocupação e ETA
6. Salva no banco (se disponível)
7. Retorna resposta com resultados

### 2. Visualização (Frontend → Backend)

```
Frontend → HTTP GET → Flask API → Consulta Banco → Processa → Retorna JSON
```

**Detalhamento:**
1. Frontend faz requisição para `/api/dashboard/data`
2. Backend consulta banco de dados (ou usa fallback)
3. Agrega dados (ocupação, ETA, métricas)
4. Retorna JSON estruturado
5. Frontend renderiza no dashboard

## 📦 Componentes Principais

### Backend (Flask)

#### APIs Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check |
| `/api/location` | POST | Recebe localização GPS |
| `/api/image/analyze` | POST | Analisa imagem |
| `/api/location-image` | POST | API integrada (GPS + Imagem) |
| `/api/dashboard/data` | GET | Dados completos do dashboard |
| `/api/dashboard/buses` | GET | Ônibus ativos |
| `/api/dashboard/occupancy` | GET | Dados de ocupação |
| `/api/dashboard/metrics` | GET | Métricas do sistema |

#### Estrutura de Pastas

```
server/
├── main.py                 # Entry point, cria app Flask
├── config_simple.py       # Configurações centralizadas
│
├── api/                    # Endpoints HTTP
│   ├── dashboard_api.py    # API do dashboard
│   ├── simple_location_api.py
│   ├── simple_image_api.py
│   └── simple_integrated_api.py
│
├── database/              # Acesso a dados
│   └── simple_connection.py
│
├── ml/                    # Machine Learning
│   ├── occupancy_predictor.py
│   └── eta_confidence.py
│
└── db/                    # Scripts SQL
    └── create_tables.sql
```

### Frontend (Next.js)

#### Estrutura de Pastas

```
client/
├── app/                   # Páginas Next.js (App Router)
│   ├── page.tsx          # Página inicial
│   └── dashboard/        # Dashboard
│       └── page.tsx
│
├── components/           # Componentes React
│   └── dashboard/
│       ├── BusCard.tsx
│       └── SystemMetrics.tsx
│
└── lib/                  # Utilitários
    └── api.ts           # Cliente API e hooks
```

#### Hooks Personalizados

```typescript
// Uso no frontend
const { data, loading, error } = useDashboardData();
const { data: buses } = useCurrentBuses('L1');
const { data: occupancy } = useOccupancyData();
```

## 🗄️ Banco de Dados

### Schema Simplificado

```
bus_location
├── id (PK)
├── bus_line
├── latitude
├── longitude
└── timestamp_location

bus_image
├── id (PK)
├── location_id (FK)
├── image_data (BYTEA)
├── occupancy_count
└── timestamp_image

bus_eta
├── id (PK)
├── location_id (FK)
├── eta_minutes
├── confidence_percent
└── timestamp_eta

bus_interval
├── id (PK)
├── location_id (FK)
├── interval_seconds
└── timestamp_interval
```

### Modo Fallback

Se o banco não estiver disponível:
- Sistema usa dados simulados
- APIs continuam funcionando
- Dashboard exibe dados de exemplo
- Logs indicam "Modo Fallback"

## 🤖 Machine Learning

### YOLO (Occupancy Detection)

- **Entrada**: Imagem do ônibus (Base64)
- **Processo**: Detecta pessoas na imagem
- **Saída**: Contagem de pessoas e nível de ocupação (0-4)

### ETA Confidence

- **Entrada**: Coordenadas GPS, histórico, ocupação
- **Processo**: Calcula confiança baseada em fatores
- **Saída**: ETA em minutos + confiança (0-100%)

## 🔐 Segurança

### CORS

Configurado para permitir:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`

### Validação

- Coordenadas GPS validadas
- Linha de ônibus sanitizada
- Imagens validadas (formato, tamanho)
- Timestamps parseados corretamente

## 📊 Fluxo Completo de Exemplo

### Cenário: ESP32 envia dados

1. **ESP32** captura:
   - GPS: -8.0630, -34.8710
   - Imagem: Foto do interior do ônibus

2. **ESP32** envia POST para `/api/location-image`:
   ```json
   {
     "bus_line": "L1",
     "latitude": -8.0630,
     "longitude": -34.8710,
     "image_data": "data:image/jpeg;base64,..."
   }
   ```

3. **Backend** processa:
   - Valida coordenadas
   - Processa imagem com YOLO
   - Detecta 18 pessoas
   - Calcula ocupação: Nível 2 (Média)
   - Calcula ETA: 12.5 minutos
   - Salva no banco

4. **Backend** retorna:
   ```json
   {
     "status": "success",
     "occupancy": {
       "level": 2,
       "person_count": 18,
       "confidence": 85.5
     },
     "eta": {
       "eta_minutes": 12.5,
       "confidence_percent": 78.2
     }
   }
   ```

5. **Frontend** atualiza:
   - Dashboard consulta `/api/dashboard/data`
   - Recebe dados atualizados
   - Renderiza novo card de ônibus
   - Atualiza métricas

## 🔧 Configurações Importantes

### Portas

- Backend: 3000
- Frontend: 3001
- PostgreSQL: 5432

### URLs

- API Base: `http://localhost:3000`
- Dashboard: `http://localhost:3001/dashboard`
- Health: `http://localhost:3000/health`

### Variáveis de Ambiente

Ver `server/env.example` para todas as opções.

## 📝 Notas de Implementação

### Modo Fallback

O sistema foi projetado para funcionar mesmo sem:
- Banco de dados
- YOLO/ML
- Configurações complexas

Isso facilita desenvolvimento e testes.

### Escalabilidade

Para produção, considere:
- Cache (Redis)
- Processamento assíncrono (Celery)
- Load balancer
- CDN para frontend

---

**Para mais detalhes**, consulte:
- `INTEGRATION_GUIDE.md` - Integração entre componentes
- `server/README.md` - Detalhes do backend
- `README.md` - Visão geral do projeto

