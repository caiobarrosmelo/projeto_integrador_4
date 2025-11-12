# 🔐 Autenticação MFA Simples com QR Code

Sistema de autenticação MFA (Multi-Factor Authentication) simples usando TOTP (Time-based One-Time Password) com QR Code.

## 🎯 Como Funciona

1. **Login**: Usuário faz login com email e senha
2. **Setup MFA**: Sistema gera um QR Code único
3. **Escanear QR**: Usuário escaneia com app autenticador (Google Authenticator, Authy, Microsoft Authenticator)
4. **Verificação**: Usuário digita código de 6 dígitos do app
5. **Acesso**: Após verificação, acessa o dashboard Power BI

## 📱 Apps Compatíveis

Qualquer app autenticador que suporte TOTP:
- ✅ Google Authenticator
- ✅ Microsoft Authenticator
- ✅ Authy
- ✅ 1Password
- ✅ LastPass Authenticator
- ✅ Qualquer app TOTP padrão

## 🚀 Como Usar

### 1. Acesse o Dashboard

```
http://localhost:3001/powerbi-dashboard
```

### 2. Faça Login

**Credenciais de Demo:**
- Email: `admin@example.com`
- Senha: `admin123`

### 3. Configure MFA

1. Clique em "Gerar QR Code"
2. Abra seu app autenticador
3. Escaneie o QR Code (ou digite a chave manualmente)
4. Clique em "Já escaneei, continuar"

### 4. Verifique o Código

1. Digite o código de 6 dígitos do seu app autenticador
2. Clique em "Verificar e Entrar"
3. Pronto! Você está autenticado

## ⚙️ Configuração para Produção

### Adicionar Usuários

Edite `client/app/api/auth/verify/route.ts`:

```typescript
// Adicione usuários válidos
const validUsers = new Set([
  'admin@example.com',
  'user@example.com',
  'seu-email@exemplo.com' // Adicione aqui
]);
```

### Alterar Senha Padrão

No mesmo arquivo, altere a verificação de senha:

```typescript
// Em produção, use hash de senha (bcrypt, argon2, etc.)
if (password !== 'sua-senha-aqui') {
  return NextResponse.json(
    { error: 'Usuário ou senha inválidos' },
    { status: 401 }
  );
}
```

### Usar Banco de Dados

Para produção, substitua o armazenamento em memória por banco de dados:

```typescript
// Em vez de:
const userSecrets = new Map<string, string>();

// Use:
// - PostgreSQL
// - MongoDB
// - SQLite
// - etc.
```

## 🔒 Segurança

### ✅ Implementado

- ✅ TOTP padrão (RFC 6238)
- ✅ Tokens expiram em 30 segundos
- ✅ QR Code gerado dinamicamente
- ✅ Sessões com expiração (24 horas)
- ✅ Cookies HTTP-only

### ⚠️ Melhorias para Produção

1. **Hash de Senhas**: Use bcrypt ou argon2
2. **Banco de Dados**: Armazene secrets e sessões em DB
3. **Rate Limiting**: Limite tentativas de login
4. **HTTPS**: Use sempre em produção
5. **Rotação de Secrets**: Permita regenerar QR code
6. **Backup Codes**: Gere códigos de recuperação

## 🐛 Troubleshooting

### QR Code não aparece

- Verifique se o servidor está rodando
- Abra o console do navegador (F12) para erros
- Verifique se a rota `/api/auth/setup` está funcionando

### Código MFA sempre inválido

- Verifique se o relógio do dispositivo está sincronizado
- Certifique-se de estar usando o código mais recente (expira em 30s)
- Tente gerar um novo QR code

### Sessão expira muito rápido

- Edite `client/app/api/auth/verify/route.ts`
- Altere `expiresAt` para o tempo desejado

## 📚 Recursos

- [TOTP RFC 6238](https://tools.ietf.org/html/rfc6238)
- [otplib Documentation](https://github.com/yeojz/otplib)
- [Google Authenticator](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)

## 🎉 Pronto!

Agora você tem um sistema MFA simples e funcional, sem necessidade de Azure AD ou configurações complexas!

