# 🎨 Frontend - Dashboard Next.js

Interface web para visualização em tempo real dos dados de monitoramento de ônibus.

## 📋 Índice

- [Início Rápido](#-início-rápido)
- [Estrutura](#-estrutura)
- [Configuração](#-configuração)
- [Componentes](#-componentes)
- [API Client](#-api-client)

---

## ⚡ Início Rápido

```bash
# 1. Instalar dependências
npm install

# 2. Executar em desenvolvimento
npm run dev

# 3. Acessar
# http://localhost:3001/dashboard
```

---

## 📁 Estrutura

```
client/
├── app/                    # Páginas Next.js (App Router)
│   ├── page.tsx           # Página inicial
│   ├── layout.tsx         # Layout principal
│   └── dashboard/
│       └── page.tsx       # ⭐ Dashboard principal
│
├── components/            # Componentes React
│   ├── dashboard/
│   │   ├── BusCard.tsx    # Card de ônibus individual
│   │   └── SystemMetrics.tsx # Métricas do sistema
│   └── ui/                # Componentes UI (shadcn/ui)
│
├── lib/                   # Utilitários
│   ├── api.ts            # ⭐ Cliente API e hooks
│   └── utils.ts          # Funções utilitárias
│
└── public/                # Arquivos estáticos
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie `.env.local` (opcional):

```env
NEXT_PUBLIC_API_URL=http://localhost:3000
```

**Padrão**: Se não configurado, usa `http://localhost:3000`

### Configuração da API

A URL da API está configurada em `lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';
```

---

## 🧩 Componentes

### Dashboard Page

**Arquivo**: `app/dashboard/page.tsx`

Página principal do dashboard com:
- Visão geral do sistema
- Lista de ônibus ativos
- Análise de ocupação
- Métricas do sistema

### BusCard

**Arquivo**: `components/dashboard/BusCard.tsx`

Exibe informações de um ônibus:
- Linha e nome
- Localização GPS
- Nível de ocupação
- ETA estimado
- Status

### SystemMetrics

**Arquivo**: `components/dashboard/SystemMetrics.tsx`

Exibe métricas do sistema:
- Requisições hoje
- Tempo médio de resposta
- Taxa de erro
- Uso de memória/CPU

---

## 🔌 API Client

### Hooks Disponíveis

```typescript
// Dados completos do dashboard
const { data, loading, error } = useDashboardData();

// Ônibus ativos
const { data: buses } = useCurrentBuses('L1'); // Filtrar por linha

// Dados de ocupação
const { data: occupancy } = useOccupancyData('L1', 24); // Últimas 24h

// Métricas do sistema
const { data: metrics } = useSystemMetrics();
```

### Cliente API Direto

```typescript
import { apiClient } from '@/lib/api';

// Obter dados do dashboard
const data = await apiClient.getDashboardData();

// Enviar localização
await apiClient.sendLocation({
  bus_line: 'L1',
  latitude: -8.0630,
  longitude: -34.8710
});
```

---

## 🚀 Executando

### Desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:3001

### Produção

```bash
# Build
npm run build

# Executar
npm start
```

### Lint

```bash
npm run lint
```

---

## 🎨 Styling

O projeto usa:
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes UI
- **Lucide React** - Ícones

### Tema

Suporte a tema claro/escuro via `next-themes`.

---

## 📱 Páginas

### Dashboard

**URL**: `/dashboard`

Dashboard principal com:
- Tabs: Visão Geral, Ônibus, Ocupação, Métricas
- Atualização automática a cada 30s
- Filtros por linha de ônibus

### Home

**URL**: `/`

Página inicial (pode ser customizada)

---

## 🔄 Atualização Automática

O dashboard atualiza automaticamente:
- **Dashboard**: A cada 30 segundos
- **Ônibus**: A cada 30 segundos
- **Métricas**: A cada 60 segundos

Também há botão "Atualizar" para refresh manual.

---

## 🧪 Desenvolvimento

### Adicionar Novo Componente

```typescript
// components/dashboard/MeuComponente.tsx
export default function MeuComponente() {
  return <div>Meu componente</div>;
}
```

### Adicionar Nova Página

```typescript
// app/minha-pagina/page.tsx
export default function MinhaPagina() {
  return <div>Minha página</div>;
}
```

### Adicionar Novo Hook

```typescript
// lib/api.ts
export const useMeusDados = () => {
  const [data, setData] = useState(null);
  // ... lógica
  return { data, loading, error };
};
```

---

## 🔧 Troubleshooting

### Erro: "Module not found"

```bash
rm -rf node_modules package-lock.json
npm install
```

### Erro: "Cannot connect to API"

1. Verifique se o backend está rodando
2. Teste: `curl http://localhost:3000/health`
3. Verifique a URL em `lib/api.ts`

### Erro: "Port 3001 already in use"

O Next.js automaticamente tenta outra porta. Ou:

```bash
PORT=3002 npm run dev
```

### Build Fails

```bash
# Limpar cache
rm -rf .next
npm run build
```

---

## 📚 Mais Informações

- **Guia Completo**: `../GUIA_EXECUCAO_LOCAL.md`
- **Integração**: `../INTEGRATION_GUIDE.md`
- **Arquitetura**: `../ARQUITETURA.md`

---

**Pronto para desenvolver!** 🚀
