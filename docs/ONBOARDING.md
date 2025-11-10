# 👋 Guia de Primeiro Uso (Onboarding)

Guia para ajudar a entender e executar o projeto pela primeira vez.

## 🎯 O que é este projeto?

Sistema de monitoramento IoT que:
- Recebe dados de GPS e imagens de dispositivos ESP32
- Processa e analisa os dados no servidor
- Exibe informações em tempo real em um dashboard web

## ⏱️ Tempo Estimado

- **Instalação**: 10-15 minutos
- **Primeira execução**: 5 minutos
- **Total**: ~20 minutos

## 📋 Antes de Começar

### Verificar Instalações

```bash
# Verificar Python
python --version
# Deve mostrar: Python 3.8 ou superior

# Verificar Node.js
node --version
# Deve mostrar: v18 ou superior

# Verificar npm
npm --version
# Deve mostrar: versão do npm
```

**Não tem instalado?**
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/ (inclui npm)

## 🚀 Passo a Passo

### Passo 1: Preparar o Ambiente (5 min)

```bash
# 1. Navegar até o projeto
cd projeto_integrador_4-modelo-integrado2

# 2. Instalar dependências do backend
cd server
pip install -r requirements_simple.txt

# 3. Instalar dependências do frontend
cd ../client
npm install
```

**O que está acontecendo?**
- Instalando bibliotecas Python necessárias (Flask, etc.)
- Instalando pacotes Node.js necessários (React, Next.js, etc.)

### Passo 2: Iniciar o Backend (2 min)

**Abra um terminal:**

```bash
cd server
python main.py
```

**O que você deve ver:**
```
INFO - Iniciando servidor de monitoramento de ônibus IoT...
 * Running on http://0.0.0.0:3000
```

**✅ Sucesso se aparecer**: "Running on http://0.0.0.0:3000"

**❌ Problema?** Veja a seção [Problemas Comuns](#problemas-comuns)

### Passo 3: Iniciar o Frontend (2 min)

**Abra OUTRO terminal** (deixe o backend rodando):

```bash
cd client
npm run dev
```

**O que você deve ver:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3001
  ✓ Ready in 2.3s
```

**✅ Sucesso se aparecer**: "Ready" e URL do localhost

**❌ Problema?** Veja a seção [Problemas Comuns](#problemas-comuns)

### Passo 4: Acessar o Dashboard (1 min)

1. Abra seu navegador
2. Acesse: **http://localhost:3001/dashboard**
3. Você deve ver o dashboard com dados (mesmo que simulados)

**✅ Sucesso se:**
- A página carrega
- Você vê cards de ônibus
- Não há erros no console (F12)

**❌ Problema?** Veja a seção [Problemas Comuns](#problemas-comuns)

## 🧪 Testar se Está Funcionando

### Teste 1: Health Check da API

Abra um novo terminal e execute:

```bash
# Windows (PowerShell)
curl http://localhost:3000/health

# Ou use um navegador:
# http://localhost:3000/health
```

**Deve retornar:**
```json
{
  "status": "healthy",
  "service": "bus-monitoring-api"
}
```

### Teste 2: Verificar Console do Navegador

1. Abra o dashboard: http://localhost:3001/dashboard
2. Pressione **F12** para abrir DevTools
3. Vá na aba **Console**
4. **Não deve haver erros vermelhos**

### Teste 3: Verificar Network

1. No DevTools (F12), vá na aba **Network**
2. Recarregue a página (F5)
3. Procure por requisições para `localhost:3000`
4. **Devem retornar status 200 (verde)**

## 🎉 Pronto!

Se todos os testes passaram, você está pronto para usar o sistema!

### Próximos Passos

1. **Explorar o Dashboard**
   - Veja os diferentes tabs
   - Observe os dados sendo atualizados
   - Teste os filtros

2. **Entender a Estrutura**
   - Leia `README.md` para visão geral
   - Explore `server/` para entender o backend
   - Explore `client/` para entender o frontend

3. **Ler a Documentação**
   - `INTEGRATION_GUIDE.md` - Como tudo se conecta
   - `GUIA_EXECUCAO_LOCAL.md` - Guia completo
   - `server/README.md` - Detalhes do backend

## ❓ Problemas Comuns

### Erro: "python: command not found"

**Solução:**
- Windows: Use `py` ao invés de `python`
- Linux/Mac: Instale Python ou use `python3`

### Erro: "ModuleNotFoundError"

**Solução:**
```bash
cd server
pip install -r requirements_simple.txt
```

### Erro: "Port 3000 already in use"

**Solução:**
```bash
# Ver o que está usando a porta
# Windows:
netstat -ano | findstr :3000

# Linux/Mac:
lsof -i :3000

# Matar o processo ou mudar a porta
```

### Erro: "npm: command not found"

**Solução:**
- Instale Node.js: https://nodejs.org/
- Reinicie o terminal após instalar

### Dashboard não carrega / Erro 404

**Solução:**
1. Verifique se o frontend está rodando
2. Verifique se está acessando a URL correta: http://localhost:3001/dashboard
3. Verifique o console do navegador (F12) para erros

### Dashboard carrega mas não mostra dados

**Solução:**
1. Verifique se o backend está rodando
2. Teste: http://localhost:3000/health
3. Verifique o console do navegador (F12) - Network tab
4. O sistema funciona com dados simulados mesmo sem banco

## 📚 Recursos de Aprendizado

### Para Entender o Projeto

1. **Arquitetura**: Leia `INTEGRATION_GUIDE.md`
2. **Código Backend**: Explore `server/api/`
3. **Código Frontend**: Explore `client/app/` e `client/components/`

### Para Desenvolver

1. **Melhorias**: Leia `SUGESTOES_MELHORIAS.md`
2. **Boas Práticas**: Leia `IMPLEMENTACAO_MELHORIAS.md`
3. **Estrutura**: Veja a seção "Estrutura do Projeto" no README.md

## 🆘 Ainda com Problemas?

1. **Verifique os logs**
   - Backend: Veja o terminal onde rodou `python main.py`
   - Frontend: Veja o terminal onde rodou `npm run dev`
   - Navegador: Console (F12)

2. **Verifique a documentação**
   - `GUIA_EXECUCAO_LOCAL.md` - Guia completo
   - `README.md` - Visão geral
   - `Troubleshooting` no README.md

3. **Verifique se tudo está instalado**
   ```bash
   python --version
   node --version
   npm --version
   ```

## ✅ Checklist de Sucesso

Marque quando completar:

- [ ] Python instalado e funcionando
- [ ] Node.js instalado e funcionando
- [ ] Dependências do backend instaladas
- [ ] Dependências do frontend instaladas
- [ ] Backend rodando sem erros
- [ ] Frontend rodando sem erros
- [ ] Dashboard acessível no navegador
- [ ] Health check retorna 200 OK
- [ ] Console do navegador sem erros
- [ ] Dados aparecendo no dashboard

**Tudo marcado?** 🎉 Você está pronto para usar o projeto!

---

**Dúvidas?** Consulte a documentação ou os guias disponíveis no projeto.

