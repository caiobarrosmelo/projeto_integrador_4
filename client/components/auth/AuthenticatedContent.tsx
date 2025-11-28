"use client"

import { useIsAuthenticated, useMsal } from "@azure/msal-react";
import { ReactNode } from "react";
import LoginButton from "./LoginButton";
import { Card } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";

interface AuthenticatedContentProps {
  children: ReactNode;
}

export default function AuthenticatedContent({ children }: AuthenticatedContentProps) {
  const isAuthenticated = useIsAuthenticated();
  const { accounts } = useMsal();

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8 space-y-6">
          <div className="text-center space-y-4">
            <div>
              <h1 className="text-2xl font-bold">Acesso Restrito</h1>
              <p className="text-muted-foreground mt-2">
                Este dashboard requer autenticação com Microsoft (MFA)
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div className="text-sm text-blue-800 dark:text-blue-200">
                  <p className="font-semibold mb-1">Autenticação com MFA</p>
                  <p>Você precisará usar o Microsoft Authenticator para fazer login.</p>
                </div>
              </div>
            </div>

            <LoginButton />
          </div>
        </Card>
      </div>
    );
  }

  return (
    <>
      {/* Header com informações do usuário */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">Dashboard Power BI</h1>
              <p className="text-sm text-muted-foreground">
                Autenticado como: {accounts[0]?.name || accounts[0]?.username}
              </p>
            </div>
            <LogoutButton />
          </div>
        </div>
      </div>
      {children}
    </>
  );
}

function LogoutButton() {
  const { instance, accounts } = useMsal();

  const handleLogout = async () => {
    try {
      await instance.logoutPopup({
        account: accounts[0],
      });
    } catch (error) {
      console.error("Erro no logout:", error);
      // Fallback para redirect
      instance.logoutRedirect();
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
    >
      Sair
    </button>
  );
}

