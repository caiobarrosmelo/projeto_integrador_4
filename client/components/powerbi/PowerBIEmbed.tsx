"use client"

import { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle, Settings } from "lucide-react";

interface PowerBIEmbedProps {
  embedUrl?: string;
}

export default function PowerBIEmbed({ embedUrl: embedUrlProp }: PowerBIEmbedProps) {
  // Prioridade: prop > localStorage > vazio
  const getInitialUrl = () => {
    if (embedUrlProp) return embedUrlProp;
    const savedUrl = localStorage.getItem("powerbi_embed_url");
    return savedUrl || "";
  };

  const [embedUrl, setEmbedUrl] = useState(getInitialUrl());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Atualiza quando a prop mudar
  useEffect(() => {
    if (embedUrlProp) {
      setEmbedUrl(embedUrlProp);
      // Salva no localStorage para persistência
      localStorage.setItem("powerbi_embed_url", embedUrlProp);
    }
  }, [embedUrlProp]);

  const handleLoad = () => {
    setIsLoading(false);
    setError(null);
  };

  const handleError = () => {
    setIsLoading(false);
    setError("Erro ao carregar o relatório Power BI. Verifique se a URL está correta e se você tem permissão de acesso.");
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmbedUrl(e.target.value);
    setError(null);
  };

  const handleSaveUrl = () => {
    if (embedUrl) {
      localStorage.setItem("powerbi_embed_url", embedUrl);
      setIsLoading(true);
      // Recarrega o iframe
      if (iframeRef.current) {
        iframeRef.current.src = embedUrl;
      }
    }
  };

  const handleOpenInNewTab = () => {
    if (embedUrl) {
      window.open(embedUrl, "_blank");
    }
  };

  // Valida se é uma URL do Power BI
  const isValidPowerBIUrl = (url: string) => {
    return url.includes("powerbi.com") || url.includes("app.powerbi.com");
  };

  if (!embedUrl) {
    return (
      <Card className="p-8">
        <div className="space-y-6">
          <div className="text-center space-y-2">
            <Settings className="h-12 w-12 mx-auto text-muted-foreground" />
            <h2 className="text-2xl font-semibold">Configurar Power BI</h2>
            <p className="text-muted-foreground">
              Cole o link de embed do seu relatório Power BI abaixo
            </p>
          </div>

          <div className="space-y-4 max-w-2xl mx-auto">
            <div>
              <label className="text-sm font-medium mb-2 block">
                URL do Relatório Power BI
              </label>
              <Input
                type="url"
                placeholder="https://app.powerbi.com/view?r=..."
                value={embedUrl}
                onChange={handleUrlChange}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Para obter a URL: No Power BI, vá em Arquivo → Incorporar → Publicar na Web (ou use a URL de embed)
              </p>
            </div>

            <Button 
              onClick={handleSaveUrl} 
              disabled={!embedUrl || !isValidPowerBIUrl(embedUrl)}
              className="w-full"
            >
              Salvar e Carregar
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Container do Power BI */}
      <Card className="p-0 overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
            <div className="text-center space-y-2">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-500" />
              <p className="text-sm text-muted-foreground">Carregando relatório...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="p-8 text-center space-y-4">
            <div className="text-red-500">
              <AlertCircle className="h-12 w-12 mx-auto mb-2" />
              <p className="font-semibold">Erro ao carregar</p>
              <p className="text-sm mt-2">{error}</p>
            </div>
            <Button variant="outline" onClick={handleSaveUrl}>
              Tentar Novamente
            </Button>
          </div>
        )}

        <div className="relative w-full" style={{ paddingBottom: "56.25%" /* 16:9 aspect ratio */ }}>
          <iframe
            ref={iframeRef}
            src={embedUrl}
            className="absolute inset-0 w-full h-full border-0"
            title="Power BI Dashboard"
            allowFullScreen
            onLoad={handleLoad}
            onError={handleError}
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
          />
        </div>
      </Card>
    </div>
  );
}


