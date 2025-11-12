# 🔐 Configuração MFA com Secret Fixo

O MFA agora usa um secret fixo que é gerado uma única vez. O QR code não aparece mais no site.

## 📱 Como Configurar (Uma Única Vez)

### Opção 1: Gerar QR Code via Script

1. Execute o script para gerar o QR code:

```bash
cd client
node scripts/generate-qrcode.js
```

2. O script irá:
   - Gerar um QR code em `public/mfa-qrcode.png`
   - Mostrar o secret e a URL OTPAuth no console

3. Escaneie o QR code com seu app autenticador:
   - Google Authenticator
   - Microsoft Authenticator
   - Authy
   - Ou qualquer app TOTP

### Opção 2: Entrada Manual

Se preferir não usar o script, você pode:

1. Pegar o secret fixo do arquivo `client/app/api/auth/store.ts`:
   ```typescript
   export const FIXED_MFA_SECRET = 'JBSWY2DPEHPK3PXP';
   ```

2. No seu app autenticador, adicione manualmente:
   - **Nome**: Dashboard Power BI
   - **Chave**: `JBSWY2DPEHPK3PXP` (ou o secret que você configurou)
   - **Tipo**: Time-based (TOTP)

## 🔄 Como Funciona Agora

1. **Login**: Usuário faz login com email e senha
2. **Verificação MFA**: Diretamente pede o código de 6 dígitos
3. **Sem Setup**: Não precisa mais configurar QR code no site

## 🔧 Personalizar o Secret

Para usar um secret diferente:

1. Gere um novo secret (pode usar qualquer string base32):
   ```bash
   # Ou use um gerador online de base32
   ```

2. Configure via variável de ambiente:
   ```env
   MFA_SECRET=SEU_SECRET_AQUI
   ```

3. Ou edite diretamente em `client/app/api/auth/store.ts`:
   ```typescript
   export const FIXED_MFA_SECRET = 'SEU_SECRET_AQUI';
   ```

4. Gere o QR code novamente:
   ```bash
   node client/scripts/generate-qrcode.js
   ```

## ✅ Vantagens

- ✅ Secret fixo - sempre o mesmo
- ✅ QR code gerado offline - não aparece no site
- ✅ Mais seguro - secret não exposto no frontend
- ✅ Mais simples - usuário só precisa do código

## 📝 Notas

- O secret padrão é `JBSWY2DPEHPK3PXP` (apenas para demo)
- Em produção, use um secret forte e único
- Guarde o secret com segurança
- Compartilhe o QR code apenas com usuários autorizados

