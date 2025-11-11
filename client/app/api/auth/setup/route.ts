import { NextRequest, NextResponse } from 'next/server';
import { authenticator } from 'otplib';
import QRCode from 'qrcode';
import { userSecrets } from '../store';

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: 'Email é obrigatório' },
        { status: 400 }
      );
    }

    // Normaliza o email
    const emailLower = email.toLowerCase().trim();
    
    // Gera um secret único para o usuário
    const secret = authenticator.generateSecret();
    userSecrets.set(emailLower, secret);
    
    console.log(`[MFA Setup] Secret gerado para: ${emailLower}`);
    console.log(`[MFA Setup] Total de secrets: ${userSecrets.size}`);

    // Cria o nome do serviço (aparece no app autenticador)
    const serviceName = 'Dashboard Power BI';
    const accountName = email;

    // Gera a URL otpauth
    const otpauthUrl = authenticator.keyuri(accountName, serviceName, secret);

    // Gera o QR code como data URL
    const qrCodeDataUrl = await QRCode.toDataURL(otpauthUrl);

    return NextResponse.json({
      secret,
      qrCode: qrCodeDataUrl,
      manualEntryKey: secret, // Para entrada manual se o QR não funcionar
    });
  } catch (error) {
    console.error('Erro ao gerar QR code:', error);
    return NextResponse.json(
      { error: 'Erro ao gerar QR code' },
      { status: 500 }
    );
  }
}

