/**
 * Armazenamento compartilhado para MFA
 * Em produção, substitua por banco de dados
 */

// Secret fixo para MFA (gerado uma vez e usado sempre)
// Para gerar um novo secret, execute: node client/scripts/generate-qrcode.js
export const FIXED_MFA_SECRET = process.env.MFA_SECRET || 'JBSWY3DPEHPK3PXP';

// Mapas compartilhados entre todas as rotas
export const userSecrets = new Map<string, string>();
export const userSessions = new Map<string, { email: string; expiresAt: number }>();

// Usuários válidos (em produção, buscar do banco de dados)
export const validUsers = new Set(['admin@example.com', 'user@example.com']);

// Inicializa secrets fixos para todos os usuários válidos
validUsers.forEach(email => {
  userSecrets.set(email.toLowerCase(), FIXED_MFA_SECRET);
});

