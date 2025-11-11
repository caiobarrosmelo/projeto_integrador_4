import { Configuration, PopupRequest } from "@azure/msal-browser";

/**
 * Configuração do MSAL para autenticação Microsoft
 * 
 * Para configurar:
 * 1. Registre sua aplicação no Azure Portal (https://portal.azure.com)
 * 2. Vá em Azure Active Directory > App registrations > New registration
 * 3. Configure as URLs de redirecionamento
 * 4. Copie o Client ID e Tenant ID
 * 5. Configure as variáveis de ambiente ou substitua os valores abaixo
 */

// Configuração do MSAL
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || "YOUR_CLIENT_ID_HERE",
    authority: process.env.NEXT_PUBLIC_AZURE_AUTHORITY || "https://login.microsoftonline.com/common",
    redirectUri: typeof window !== "undefined" ? window.location.origin + "/powerbi-dashboard" : "http://localhost:3001/powerbi-dashboard",
  },
  cache: {
    cacheLocation: "sessionStorage", // Armazena tokens na sessão
    storeAuthStateInCookie: false,
  },
};

/**
 * Escopos necessários para autenticação
 * user.read é necessário para login básico
 * Adicione outros escopos conforme necessário
 */
export const loginRequest: PopupRequest = {
  scopes: ["User.Read"],
  prompt: "select_account", // Força seleção de conta
};

/**
 * Escopos para Power BI (se necessário)
 */
export const powerBIScopes: PopupRequest = {
  scopes: ["https://analysis.windows.net/powerbi/api/.default"],
};

