"use client"

import { ReactNode } from "react";
import { useAuth } from "@/hooks/useAuth";
import SimpleMFA from "./SimpleMFA";
import { Loader2 } from "lucide-react";

interface AuthGuardProps {
  children: ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, loading, email } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-500" />
          <p className="text-muted-foreground">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <SimpleMFA onSuccess={() => {
          window.location.reload();
        }} />
      </div>
    );
  }

  return <>{children}</>;
}

