/**
 * Script para gerar QR Code MFA uma única vez
 * Execute: node client/scripts/generate-qrcode.js
 */

const { authenticator } = require('otplib');
const QRCode = require('qrcode');
const fs = require('fs');
const path = require('path');

// Secret fixo (use o mesmo do store.ts)
// Para gerar um secret seguro, use: node -e "console.log(require('otplib').authenticator.generateSecret())"
const FIXED_SECRET = process.env.MFA_SECRET || 'JBSWY3DPEHPK3PXP'; // Secret padrão para demo

const serviceName = 'Dashboard Power BI';
const accountName = 'admin@example.com';

// Gera a URL otpauth
const otpauthUrl = authenticator.keyuri(accountName, serviceName, FIXED_SECRET);

console.log('🔐 Secret MFA Fixo:');
console.log(FIXED_SECRET);
console.log('\n📱 URL OTPAuth:');
console.log(otpauthUrl);
console.log('\n📸 Gerando QR Code...\n');

// Gera o QR code
QRCode.toDataURL(otpauthUrl, (err, url) => {
  if (err) {
    console.error('Erro ao gerar QR code:', err);
    return;
  }

  // Salva como imagem
  const base64Data = url.replace(/^data:image\/png;base64,/, '');
  const outputPath = path.join(__dirname, '..', 'public', 'mfa-qrcode.png');
  
  fs.writeFileSync(outputPath, base64Data, 'base64');
  console.log('✅ QR Code salvo em:', outputPath);
  console.log('\n📋 Instruções:');
  console.log('1. Abra o arquivo mfa-qrcode.png');
  console.log('2. Escaneie com seu app autenticador (Google Authenticator, etc.)');
  console.log('3. Use o código de 6 dígitos para fazer login');
  console.log('\n💡 Ou escaneie diretamente esta URL no app:');
  console.log(otpauthUrl);
});

