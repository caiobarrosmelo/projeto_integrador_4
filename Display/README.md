# Display Totem

## Tecnologias

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide React (ícones)

## Como executar

1. Instale as dependências:
```bash
npm install
```

2. Execute o projeto:
```bash
npm run dev
```

3. Acesse `http://localhost:3000`

## Estrutura do Projeto

- `app/` - Páginas e layouts da aplicação
- `components/` - Componentes reutilizáveis
- `lib/` - Utilitários e configurações

## Próximos Passos
- `app/page.tsx` - Substituir o array busArrivals inicial e o useEffect de simulação por chamadas para suas APIs reais

```javascript
// Substitua por:
useEffect(() => {
  const fetchBusData = async () => {
    try {
      const response = await fetch('/api/bus-arrivals') // Sua API
      const data = await response.json()
      setBusArrivals(data)
    } catch (error) {
      console.error('Erro ao buscar dados dos ônibus:', error)
    }
  }
  
  fetchBusData()
  const interval = setInterval(fetchBusData, 30000) // Atualiza a cada 30s
  return () => clearInterval(interval)
}, [])
```
### **Estrutura dos dados esperados:**

- **Ônibus**: `{ id, line, arrivalTime, capacity }`

### **Dados da temperatura**(linha 13):

Substitua os dados fixos por uma API de clima:

```javascript
// Substitua por:
useEffect(() => {
  const fetchWeather = async () => {
    try {
      const response = await fetch('/api/weather') // Sua API de clima
      const data = await response.json()
      setWeather(data)
    } catch (error) {
      console.error('Erro ao buscar dados do clima:', error)
    }
  }
  
  fetchWeather()
  const interval = setInterval(fetchWeather, 300000) // Atualiza a cada 5min
  return () => clearInterval(interval)
}, [])
```
### **Estrutura dos dados esperados:**
- **Clima**: `{ temperature, condition }`
