import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const response = NextResponse.json({ success: true });
  
  // Remove o cookie de sessão
  response.cookies.delete('auth_session');
  
  return response;
}

