# 🚌 Sistema de Monitoramento IoT para Ônibus

Sistema completo de monitoramento em tempo real de ônibus utilizando dispositivos ESP32, processamento na nuvem e visualização em dashboard web.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Início Rápido](#-início-rápido)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Executando o Projeto](#-executando-o-projeto)
- [Documentação](#-documentação)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Este projeto é um sistema completo de monitoramento IoT que:

- 📡 **Coleta dados** de dispositivos ESP32 (GPS, câmera)
- ☁️ **Processa na nuvem** com Flask (Python)
- 🤖 **Aplica Machine Learning** para análise de ocupação (YOLO)
- 📊 **Visualiza em tempo real** com dashboard Next.js
- 🗄️ **Armazena dados** em PostgreSQL (opcional)

### Componentes Principais

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   ESP32     │─────▶│   Backend    │─────▶│  Frontend   │
│  (Hardware) │      │   (Flask)    │      │  (Next.js)  │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  PostgreSQL  │
                     │  (Opcional)  │
                     └─────────────┘
```

---

## ⚡ Início Rápido

1. **Instalar dependências:**
   ```bash
   # Backend
   cd server
   pip install -r requirements_simple.txt
   
   # Frontend
   cd ../client
   npm install
   ```

2. **Iniciar servidores (2 terminais):**
   ```bash
   # Terminal 1 - Backend
   cd server
   python main.py
   
   # Terminal 2 - Frontend
   cd client
   npm run dev
   ```

3. **Acessar:**
   - Dashboard: http://localhost:3001/dashboard
   - API: http://localhost:3000/health

> O sistema funciona sem banco de dados usando dados simulados

---

## 📁 Estrutura do Projeto

```
projeto_integrador_4/
│
├── 📄 README.md                    # Este arquivo - comece aqui!
├── 📄 README_EXECUCAO.md           # Guia rápido de execução
├── 📄 GUIA_EXECUCAO_LOCAL.md       # Guia completo passo a passo
│
├── 🖥️ server/                      # Backend (Flask/Python)
│   ├── main.py                     # ⭐ Ponto de entrada principal
│   ├── config_simple.py             # Configurações
│   ├── requirements_simple.txt     # Dependências Python
│   ├── env.example                  # Template de variáveis de ambiente
│   │
│   ├── api/                         # Endpoints da API
│   │   ├── dashboard_api.py         # API do dashboard
│   │   ├── simple_location_api.py   # API de localização GPS
│   │   ├── simple_image_api.py      # API de análise de imagens
│   │   └── simple_integrated_api.py # API integrada
│   │
│   ├── database/                    # Acesso ao banco de dados
│   │   └── simple_connection.py     # Conexão e repositórios
│   │
│   ├── ml/                          # Machine Learning
│   │   ├── occupancy_predictor.py   # Predição de ocupação
│   │   └── eta_confidence.py       # Confiança de ETA
│   │
│   └── db/                          # Scripts SQL
│       └── create_tables.sql        # Schema do banco
│
├── 🎨 client/                       # Frontend (Next.js/React)
│   ├── package.json                 # Dependências Node.js
│   ├── app/                         # Páginas Next.js
│   │   └── dashboard/               # Dashboard principal
│   ├── components/                  # Componentes React
│   │   └── dashboard/               # Componentes do dashboard
│   └── lib/                         # Utilitários
│       └── api.ts                   # Cliente API
│
├── 🔧 hardware/                     # Código do ESP32
│   ├── ESP32_S3/
│   │   ├── main_real.ino           # Código para hardware real
│   │   └── main_simulated.ino      # Código simulado
│   └── README.md                    # Documentação do hardware
│
├── 📊 data/                         # Dados de exemplo e logs
│   ├── gps_logs.json
│   ├── camera_logs.json
│   └── prediction_logs.json
│
├── 🧪 tests/                        # Testes
│   ├── test_esp32.py
│   ├── test_server.py
│   └── teste_ml.py
│
└── 📚 docs/                         # Documentação adicional
    ├── INTEGRATION_GUIDE.md         # Guia de integração
    ├── SUGESTOES_MELHORIAS.md       # Sugestões de melhorias
    └── fluxo.png                    # Diagrama de fluxo
```

---

## 📋 Pré-requisitos

### Obrigatórios
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **npm** ou **yarn** - Vem com Node.js

### Opcionais (para funcionalidades completas)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **Arduino IDE** - Para programar ESP32

---

## 🛠️ Instalação

### 1. Clonar/Baixar o Projeto

```bash
# Se usar Git
git clone <url-do-repositorio>
cd projeto_integrador_4-modelo-integrado2

# Ou simplesmente extraia o ZIP do projeto
```

### 2. Instalar Dependências do Backend

```bash
cd server

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements_simple.txt
```

### 3. Instalar Dependências do Frontend

```bash
cd client
npm install
```

### 4. Configurar Variáveis de Ambiente (Opcional)

```bash
cd server
cp env.example .env
# Edite o arquivo .env com suas configurações
```

---

## 🚀 Executando o Projeto

### Opção 1: Scripts Automáticos (Mais Fácil)

**Windows:**
```bash
# Terminal 1
start_backend.bat

# Terminal 2
start_frontend.bat
```

**Linux/Mac:**
```bash
# Dar permissão de execução
chmod +x start_backend.sh start_frontend.sh

# Terminal 1
./start_backend.sh

# Terminal 2
./start_frontend.sh
```

### Opção 2: Manual

**Terminal 1 - Backend:**
```bash
cd server
python main.py
```

Você deve ver:
```
INFO - Iniciando servidor de monitoramento de ônibus IoT...
 * Running on http://0.0.0.0:3000
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```

Você deve ver:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3001
```

### Acessar o Sistema

- **Dashboard**: http://localhost:3001/dashboard
- **API Health Check**: http://localhost:3000/health
- **API Info**: http://localhost:3000/

---

## 📚 Documentação

### Guias Disponíveis

1. **ONBOARDING.md** - Guia passo a passo para primeira execução
2. **GUIA_EXECUCAO_LOCAL.md** - Guia completo detalhado
3. **ARQUITETURA.md** - Arquitetura e funcionamento do sistema
4. **INTEGRATION_GUIDE.md** - Guia de integração entre componentes
5. **DOCUMENTACAO.md** - Índice completo de toda documentação
6. **server/README.md** - Documentação do backend
7. **client/README.md** - Documentação do frontend
8. **hardware/README.md** - Documentação do ESP32

### Para Desenvolvedores

- **SUGESTOES_MELHORIAS.md** - Sugestões de melhorias de código
- **IMPLEMENTACAO_MELHORIAS.md** - Como implementar melhorias

---

## 🔧 Configuração do Banco de Dados (Opcional)

O sistema funciona **sem banco de dados** usando dados simulados. Para usar banco de dados:

### 1. Instalar PostgreSQL

**Windows**: Baixe do [site oficial](https://www.postgresql.org/download/windows/)  
**Linux**: `sudo apt-get install postgresql`  
**Mac**: `brew install postgresql`

### 2. Criar Banco de Dados

```bash
# Acessar PostgreSQL
psql -U postgres

# No prompt do PostgreSQL:
CREATE DATABASE bus_monitoring;
\q
```

### 3. Criar Schema e Dados Iniciais

```bash
# Opção A - Executar script SQL diretamente
psql -U postgres -d bus_monitoring -f server/db/create_tables.sql

# Opção B - Usar script Node para criar e popular o banco
cd server/db
npm install
npm run setup
```

### 4. Configurar .env do Backend

Edite `server/.env` com suas credenciais:
```env
DB_HOST=localhost
DB_NAME=bus_monitoring
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

---

## 🆘 Troubleshooting

### Problema: Porta 3000 já está em uso

**Solução:**
```bash
# Verificar o que está usando a porta
# Windows:
netstat -ano | findstr :3000

# Linux/Mac:
lsof -i :3000

# Matar o processo ou mudar a porta no config_simple.py
```

### Problema: Erro "Module not found"

**Backend:**
```bash
cd server
pip install -r requirements_simple.txt
```

**Frontend:**
```bash
cd client
npm install
```

### Problema: Frontend não conecta no backend

1. Verifique se o backend está rodando: `curl http://localhost:3000/health`
2. Verifique o console do navegador (F12)
3. Verifique se a URL está correta em `client/lib/api.ts`

### Problema: Erro de banco de dados

**Solução**: O sistema funciona sem banco! Se quiser usar banco:
- Verifique se PostgreSQL está rodando
- Verifique as credenciais em `server/.env`
- O sistema automaticamente usa modo fallback se não conectar

---

## 📊 Portas e URLs

| Serviço                | Porta | URL                    |
|------------------------|-------|------------------------|
| Backend (Flask)        | 3000  | http://localhost:3000  |
| Frontend (Next.js)     | 3001  | http://localhost:3001  |
| Pipeline IoT (Node)    | 4000  | http://localhost:4000  |
| PostgreSQL             | 5432  | localhost:5432         |

---

## 🎯 Fluxo de Dados

```
ESP32 → Backend (Flask) → Banco de Dados (Opcional)
                          ↓
                    Frontend (Next.js)
                          ↓
                    Dashboard Web
```

1. **ESP32** envia dados GPS e imagens via HTTP POST
2. **Backend** processa, analisa com ML e armazena
3. **Frontend** consulta backend e exibe no dashboard
4. **Usuário** visualiza dados em tempo real

---

## ✅ Checklist de Primeira Execução

- [ ] Python 3.8+ instalado
- [ ] Node.js 18+ instalado
- [ ] Dependências do backend instaladas
- [ ] Dependências do frontend instaladas
- [ ] Backend rodando em http://localhost:3000
- [ ] Frontend rodando em http://localhost:3001
- [ ] Dashboard acessível sem erros
- [ ] Health check retorna 200 OK

---

## 🤝 Contribuindo

1. Leia a documentação completa
2. Siga as convenções de código
3. Teste suas mudanças
4. Documente alterações importantes

---

## 📝 Licença

Este projeto foi desenvolvido para o Projeto Integrador do 4º Semestre de ADS.

---

## 🎓 Autores

Desenvolvido para o curso de Análise e Desenvolvimento de Sistemas.

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `docs/`
2. Verifique o `Troubleshooting` acima
3. Revise os logs do servidor

---

**Pronto para começar?** Siga o [Início Rápido](#-início-rápido) acima! 🚀
