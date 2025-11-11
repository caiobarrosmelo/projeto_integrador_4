"use client"

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Shield, Loader2, AlertCircle } from "lucide-react";

interface SimpleMFAProps {
  onSuccess: (email: string) => void;
}

export default function SimpleMFA({ onSuccess }: SimpleMFAProps) {
  const [step, setStep] = useState<"login" | "verify">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Valida credenciais básicas antes de ir para MFA
      if (!email || !password) {
        setError("Email e senha são obrigatórios");
        setLoading(false);
        return;
      }

      // Verifica se é um usuário válido (em produção, fazer chamada à API)
      const emailLower = email.toLowerCase().trim();
      if (emailLower !== "admin@example.com" && emailLower !== "user@example.com") {
        setError("Usuário ou senha inválidos");
        setLoading(false);
        return;
      }

      // Verifica senha (em produção, fazer chamada à API)
      if (password !== "admin123") {
        setError("Usuário ou senha inválidos");
        setLoading(false);
        return;
      }

      // MFA já está configurado com secret fixo, vai direto para verificação
      setStep("verify");
    } catch (err) {
      setError("Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  };


  const handleVerifyMFA = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, token }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Erro na verificação");
      }

      onSuccess(email);
    } catch (err: any) {
      setError(err.message || "Código MFA inválido");
    } finally {
      setLoading(false);
    }
  };

  if (step === "login") {
    return (
      <Card className="w-full max-w-md p-8 space-y-6">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-4">
              <Shield className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div>
            <h1 className="text-2xl font-bold">Acesso Restrito</h1>
            <p className="text-muted-foreground mt-2">
              Faça login para acessar o dashboard Power BI
            </p>
          </div>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-3 flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Entrando...
              </>
            ) : (
              "Continuar"
            )}
          </Button>
        </form>

        <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800 dark:text-blue-200">
              <p className="font-semibold mb-1">Credenciais de Demo</p>
              <p>Email: admin@example.com</p>
              <p>Senha: admin123</p>
            </div>
          </div>
        </div>
      </Card>
    );
  }


  // Step: verify
  return (
    <Card className="w-full max-w-md p-8 space-y-6">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-purple-100 dark:bg-purple-900 p-4">
            <Shield className="h-8 w-8 text-purple-600 dark:text-purple-400" />
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-bold">Verificar Código MFA</h1>
          <p className="text-muted-foreground mt-2">
            Digite o código de 6 dígitos do seu app autenticador
          </p>
        </div>
      </div>

      <form onSubmit={handleVerifyMFA} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="token">Código MFA</Label>
          <Input
            id="token"
            type="text"
            placeholder="000000"
            value={token}
            onChange={(e) => setToken(e.target.value.replace(/\D/g, "").slice(0, 6))}
            maxLength={6}
            required
            className="text-center text-2xl tracking-widest font-mono"
          />
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-3 flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <Button type="submit" className="w-full" disabled={loading || token.length !== 6}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Verificando...
            </>
          ) : (
            "Verificar e Entrar"
          )}
        </Button>
      </form>
    </Card>
  );
}

