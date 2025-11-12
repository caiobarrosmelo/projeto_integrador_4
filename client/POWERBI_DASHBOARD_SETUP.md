# 🔐 Configuração do Dashboard Power BI com Autenticação Microsoft

Este guia explica como configurar o dashboard Power BI com autenticação Microsoft (MFA).

## 📋 Pré-requisitos

1. Conta Microsoft (Azure AD)
2. Acesso ao Azure Portal
3. Relatório Power BI publicado

## 🚀 Passo a Passo

### 1. Registrar Aplicação no Azure AD

1. Acesse o [Azure Portal](https://portal.azure.com)
2. Vá em **Azure Active Directory** > **App registrations** > **New registration**
3. Preencha:
   - **Name**: `Dashboard Power BI - Projeto Integrador`
   - **Supported account types**: Selecione conforme necessário (Single tenant, Multi-tenant, etc.)
   - **Redirect URI**: 
     - Type: `Single-page application (SPA)`
     - URI: `http://localhost:3001/powerbi-dashboard` (desenvolvimento)
     - Para produção, adicione também a URL de produção
4. Clique em **Register**

### 2. Configurar Autenticação

1. Na página da aplicação, vá em **Authentication**
2. Em **Platform configurations**, adicione:
   - **Single-page application**
   - Redirect URIs:
     - `http://localhost:3001/powerbi-dashboard`
     - `http://localhost:3001` (para desenvolvimento)
3. Em **Implicit grant and hybrid flows**, marque:
   - ✅ **Access tokens**
   - ✅ **ID tokens**
4. Clique em **Save**

### 3. Configurar API Permissions (Opcional)

Se precisar acessar Power BI via API:

1. Vá em **API permissions**
2. Clique em **Add a permission**
3. Selecione **Power BI Service**
4. Adicione as permissões necessárias:
   - `Dataset.Read.All` (para ler dados)
   - `Report.Read.All` (para ler relatórios)
5. Clique em **Add permissions**

### 4. Configurar MFA (Multi-Factor Authentication)

1. No Azure Portal, vá em **Azure Active Directory** > **Security** > **MFA**
2. Configure as políticas de MFA conforme necessário
3. O Microsoft Authenticator será solicitado automaticamente durante o login

### 5. Obter Client ID e Tenant ID

1. Na página da aplicação, vá em **Overview**
2. Copie:
   - **Application (client) ID** → `NEXT_PUBLIC_AZURE_CLIENT_ID`
   - **Directory (tenant) ID** → Usado no `authority` (ou use `common` para multi-tenant)

### 6. Configurar Variáveis de Ambiente

Crie um arquivo `.env.local` na pasta `client/`:

```env
# Azure AD Configuration
NEXT_PUBLIC_AZURE_CLIENT_ID=seu-client-id-aqui
NEXT_PUBLIC_AZURE_AUTHORITY=https://login.microsoftonline.com/seu-tenant-id-ou-common
```

**Ou** edite diretamente `client/lib/msalConfig.ts`:

```typescript
export const msalConfig: Configuration = {
  auth: {
    clientId: "seu-client-id-aqui",
    authority: "https://login.microsoftonline.com/seu-tenant-id-ou-common",
    // ...
  },
  // ...
};
```

### 7. Obter URL do Power BI

1. Acesse seu relatório no Power BI
2. Vá em **Arquivo** > **Incorporar** > **Publicar na Web** (para relatórios públicos)
   - **OU** use **Arquivo** > **Incorporar** > **Website ou portal** (para relatórios privados)
3. Copie a URL de embed
4. Cole a URL no dashboard quando solicitado

**Nota**: Para relatórios privados, você precisará configurar permissões no Power BI Service.

## 🎯 Como Usar

1. Inicie o servidor de desenvolvimento:
   ```bash
   cd client
   npm run dev
   ```

2. Acesse: `http://localhost:3001/powerbi-dashboard`

3. Faça login com sua conta Microsoft (MFA será solicitado se configurado)

4. Cole a URL do Power BI quando solicitado

5. O relatório será exibido no dashboard

## 🔒 Segurança

- ✅ Autenticação obrigatória (não é possível acessar sem login)
- ✅ MFA suportado via Microsoft Authenticator
- ✅ Tokens armazenados em sessionStorage (limpos ao fechar navegador)
- ✅ Logout disponível no header

## 🐛 Troubleshooting

### Erro: "AADSTS50011: The redirect URI specified in the request does not match"

**Solução**: Verifique se a Redirect URI no Azure Portal corresponde exatamente à URL usada (incluindo porta e path).

### Erro: "Popup blocked"

**Solução**: O navegador pode estar bloqueando popups. O sistema tentará usar redirect automaticamente.

### Power BI não carrega

**Soluções**:
1. Verifique se a URL está correta
2. Verifique se você tem permissão para acessar o relatório
3. Tente abrir a URL diretamente no navegador
4. Verifique o console do navegador (F12) para erros

### MFA não está sendo solicitado

**Solução**: 
1. Verifique as configurações de MFA no Azure AD
2. Certifique-se de que a política de MFA está aplicada ao usuário
3. Tente fazer logout e login novamente

## 📚 Recursos

- [Documentação MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [Azure AD App Registration](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [Power BI Embedding](https://docs.microsoft.com/power-bi/developer/embedded/)

