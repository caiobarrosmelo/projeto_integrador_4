"use client"

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RefreshCw, Wifi, WifiOff, Activity, Users, Clock } from 'lucide-react';
import { 
  useDashboardData, 
  useCurrentBuses, 
  useOccupancyData, 
  useSystemMetrics,
  DashboardData,
  BusLocation,
  OccupancySummary,
  SystemMetrics
} from '@/lib/api';
import BusCard from '@/components/dashboard/BusCard';
import SystemMetricsComponent from '@/components/dashboard/SystemMetrics';

export default function DashboardPage() {
  const [refresh, setRefresh] = useState(false);
  const [selectedLine, setSelectedLine] = useState<string>('');
  const [showDetails, setShowDetails] = useState(false);

  // Hooks para dados
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError, refetch: refetchDashboard } = useDashboardData(refresh);
  const { data: buses, loading: busesLoading, error: busesError } = useCurrentBuses(selectedLine || undefined);
  const { data: occupancyData, loading: occupancyLoading, error: occupancyError } = useOccupancyData(selectedLine || undefined);
  const { data: systemMetrics, loading: metricsLoading, error: metricsError } = useSystemMetrics();

  // Atualiza dados automaticamente
  useEffect(() => {
    const interval = setInterval(() => {
      setRefresh(prev => !prev);
    }, 30000); // Atualiza a cada 30 segundos

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefresh(prev => !prev);
    refetchDashboard();
  };

  const getConnectionStatus = () => {
    if (dashboardData?.system_status.database_connected) {
      return {
        status: 'connected',
        icon: <Wifi className="w-4 h-4 text-green-500" />,
        text: 'Conectado',
        color: 'text-green-500'
      };
    } else {
      return {
        status: 'disconnected',
        icon: <WifiOff className="w-4 h-4 text-red-500" />,
        text: 'Modo Fallback',
        color: 'text-red-500'
      };
    }
  };

  const connectionStatus = getConnectionStatus();

  if (dashboardLoading && !dashboardData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-lg">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  if (dashboardError && !dashboardData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <WifiOff className="w-8 h-8 mx-auto mb-4 text-red-500" />
          <p className="text-lg text-red-500">Erro ao carregar dashboard</p>
          <p className="text-sm text-gray-500 mt-2">{dashboardError}</p>
          <Button onClick={handleRefresh} className="mt-4">
            <RefreshCw className="w-4 h-4 mr-2" />
            Tentar Novamente
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Dashboard de Monitoramento</h1>
              <p className="text-sm text-muted-foreground">
                Sistema IoT para Ônibus - Tempo Real
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                {connectionStatus.icon}
                <span className={`text-sm font-medium ${connectionStatus.color}`}>
                  {connectionStatus.text}
                </span>
              </div>
              
              <Button onClick={handleRefresh} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Atualizar
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="buses">Ônibus Ativos</TabsTrigger>
            <TabsTrigger value="occupancy">Ocupação</TabsTrigger>
            <TabsTrigger value="metrics">Métricas</TabsTrigger>
          </TabsList>

          {/* Visão Geral */}
          <TabsContent value="overview" className="space-y-6">
            {/* Status do Sistema */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Status do Sistema</h2>
                <Badge variant={dashboardData?.system_status.database_connected ? "default" : "destructive"}>
                  {dashboardData?.system_status.database_connected ? "Online" : "Modo Fallback"}
                </Badge>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {dashboardData?.system_status.total_active_buses || 0}
                  </div>
                  <div className="text-sm text-gray-500">Ônibus Ativos</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {dashboardData?.occupancy_summary.total_analyses || 0}
                  </div>
                  <div className="text-sm text-gray-500">Análises Hoje</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {dashboardData?.eta_summary.total_predictions || 0}
                  </div>
                  <div className="text-sm text-gray-500">Previsões ETA</div>
                </div>
              </div>
            </Card>

            {/* Ônibus em Destaque */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Ônibus em Tempo Real</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {buses?.slice(0, 6).map((bus) => (
                  <BusCard key={bus.id} bus={bus} showDetails={showDetails} />
                ))}
              </div>
              
              <div className="mt-4 flex justify-center">
                <Button 
                  variant="outline" 
                  onClick={() => setShowDetails(!showDetails)}
                >
                  {showDetails ? 'Ocultar Detalhes' : 'Mostrar Detalhes'}
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* Ônibus Ativos */}
          <TabsContent value="buses" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Ônibus Ativos</h2>
              
              <div className="flex items-center gap-2">
                <select 
                  value={selectedLine} 
                  onChange={(e) => setSelectedLine(e.target.value)}
                  className="px-3 py-1 border rounded-md text-sm"
                >
                  <option value="">Todas as Linhas</option>
                  <option value="L1">L1 - Centro</option>
                  <option value="L2">L2 - Boa Viagem</option>
                  <option value="L3">L3 - Casa Amarela</option>
                  <option value="L4">L4 - Olinda</option>
                  <option value="BRT-1">BRT-1 - Aeroporto</option>
                </select>
              </div>
            </div>

            {busesLoading ? (
              <div className="text-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                <p>Carregando ônibus...</p>
              </div>
            ) : busesError ? (
              <div className="text-center py-8">
                <p className="text-red-500">Erro ao carregar ônibus: {busesError}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {buses?.map((bus) => (
                  <BusCard key={bus.id} bus={bus} showDetails={true} />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Ocupação */}
          <TabsContent value="occupancy" className="space-y-6">
            <h2 className="text-xl font-semibold">Análise de Ocupação</h2>
            
            {occupancyLoading ? (
              <div className="text-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                <p>Carregando dados de ocupação...</p>
              </div>
            ) : occupancyError ? (
              <div className="text-center py-8">
                <p className="text-red-500">Erro ao carregar ocupação: {occupancyError}</p>
              </div>
            ) : occupancyData ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Resumo */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Resumo Geral</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Total de Análises:</span>
                      <span className="font-semibold">{occupancyData.total_analyses}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Confiança Média:</span>
                      <span className="font-semibold">{occupancyData.overall_confidence.toFixed(1)}%</span>
                    </div>
                  </div>
                </Card>

                {/* Distribuição */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Distribuição por Nível</h3>
                  <div className="space-y-3">
                    {Object.entries(occupancyData.distribution).map(([level, data]) => (
                      <div key={level} className="flex items-center justify-between">
                        <span className="capitalize">{level}:</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">
                            {data.count} ({data.percentage.toFixed(1)}%)
                          </span>
                          <Badge variant="outline">
                            {data.avg_person_count.toFixed(0)} pessoas
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            ) : null}
          </TabsContent>

          {/* Métricas */}
          <TabsContent value="metrics" className="space-y-6">
            <h2 className="text-xl font-semibold">Métricas do Sistema</h2>
            
            {metricsLoading ? (
              <div className="text-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                <p>Carregando métricas...</p>
              </div>
            ) : metricsError ? (
              <div className="text-center py-8">
                <p className="text-red-500">Erro ao carregar métricas: {metricsError}</p>
              </div>
            ) : systemMetrics ? (
              <SystemMetricsComponent 
                metrics={systemMetrics}
                databaseInfo={dashboardData?.database_info}
                isConnected={dashboardData?.system_status.database_connected}
              />
            ) : null}
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <div className="border-t bg-card mt-8">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div>
              Última atualização: {dashboardData?.system_status.last_update ? 
                new Date(dashboardData.system_status.last_update).toLocaleString('pt-BR') : 
                'N/A'
              }
            </div>
            <div>
              Sistema de Monitoramento IoT - Projeto Integrador
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
