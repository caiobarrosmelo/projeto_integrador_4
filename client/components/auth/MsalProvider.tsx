"use client"

import { MsalProvider as MSALProvider } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "@/lib/msalConfig";
import { ReactNode } from "react";

// Cria instância do MSAL
const msalInstance = new PublicClientApplication(msalConfig);

// Inicializa o MSAL
if (typeof window !== "undefined") {
  msalInstance.initialize().then(() => {
    // Handle redirect response
    msalInstance.handleRedirectPromise().catch((error) => {
      console.error("Erro ao processar redirect:", error);
    });
  });
}

interface MsalProviderProps {
  children: ReactNode;
}

export default function MsalProvider({ children }: MsalProviderProps) {
  return <MSALProvider instance={msalInstance}>{children}</MSALProvider>;
}

