/**
 * Cliente API para integração com o back-end
 * Sistema de Monitoramento IoT para Ônibus
 */

import React from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

export interface BusLocation {
  id: string;
  line_code: string;
  line_name: string;
  latitude: number;
  longitude: number;
  speed_kmh: number;
  last_update: string;
  status: 'active' | 'inactive';
  occupancy?: {
    level: number;
    name: string;
    person_count: number;
    confidence: number;
  };
  eta?: {
    minutes: number;
    confidence: number;
  };
}

export interface OccupancySummary {
  total_analyses: number;
  overall_confidence: number;
  distribution: {
    [key: string]: {
      count: number;
      percentage: number;
      avg_person_count: number;
      avg_confidence: number;
    };
  };
}

export interface ETASummary {
  total_predictions: number;
  avg_accuracy_minutes: number;
  avg_confidence_percent: number;
  by_method: {
    [key: string]: {
      count: number;
      avg_accuracy: number;
      avg_confidence: number;
    };
  };
  performance: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
  };
}

export interface SystemMetrics {
  total_requests_today: number;
  avg_response_time: number;
  error_rate: number;
  active_connections: number;
  memory_usage: number;
  cpu_usage: number;
}

export interface DashboardData {
  timestamp: string;
  system_status: {
    database_connected: boolean;
    total_active_buses: number;
    last_update: string;
    mode?: string;
  };
  current_buses: BusLocation[];
  occupancy_summary: OccupancySummary;
  eta_summary: ETASummary;
  system_metrics: SystemMetrics;
  database_info: {
    tables_count: number;
    total_records: number;
    connection_pool_size: number;
  };
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Dashboard APIs
  async getDashboardData(refresh: boolean = false): Promise<DashboardData> {
    const params = new URLSearchParams();
    if (refresh) params.append('refresh', 'true');
    
    return this.request<DashboardData>(`/api/dashboard/data?${params}`);
  }

  async getCurrentBuses(lineCode?: string, minutes: number = 5): Promise<{
    timestamp: string;
    count: number;
    buses: BusLocation[];
    filters: {
      line_code?: string;
      minutes: number;
    };
  }> {
    const params = new URLSearchParams();
    if (lineCode) params.append('line', lineCode);
    params.append('minutes', minutes.toString());
    
    return this.request(`/api/dashboard/buses?${params}`);
  }

  async getOccupancyData(lineCode?: string, hours: number = 24): Promise<{
    timestamp: string;
    occupancy_data: OccupancySummary;
    filters: {
      line_code?: string;
      hours: number;
    };
  }> {
    const params = new URLSearchParams();
    if (lineCode) params.append('line', lineCode);
    params.append('hours', hours.toString());
    
    return this.request(`/api/dashboard/occupancy?${params}`);
  }

  async getSystemMetrics(): Promise<{
    timestamp: string;
    system_metrics: SystemMetrics;
    database_metrics: any;
    api_metrics: any;
  }> {
    return this.request('/api/dashboard/metrics');
  }

  // Location APIs
  async sendLocation(data: {
    bus_line: string;
    latitude: number;
    longitude: number;
    timestamp?: string;
  }): Promise<any> {
    return this.request('/api/location', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getLocationHistory(busLine: string, limit: number = 50, hours: number = 24): Promise<any> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('hours', hours.toString());
    
    return this.request(`/api/location/history/${busLine}?${params}`);
  }

  // Image Analysis APIs
  async analyzeImage(data: {
    bus_line: string;
    image_data: string;
    timestamp?: string;
  }): Promise<any> {
    return this.request('/api/image/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getOccupancyHistory(busLine: string, limit: number = 20, hours: number = 24): Promise<any> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('hours', hours.toString());
    
    return this.request(`/api/image/occupancy/${busLine}?${params}`);
  }

  // Integrated APIs
  async sendLocationAndImage(data: {
    bus_line: string;
    latitude: number;
    longitude: number;
    image_data: string;
    timestamp?: string;
  }): Promise<any> {
    return this.request('/api/location-image', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getIntegratedStatus(busLine: string): Promise<any> {
    return this.request(`/api/integrated/status/${busLine}`);
  }

  // Health Checks
  async getHealth(): Promise<any> {
    return this.request('/health');
  }

  async getApiHealth(): Promise<any> {
    return this.request('/api/health');
  }

  async getDashboardHealth(): Promise<any> {
    return this.request('/api/dashboard/health');
  }

  async getImageHealth(): Promise<any> {
    return this.request('/api/image/health');
  }

  async getIntegratedHealth(): Promise<any> {
    return this.request('/api/integrated/health');
  }
}

// Instância singleton do cliente API
export const apiClient = new ApiClient();

// Hooks personalizados para React
export const useDashboardData = (refresh: boolean = false) => {
  const [data, setData] = React.useState<DashboardData | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiClient.getDashboardData(refresh);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [refresh]);

  return { data, loading, error, refetch: () => fetchData() };
};

export const useCurrentBuses = (lineCode?: string, minutes: number = 5) => {
  const [data, setData] = React.useState<BusLocation[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiClient.getCurrentBuses(lineCode, minutes);
        setData(result.buses);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Atualiza a cada 30 segundos
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [lineCode, minutes]);

  return { data, loading, error, refetch: () => fetchData() };
};

export const useOccupancyData = (lineCode?: string, hours: number = 24) => {
  const [data, setData] = React.useState<OccupancySummary | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiClient.getOccupancyData(lineCode, hours);
        setData(result.occupancy_data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [lineCode, hours]);

  return { data, loading, error, refetch: () => fetchData() };
};

export const useSystemMetrics = () => {
  const [data, setData] = React.useState<SystemMetrics | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiClient.getSystemMetrics();
        setData(result.system_metrics);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Atualiza a cada 60 segundos
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, refetch: () => fetchData() };
};

// Utilitários
export const formatTime = (dateString: string): string => {
  return new Date(dateString).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('pt-BR');
};

export const getOccupancyColor = (level: number): string => {
  const colors = {
    0: 'text-green-500', // Vazio
    1: 'text-yellow-500', // Baixa
    2: 'text-orange-500', // Média
    3: 'text-red-500', // Alta
    4: 'text-purple-500', // Lotado
  };
  return colors[level as keyof typeof colors] || 'text-gray-500';
};

export const getOccupancyBgColor = (level: number): string => {
  const colors = {
    0: 'bg-green-100 border-green-300', // Vazio
    1: 'bg-yellow-100 border-yellow-300', // Baixa
    2: 'bg-orange-100 border-orange-300', // Média
    3: 'bg-red-100 border-red-300', // Alta
    4: 'bg-purple-100 border-purple-300', // Lotado
  };
  return colors[level as keyof typeof colors] || 'bg-gray-100 border-gray-300';
};

export const getETAColor = (minutes: number): string => {
  if (minutes <= 5) return 'text-green-500';
  if (minutes <= 10) return 'text-yellow-500';
  if (minutes <= 20) return 'text-orange-500';
  return 'text-red-500';
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return 'text-green-500';
  if (confidence >= 60) return 'text-yellow-500';
  return 'text-red-500';
};

export default apiClient;
