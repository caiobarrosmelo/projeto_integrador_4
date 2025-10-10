"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Clock, Thermometer } from "lucide-react"

interface BusArrival {
  id: string
  line: string
  arrivalTime: number // minutes
  capacity: number // 0-4
  lastUpdate: Date
}

interface WeatherData {
  temperature: number
  condition: string
}

export default function BusMonitorPage() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [weather, setWeather] = useState<WeatherData>({ temperature: 28, condition: "Ensolarado" })
  const [busArrivals, setBusArrivals] = useState<BusArrival[]>([
    {
      id: "1",
      line: "001 - Centro",
      arrivalTime: 3,
      capacity: 1,
      lastUpdate: new Date(),
    },
    {
      id: "2",
      line: "042 - Boa Viagem",
      arrivalTime: 7,
      capacity: 3,
      lastUpdate: new Date(),
    },
    {
      id: "3",
      line: "195 - Casa Amarela",
      arrivalTime: 12,
      capacity: 2,
      lastUpdate: new Date(),
    },
    {
      id: "4",
      line: "260 - Olinda",
      arrivalTime: 18,
      capacity: 0,
      lastUpdate: new Date(),
    },
    {
      id: "5",
      line: "350 - Jaboatão",
      arrivalTime: 25,
      capacity: 4,
      lastUpdate: new Date(),
    },
  ])

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Simulate bus arrivals updates
  useEffect(() => {
    const updateBuses = () => {
      setBusArrivals((prev) => {
        const updated = prev.map((bus) => ({
          ...bus,
          arrivalTime: Math.max(0, bus.arrivalTime - 1),
          capacity: Math.floor(Math.random() * 5), // Simulate capacity changes
          lastUpdate: new Date(),
        }))

        // Remove buses that have arrived and add new ones
        const activeBuses = updated.filter((bus) => bus.arrivalTime > 0)

        // Add new buses if needed
        while (activeBuses.length < 5) {
          const newBus: BusArrival = {
            id: Math.random().toString(36).substr(2, 9),
            line: `${Math.floor(Math.random() * 400)
              .toString()
              .padStart(
                3,
                "0",
              )} - ${["Centro", "Boa Viagem", "Casa Amarela", "Olinda", "Jaboatão"][Math.floor(Math.random() * 5)]}`,
            arrivalTime: Math.floor(Math.random() * 30) + 1,
            capacity: Math.floor(Math.random() * 5),
            lastUpdate: new Date(),
          }
          activeBuses.push(newBus)
        }

        return activeBuses.sort((a, b) => a.arrivalTime - b.arrivalTime)
      })
    }

    const interval = setInterval(updateBuses, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  const getCapacityText = (capacity: number) => {
    switch (capacity) {
      case 0:
        return "Vazio"
      case 1:
        return "Pouco cheio"
      case 2:
        return "Meio cheio"
      case 3:
        return "Cheio"
      case 4:
        return "Lotado"
      default:
        return "Desconhecido"
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const CapacityBars = ({ capacity }: { capacity: number }) => {
    return (
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((bar) => (
          <div
            key={bar}
            className={`w-3 h-6 rounded-sm ${
              bar < capacity
                ? "bg-white" // All filled bars are now white
                : "bg-[#1F1F1F]" // Changed empty bars color from #1E1E1E to #1F1F1F
            }`}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header with time and weather */}
        <Card className="p-6 text-center">
          <div className="flex items-center justify-center gap-8 mb-4">
            <div className="flex items-center gap-3">
              <Clock className="h-8 w-8 text-white" />
              <span className="text-4xl font-bold font-mono">{formatTime(currentTime)}</span>
            </div>
            <div className="flex items-center gap-3">
              <Thermometer className="h-8 w-8 text-white" />
              <span className="text-3xl font-semibold">{weather.temperature}°C</span>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mt-2">{weather.condition}</p>
        </Card>

        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">PRÓXIMOS ÔNIBUS</h1>
        </div>

        <div className="space-y-3">
          {busArrivals.map((bus, index) => (
            <Card key={bus.id} className="p-6">
              <div className="grid grid-cols-12 gap-4 items-center">
                {/* Linha do ônibus - ocupa o espaço necessário */}
                <div className="col-span-5">
                  <div className="text-2xl font-bold font-mono text-white">{bus.line}</div>
                </div>

                {/* Indicador de lotação - coluna fixa centralizada */}
                <div className="col-span-3 flex justify-center">
                  <div className="flex flex-col items-center gap-1">
                    <CapacityBars capacity={bus.capacity} />
                    <span className="text-xs text-gray-400">LOTAÇÃO</span>
                  </div>
                </div>

                {/* Tempo de chegada - coluna fixa à direita */}
                <div className="col-span-4 text-right">
                  <div className="text-5xl font-bold font-mono text-white">
                    {bus.arrivalTime === 0 ? "CHEGANDO" : bus.arrivalTime}
                  </div>
                  {bus.arrivalTime > 0 && <div className="text-lg text-gray-400 font-semibold">MINUTOS</div>}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground pt-4">
          <p>ATUALIZAÇÃO AUTOMÁTICA</p>
        </div>
      </div>
    </div>
  )
}
