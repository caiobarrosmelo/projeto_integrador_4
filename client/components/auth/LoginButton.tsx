"use client"

import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/lib/msalConfig";
import { Button } from "@/components/ui/button";
import { LogIn, Loader2 } from "lucide-react";
import { useState } from "react";

export default function LoginButton() {
  const { instance } = useMsal();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    try {
      setIsLoading(true);
      
      // Tenta login com popup (mais suave)
      await instance.loginPopup(loginRequest);
    } catch (error: any) {
      console.error("Erro no login:", error);
      
      // Se popup falhar, tenta redirect
      if (error.errorCode === "popup_window_error" || error.errorCode === "user_cancelled") {
        try {
          await instance.loginRedirect(loginRequest);
        } catch (redirectError) {
          console.error("Erro no redirect:", redirectError);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button 
      onClick={handleLogin} 
      disabled={isLoading}
      className="w-full"
      size="lg"
    >
      {isLoading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Entrando...
        </>
      ) : (
        <>
          <LogIn className="mr-2 h-4 w-4" />
          Entrar com Microsoft
        </>
      )}
    </Button>
  );
}

