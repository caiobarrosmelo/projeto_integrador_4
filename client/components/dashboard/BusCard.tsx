"use client"

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Users, MapPin, Activity } from 'lucide-react';
import { BusLocation, formatTime, getOccupancyColor, getOccupancyBgColor, getETAColor, getConfidenceColor } from '@/lib/api';

interface BusCardProps {
  bus: BusLocation;
  showDetails?: boolean;
}

export const BusCard: React.FC<BusCardProps> = ({ bus, showDetails = false }) => {
  const getOccupancyBars = (level: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <div
        key={i}
        className={`w-2 h-4 rounded-sm ${
          i < level ? 'bg-current' : 'bg-gray-300'
        }`}
      />
    ));
  };

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'bg-green-500' : 'bg-red-500';
  };

  return (
    <Card className={`p-4 transition-all duration-200 hover:shadow-lg ${getOccupancyBgColor(bus.occupancy?.level || 0)}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor(bus.status)}`} />
          <h3 className="font-bold text-lg">{bus.line_code}</h3>
          <Badge variant="outline" className="text-xs">
            {bus.line_name}
          </Badge>
        </div>
        <div className="text-xs text-gray-500">
          {formatTime(bus.last_update)}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* ETA */}
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-600" />
          <div>
            <div className={`text-2xl font-bold ${getETAColor(bus.eta?.minutes || 0)}`}>
              {bus.eta?.minutes || 'N/A'}
            </div>
            <div className="text-xs text-gray-500">min</div>
          </div>
        </div>

        {/* Ocupação */}
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-gray-600" />
          <div>
            <div className={`text-lg font-semibold ${getOccupancyColor(bus.occupancy?.level || 0)}`}>
              {bus.occupancy?.name || 'N/A'}
            </div>
            <div className="text-xs text-gray-500">
              {bus.occupancy?.person_count || 0} pessoas
            </div>
          </div>
        </div>
      </div>

      {/* Barras de ocupação */}
      {bus.occupancy && (
        <div className="mt-3 flex items-center gap-2">
          <span className="text-xs text-gray-500">Ocupação:</span>
          <div className={`flex gap-1 ${getOccupancyColor(bus.occupancy.level)}`}>
            {getOccupancyBars(bus.occupancy.level)}
          </div>
        </div>
      )}

      {/* Detalhes expandidos */}
      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gray-600" />
              <div>
                <div className="font-medium">Localização</div>
                <div className="text-xs text-gray-500">
                  {bus.latitude.toFixed(4)}, {bus.longitude.toFixed(4)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-gray-600" />
              <div>
                <div className="font-medium">Velocidade</div>
                <div className="text-xs text-gray-500">
                  {bus.speed_kmh} km/h
                </div>
              </div>
            </div>
          </div>

          {/* Confiança */}
          {(bus.occupancy?.confidence || bus.eta?.confidence) && (
            <div className="mt-3 flex gap-4 text-xs">
              {bus.occupancy?.confidence && (
                <div className="flex items-center gap-1">
                  <span className="text-gray-500">Conf. Ocupação:</span>
                  <span className={getConfidenceColor(bus.occupancy.confidence)}>
                    {bus.occupancy.confidence.toFixed(1)}%
                  </span>
                </div>
              )}
              {bus.eta?.confidence && (
                <div className="flex items-center gap-1">
                  <span className="text-gray-500">Conf. ETA:</span>
                  <span className={getConfidenceColor(bus.eta.confidence)}>
                    {bus.eta.confidence.toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default BusCard;
