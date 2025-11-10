"use client"

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  Database, 
  Clock, 
  AlertTriangle, 
  Server, 
  Cpu,
  MemoryStick,
  Network
} from 'lucide-react';
import { SystemMetrics } from '@/lib/api';

interface SystemMetricsProps {
  metrics: SystemMetrics;
  databaseInfo?: {
    tables_count: number;
    total_records: number;
    connection_pool_size: number;
  };
  isConnected?: boolean;
}

export const SystemMetricsComponent: React.FC<SystemMetricsProps> = ({ 
  metrics, 
  databaseInfo,
  isConnected = false 
}) => {
  const getStatusColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value <= thresholds.good) return 'text-green-500';
    if (value <= thresholds.warning) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusBadge = (value: number, thresholds: { good: number; warning: number }) => {
    if (value <= thresholds.good) return 'bg-green-100 text-green-800';
    if (value <= thresholds.warning) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* Requisições Hoje */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <span className="font-medium">Requisições Hoje</span>
          </div>
          <Badge variant="outline">{metrics.total_requests_today}</Badge>
        </div>
        <div className="text-2xl font-bold text-blue-600">
          {metrics.total_requests_today.toLocaleString()}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Total de chamadas da API
        </div>
      </Card>

      {/* Tempo de Resposta */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-green-500" />
            <span className="font-medium">Tempo de Resposta</span>
          </div>
          <Badge 
            className={getStatusBadge(metrics.avg_response_time, { good: 200, warning: 500 })}
          >
            {metrics.avg_response_time.toFixed(0)}ms
          </Badge>
        </div>
        <div className={`text-2xl font-bold ${getStatusColor(metrics.avg_response_time, { good: 200, warning: 500 })}`}>
          {metrics.avg_response_time.toFixed(0)}ms
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Média das últimas requisições
        </div>
      </Card>

      {/* Taxa de Erro */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span className="font-medium">Taxa de Erro</span>
          </div>
          <Badge 
            className={getStatusBadge(metrics.error_rate, { good: 2, warning: 5 })}
          >
            {metrics.error_rate.toFixed(1)}%
          </Badge>
        </div>
        <div className={`text-2xl font-bold ${getStatusColor(metrics.error_rate, { good: 2, warning: 5 })}`}>
          {metrics.error_rate.toFixed(1)}%
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Requisições com erro
        </div>
      </Card>

      {/* Conexões Ativas */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-purple-500" />
            <span className="font-medium">Conexões Ativas</span>
          </div>
          <Badge variant="outline">{metrics.active_connections}</Badge>
        </div>
        <div className="text-2xl font-bold text-purple-600">
          {metrics.active_connections}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Pool de conexões
        </div>
      </Card>

      {/* Uso de Memória */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <MemoryStick className="w-5 h-5 text-orange-500" />
            <span className="font-medium">Uso de Memória</span>
          </div>
          <Badge 
            className={getStatusBadge(metrics.memory_usage, { good: 60, warning: 80 })}
          >
            {metrics.memory_usage.toFixed(1)}%
          </Badge>
        </div>
        <div className="text-2xl font-bold text-orange-600">
          {metrics.memory_usage.toFixed(1)}%
        </div>
        <Progress 
          value={metrics.memory_usage} 
          className="mt-2"
        />
        <div className="text-xs text-gray-500 mt-1">
          RAM utilizada
        </div>
      </Card>

      {/* Uso de CPU */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-500" />
            <span className="font-medium">Uso de CPU</span>
          </div>
          <Badge 
            className={getStatusBadge(metrics.cpu_usage, { good: 50, warning: 80 })}
          >
            {metrics.cpu_usage.toFixed(1)}%
          </Badge>
        </div>
        <div className="text-2xl font-bold text-indigo-600">
          {metrics.cpu_usage.toFixed(1)}%
        </div>
        <Progress 
          value={metrics.cpu_usage} 
          className="mt-2"
        />
        <div className="text-xs text-gray-500 mt-1">
          Processamento
        </div>
      </Card>

      {/* Status do Banco de Dados */}
      {databaseInfo && (
        <Card className="p-4 md:col-span-2 lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-500" />
              <span className="font-medium">Banco de Dados</span>
            </div>
            <Badge 
              className={isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
            >
              {isConnected ? 'Conectado' : 'Desconectado'}
            </Badge>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {databaseInfo.tables_count}
              </div>
              <div className="text-xs text-gray-500">Tabelas</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {databaseInfo.total_records.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Registros</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {databaseInfo.connection_pool_size}
              </div>
              <div className="text-xs text-gray-500">Conexões</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default SystemMetricsComponent;
