"use client"

import { useState, useEffect } from "react";

interface AuthState {
  isAuthenticated: boolean;
  email: string | null;
  loading: boolean;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    email: null,
    loading: true,
  });

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch("/api/auth/verify");
      if (response.ok) {
        const data = await response.json();
        setAuthState({
          isAuthenticated: true,
          email: data.email,
          loading: false,
        });
      } else {
        setAuthState({
          isAuthenticated: false,
          email: null,
          loading: false,
        });
      }
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        email: null,
        loading: false,
      });
    }
  };

  const logout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
      setAuthState({
        isAuthenticated: false,
        email: null,
        loading: false,
      });
      window.location.href = "/dashboard";
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
    }
  };

  return {
    ...authState,
    logout,
    refetch: checkAuth,
  };
}

