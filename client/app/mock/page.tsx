"use client"

import Link from "next/link"
import { useEffect, useMemo, useState } from "react"
import { AlertTriangle, Clock, RefreshCw, Thermometer } from "lucide-react"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useCurrentBuses } from "@/lib/api"

type NormalizedBus = {
  id: string
  line: string
  arrivalMinutes: number | null
  capacity: number
  lastUpdate: string
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  })
}

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
      return "Sem dado"
  }
}

const CapacityBars = ({ capacity }: { capacity: number }) => {
  return (
    <div className="flex gap-1">
      {[0, 1, 2, 3].map((bar) => (
        <div
          key={bar}
          className={`w-3 h-6 rounded-sm ${bar < capacity ? "bg-white" : "bg-[#1F1F1F]"}`}
        />
      ))}
    </div>
  )
}

export default function RealTimeArrivalsPage() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const { data: buses, loading, error, refetch } = useCurrentBuses(undefined, 10)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const normalizedBuses = useMemo<NormalizedBus[]>(() => {
    if (!buses) return []

    return buses
      .map((bus) => ({
        id: bus.id,
        line: `${bus.line_code} - ${bus.line_name}`,
        arrivalMinutes: typeof bus.eta?.minutes === "number" ? Math.max(0, Math.round(bus.eta.minutes)) : null,
        capacity: bus.occupancy?.level ?? 0,
        lastUpdate: bus.last_update,
      }))
      .sort((a, b) => {
        const aMinutes = a.arrivalMinutes ?? Number.POSITIVE_INFINITY
        const bMinutes = b.arrivalMinutes ?? Number.POSITIVE_INFINITY
        return aMinutes - bMinutes
      })
  }, [buses])

  return (
    <div className="min-h-screen bg-background text-foreground p-4">
      <div className="max-w-3xl mx-auto space-y-6">
        <Card className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
            <div className="flex items-center gap-3">
              <Clock className="h-8 w-8 text-white" />
              <span className="text-4xl font-bold font-mono">{formatTime(currentTime)}</span>
            </div>
            <div className="flex items-center gap-3">
              <Thermometer className="h-8 w-8 text-white" />
              <span className="text-3xl font-semibold">28°C</span>
            </div>
          </div>
        </Card>

        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">Próximos Ônibus</h1>
        </div>

        <div className="flex justify-end">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Atualizar agora
          </Button>
        </div>

        {loading && (
          <Card className="p-6 text-center">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
            <p>Carregando dados em tempo real...</p>
          </Card>
        )}

        {error && (
          <Card className="p-6 text-center border-destructive/50">
            <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-destructive" />
            <p className="text-destructive font-semibold">Erro ao buscar dados: {error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Verifique se o backend em <code>http://localhost:3000</code> está ativo.
            </p>
          </Card>
        )}

        {!loading && !error && (
          <div className="space-y-3">
            {normalizedBuses.length === 0 ? (
              <Card className="p-6 text-center text-muted-foreground">
                Nenhum ônibus ativo nos últimos minutos. Tente novamente em instantes ou abra o dashboard completo.
              </Card>
            ) : (
              normalizedBuses.map((bus) => (
                <Card key={bus.id} className="p-6">
                  <div className="grid grid-cols-12 gap-4 items-center">
                    <div className="col-span-12 md:col-span-5">
                      <div className="text-2xl font-bold font-mono text-white">{bus.line}</div>
                    </div>
                    <div className="col-span-6 md:col-span-3 flex flex-col items-center gap-1">
                      <CapacityBars capacity={bus.capacity} />
                      <span className="text-xs text-gray-400">LOTAÇÃO · {getCapacityText(bus.capacity).toUpperCase()}</span>
                    </div>
                    <div className="col-span-6 md:col-span-4 text-right">
                      <div className="text-5xl font-bold font-mono text-white">
                        {bus.arrivalMinutes === null ? "--" : bus.arrivalMinutes === 0 ? "AGORA" : bus.arrivalMinutes}
                      </div>
                      <div className="text-lg text-gray-400 font-semibold">
                        {bus.arrivalMinutes === null ? "ETA indisponível" : "MINUTOS"}
                      </div>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        <div className="text-center text-sm text-muted-foreground pt-4 space-y-1">
          <p>Atualizações automáticas a cada 30 segundos </p>
          <p>
            Dados fornecidos pela API Flask ·{" "}
            <Link href="/mock" className="underline">
              Ver modo mock
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

