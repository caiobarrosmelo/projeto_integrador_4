"use client";

import { Suspense } from "react";
import AuthGuard from "@/components/auth/AuthGuard";
import PowerBIEmbed from "@/components/powerbi/PowerBIEmbed";
import { Card } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

const DISABLE_AUTH = false;

const DEFAULT_POWERBI_URL =
  "https://app.powerbi.com/view?r=eyJrIjoiNGY2ZjZjM2ItNWJmYy00MDU5LThlZDQtYzU2ZjgxZGM1ZGU2IiwidCI6IjRhMjJmMTE2LTUxY2UtNGZlMy1hZWFhLTljNDYxNDNkMDg4YiJ9";

export default function DashboardPage() {
  if (DISABLE_AUTH) {
    return <PowerBIDashboardContentNoAuth />;
  }

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
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">Dashboard Power BI</h1>
              <p className="text-sm text-muted-foreground">Autenticado como: {email}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={logout} className="text-sm">
              Sair
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <Suspense fallback={<LoadingFallback />}>
          <PowerBIEmbed embedUrl={DEFAULT_POWERBI_URL} />
        </Suspense>
      </div>
    </div>
  );
}

function PowerBIDashboardContentNoAuth() {
  return (
    <div className="min-h-screen bg-background">
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">Dashboard Power BI</h1>
              <p className="text-sm text-muted-foreground">🔓 Modo de desenvolvimento - Autenticação desabilitada</p>
            </div>
          </div>
        </div>
      </div>

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
