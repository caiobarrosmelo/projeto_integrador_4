# 🚀 Guia Completo: Como Rodar o Projeto Localmente

> **Nota**: Para início rápido, veja o [README.md](README.md#-início-rápido). Este guia fornece instruções detalhadas passo a passo.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** e npm ([Download](https://nodejs.org/))
- **PostgreSQL 12+** (Opcional - o sistema funciona sem banco) ([Download](https://www.postgresql.org/download/))

## 🔧 Instalação e Configuração

### 1. Clone/Prepare o Projeto

```bash
# Navegue até o diretório do projeto
cd projeto_integrador_4-modelo-integrado2
```

### 2. Configurar o Backend (Flask)

```bash
# Entre no diretório do servidor
cd server

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements_simple.txt

# OU se requirements_simple.txt não existir:
pip install flask flask-cors psycopg2-binary
```

### 3. Configurar o Frontend (Next.js)

```bash
# Em um novo terminal, entre no diretório do cliente
cd client

# Instale as dependências
npm install
```

### 4. Configurar Banco de Dados (Opcional)

O sistema funciona **sem banco de dados** usando dados simulados. Se quiser usar banco de dados:

#### 4.1. Instalar PostgreSQL

**Windows:**
- Baixe do site oficial: https://www.postgresql.org/download/windows/
- Durante a instalação, anote a senha do usuário `test`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

#### 4.2. Criar Banco de Dados

```bash
# Acesse o PostgreSQL
# Windows (via pgAdmin ou linha de comando):
psql -U postgres

# Linux/Mac:
sudo -u postgres psql
```

No prompt do PostgreSQL:
```sql
-- Criar banco de dados
CREATE DATABASE bus_monitoring;

-- Criar usuário (opcional)
CREATE USER bus_user WITH PASSWORD 'sua_senha_aqui';
GRANT ALL PRIVILEGES ON DATABASE bus_monitoring TO bus_user;

-- Sair
\q
```

#### 4.3. Executar Schema

```bash
# Execute o script SQL
psql -U postgres -d bus_monitoring -f server/db/create_tables.sql

# OU se usar usuário específico:
psql -U bus_user -d bus_monitoring -f server/db/create_tables.sql
```

#### 4.4. Configurar Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` no diretório `server/` (ou configure no sistema):

```bash
# Windows (PowerShell):
$env:DB_HOST="localhost"
$env:DB_NAME="bus_monitoring"
$env:DB_USER="postgres"
$env:DB_PASSWORD="sua_senha"
$env:API_PORT="3000"

# Linux/Mac:
export DB_HOST=localhost
export DB_NAME=bus_monitoring
export DB_USER=postgres
export DB_PASSWORD=sua_senha
export API_PORT=3000
```

## 🏃 Executando o Projeto

### Opção 1: Execução Básica (Sem Banco de Dados)

O sistema funciona perfeitamente sem banco de dados usando dados simulados.

#### Terminal 1 - Backend:
```bash
cd server
python main.py
```

Você deve ver:
```
INFO - Iniciando servidor de monitoramento de ônibus IoT...
INFO - Usando modo fallback (sem banco de dados)
 * Running on http://0.0.0.0:3000
```

#### Terminal 2 - Frontend:
```bash
cd client
npm run dev
```

Você deve ver:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3001
  - ready started server on 0.0.0.0:3001
```

#### Acessar o Dashboard:
Abra seu navegador em: **http://localhost:3001/dashboard**

### Opção 2: Execução Completa (Com Banco de Dados)

#### 1. Iniciar PostgreSQL
```bash
# Windows (se instalado como serviço, já está rodando)
# Linux:
sudo systemctl start postgresql
# Mac:
brew services start postgresql
```

#### 2. Iniciar Backend
```bash
cd server
python main.py
```

Você deve ver:
```
INFO - Banco de dados simplificado inicializado
INFO - * Running on http://0.0.0.0:3000
```

#### 3. Iniciar Frontend
```bash
cd client
npm run dev
```

#### 4. Acessar Dashboard
Abra: **http://localhost:3001/dashboard**

## 🧪 Verificar se Está Funcionando

### 1. Testar Backend

Abra um novo terminal e teste os endpoints:

```bash
# Health check
curl http://localhost:3000/health

# Dados do dashboard
curl http://localhost:3000/api/dashboard/data

# Ônibus ativos
curl http://localhost:3000/api/dashboard/buses
```

### 2. Testar Frontend

1. Abra o navegador em `http://localhost:3001/dashboard`
2. Verifique se:
   - ✅ A página carrega sem erros
   - ✅ Os dados são exibidos (mesmo que simulados)
   - ✅ Não há erros no console do navegador (F12)

### 3. Verificar Console do Navegador

Pressione `F12` no navegador e verifique:
- **Console**: Não deve haver erros vermelhos
- **Network**: As requisições para `localhost:3000` devem retornar status 200

## 🔍 Troubleshooting

### Problema: Porta 3000 já está em uso

**Solução:**
```bash
# Windows - Verificar o que está usando a porta:
netstat -ano | findstr :3000

# Linux/Mac:
lsof -i :3000

# Matar o processo ou mudar a porta do Flask
# Edite server/config_simple.py e mude API_PORT para 5000
# E atualize client/lib/api.ts para usar http://localhost:5000
```

### Problema: Erro ao conectar no banco de dados

**Solução:**
- Verifique se o PostgreSQL está rodando
- Verifique as credenciais em `server/config_simple.py`
- O sistema funciona sem banco (modo fallback)

### Problema: Frontend não conecta no backend

**Solução:**
1. Verifique se o backend está rodando em `http://localhost:3000`
2. Teste: `curl http://localhost:3000/health`
3. Verifique CORS em `server/config_simple.py`
4. Verifique se a URL está correta em `client/lib/api.ts`

### Problema: Erro "Module not found" no Python

**Solução:**
```bash
cd server
pip install -r requirements_simple.txt
# OU
pip install flask flask-cors psycopg2-binary
```

### Problema: Erro "Module not found" no Node.js

**Solução:**
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

### Problema: Next.js não inicia

**Solução:**
```bash
cd client
# Limpar cache
rm -rf .next
npm run dev
```

## 📊 Estrutura de Portas

| Serviço | Porta | URL |
|---------|-------|-----|
| Backend (Flask) | 3000 | http://localhost:3000 |
| Frontend (Next.js) | 3001 | http://localhost:3001 |
| PostgreSQL | 5433 | localhost:5433 |

## 🎯 Comandos Rápidos

### Iniciar Tudo (2 terminais)

**Terminal 1:**
```bash
cd server; python main.py
```

**Terminal 2:**
```bash
cd client; npm run dev
```

### Parar Serviços

- **Backend**: `Ctrl + C` no terminal do Flask
- **Frontend**: `Ctrl + C` no terminal do Next.js
- **PostgreSQL**: 
  - Windows: Parar serviço via Services
  - Linux: `sudo systemctl stop postgresql`
  - Mac: `brew services stop postgresql`

## 📝 Checklist de Execução

- [ ] Python 3.8+ instalado
- [ ] Node.js 18+ instalado
- [ ] Dependências do backend instaladas (`pip install -r requirements_simple.txt`)
- [ ] Dependências do frontend instaladas (`npm install`)
- [ ] Backend rodando em `http://localhost:3000`
- [ ] Frontend rodando em `http://localhost:3001`
- [ ] Dashboard acessível em `http://localhost:3001/dashboard`
- [ ] Sem erros no console do navegador

## 🎉 Pronto!

Se tudo estiver funcionando, você verá:
- ✅ Dashboard carregando dados
- ✅ Ônibus sendo exibidos (mesmo que simulados)
- ✅ Métricas do sistema funcionando
- ✅ Sem erros no console

## 📚 Próximos Passos

1. **Testar com dados reais**: Configure o ESP32 para enviar dados
2. **Configurar banco de dados**: Para persistência de dados
3. **Personalizar**: Ajuste as configurações conforme necessário

---

**Dúvidas?** Consulte o arquivo `CORRECOES_INTEGRACAO.md` para mais detalhes sobre a integração.

