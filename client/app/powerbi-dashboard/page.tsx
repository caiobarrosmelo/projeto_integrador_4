"use client"

import { Suspense } from "react";
import AuthGuard from "@/components/auth/AuthGuard";
import PowerBIEmbed from "@/components/powerbi/PowerBIEmbed";
import { Card } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

// 🔓 DESABILITAR MFA TEMPORARIAMENTE:
// Altere para true para desabilitar autenticação
const DISABLE_AUTH = false;

// 🔗 URL PADRÃO DO POWER BI:
// Defina aqui a URL do seu relatório Power BI
// Esta URL será carregada automaticamente ao acessar o dashboard
const DEFAULT_POWERBI_URL = 
  "https://app.powerbi.com/view?r=eyJrIjoiNGY2ZjZjM2ItNWJmYy00MDU5LThlZDQtYzU2ZjgxZGM1ZGU2IiwidCI6IjRhMjJmMTE2LTUxY2UtNGZlMy1hZWFhLTljNDYxNDNkMDg4YiJ9";

export default function PowerBIDashboardPage() {
  // Se autenticação estiver desabilitada, mostra direto o conteúdo
  if (DISABLE_AUTH) {
    return <PowerBIDashboardContentNoAuth />;
  }

  // Com autenticação habilitada
  return (
    <AuthGuard>
      <PowerBIDashboardContent />
    </AuthGuard>
  );
}

function PowerBIDashboardContent() {
  const { email, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">Dashboard Power BI</h1>
              <p className="text-sm text-muted-foreground">
                Autenticado como: {email}
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-sm"
            >
              Sair
            </Button>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="container mx-auto px-4 py-6">
        <Suspense fallback={<LoadingFallback />}>
          <PowerBIEmbed embedUrl={DEFAULT_POWERBI_URL} />
        </Suspense>
      </div>
    </div>
  );
}

// Versão sem autenticação (para desenvolvimento)
function PowerBIDashboardContentNoAuth() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">Dashboard Power BI</h1>
              <p className="text-sm text-muted-foreground">
                🔓 Modo de desenvolvimento - Autenticação desabilitada
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="container mx-auto px-4 py-6">
        <Suspense fallback={<LoadingFallback />}>
          <PowerBIEmbed embedUrl={DEFAULT_POWERBI_URL} />
        </Suspense>
      </div>
    </div>
  );
}

function LoadingFallback() {
  return (
    <Card className="p-8">
      <div className="flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    </Card>
  );
}

