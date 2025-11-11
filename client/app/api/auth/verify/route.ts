import { NextRequest, NextResponse } from 'next/server';
import { authenticator } from 'otplib';
import { userSecrets, userSessions, validUsers } from '../store';

export async function POST(request: NextRequest) {
  try {
    const { email, password, token } = await request.json();

    if (!email || !password || !token) {
      return NextResponse.json(
        { error: 'Email, senha e código MFA são obrigatórios' },
        { status: 400 }
      );
    }

    const emailLower = email.toLowerCase().trim();

    console.log(`[MFA Verify] Tentativa de login: ${emailLower}`);
    console.log(`[MFA Verify] Total de secrets disponíveis: ${userSecrets.size}`);
    console.log(`[MFA Verify] Secrets:`, Array.from(userSecrets.keys()));

    // Verifica se o usuário existe (em produção, verificar no banco)
    if (!validUsers.has(emailLower)) {
      return NextResponse.json(
        { error: 'Usuário ou senha inválidos' },
        { status: 401 }
      );
    }

    // Verifica senha simples (em produção, usar hash)
    // Para demo: senha padrão é "admin123"
    if (password !== 'admin123') {
      return NextResponse.json(
        { error: 'Usuário ou senha inválidos' },
        { status: 401 }
      );
    }

    // Busca o secret do usuário
    const secret = userSecrets.get(emailLower);

    if (!secret) {
      console.log(`[MFA Verify] Secret não encontrado para: ${emailLower}`);
      return NextResponse.json(
        { error: 'Usuário não configurou MFA. Configure primeiro.' },
        { status: 400 }
      );
    }

    console.log(`[MFA Verify] Secret encontrado para: ${emailLower}`);

    // Verifica o token TOTP
    const isValid = authenticator.verify({ token, secret });

    if (!isValid) {
      return NextResponse.json(
        { error: 'Código MFA inválido' },
        { status: 401 }
      );
    }

    // Cria sessão (em produção, usar JWT ou session do Next.js)
    const sessionId = crypto.randomUUID?.() || 
      `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
    const expiresAt = Date.now() + 24 * 60 * 60 * 1000; // 24 horas

    userSessions.set(sessionId, {
      email: emailLower,
      expiresAt,
    });

    // Retorna cookie via header
    const response = NextResponse.json({
      success: true,
      email: emailLower,
    });

    response.cookies.set('auth_session', sessionId, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 24 * 60 * 60, // 24 horas
    });

    return response;
  } catch (error) {
    console.error('Erro na verificação:', error);
    return NextResponse.json(
      { error: 'Erro ao verificar autenticação' },
      { status: 500 }
    );
  }
}

// Rota para verificar se está autenticado
export async function GET(request: NextRequest) {
  try {
    const sessionId = request.cookies.get('auth_session')?.value;

    if (!sessionId) {
      return NextResponse.json({ authenticated: false }, { status: 401 });
    }

    const session = userSessions.get(sessionId);

    if (!session || session.expiresAt < Date.now()) {
      userSessions.delete(sessionId);
      return NextResponse.json({ authenticated: false }, { status: 401 });
    }

    return NextResponse.json({
      authenticated: true,
      email: session.email,
    });
  } catch (error) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
}

