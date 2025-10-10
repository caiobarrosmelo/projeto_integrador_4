// ========================================================
// Pipeline de Dados IoT - Backend Node.js
// Sistema de Monitoramento de Ônibus
// ========================================================

const express = require('express');
const { Pool } = require('pg');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json({ limit: '10mb' }));

// ========================================================
// CONFIGURAÇÃO DO BANCO DE DADOS POSTGRESQL
// ========================================================
const pool = new Pool({
  user: 'seu_usuario',
  host: 'localhost',
  database: 'bus_monitoring',
  password: 'sua_senha',
  port: 5432,
});

// Teste de conexão
pool.connect((err, client, release) => {
  if (err) {
    console.error('❌ Erro ao conectar ao PostgreSQL:', err.stack);
  } else {
    console.log('✅ Conectado ao PostgreSQL');
    release();
  }
});

// ========================================================
// FUNÇÕES DE VALIDAÇÃO E TRATAMENTO DE DADOS
// ========================================================

/**
 * Valida coordenadas GPS
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {boolean} - True se válidas
 */
function validateGPS(lat, lon) {
  return (
    typeof lat === 'number' &&
    typeof lon === 'number' &&
    lat >= -90 && lat <= 90 &&
    lon >= -180 && lon <= 180
  );
}

/**
 * Valida formato Base64
 * @param {string} base64 - String Base64
 * @returns {boolean} - True se válido
 */
function isValidBase64(base64) {
  if (!base64 || typeof base64 !== 'string') return false;
  const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/;
  return base64Regex.test(base64) && base64.length % 4 === 0;
}

/**
 * Limpa e valida linha do ônibus
 * @param {string} busLine - Identificador da linha
 * @returns {string|null} - Linha limpa ou null
 */
function sanitizeBusLine(busLine) {
  if (!busLine || typeof busLine !== 'string') return null;
  const cleaned = busLine.trim().toUpperCase();
  return cleaned.length > 0 && cleaned.length <= 30 ? cleaned : null;
}

/**
 * Converte timestamp mock em formato PostgreSQL
 * @param {string|number} timestamp - Timestamp em ms ou ISO
 * @returns {Date} - Objeto Date
 */
function parseTimestamp(timestamp) {
  if (!timestamp) return new Date();
  
  // Se for número (millis do ESP32), converte
  if (typeof timestamp === 'number' || /^\d+$/.test(timestamp)) {
    return new Date();  // Usa timestamp atual do servidor
  }
  
  // Se for ISO string, converte
  const date = new Date(timestamp);
  return isNaN(date.getTime()) ? new Date() : date;
}

/**
 * Decodifica Base64 para Buffer
 * @param {string} base64 - String Base64
 * @returns {Buffer|null} - Buffer ou null se inválido
 */
function decodeBase64ToBuffer(base64) {
  try {
    if (!isValidBase64(base64)) return null;
    return Buffer.from(base64, 'base64');
  } catch (error) {
    console.error('Erro ao decodificar Base64:', error);
    return null;
  }
}

// ========================================================
// FUNÇÕES DE DETECÇÃO DE ANOMALIAS
// ========================================================

/**
 * Detecta saltos anormais de localização (teleporte)
 * @param {number} lat - Nova latitude
 * @param {number} lon - Nova longitude
 * @param {string} busLine - Linha do ônibus
 * @returns {Promise<boolean>} - True se movimento é suspeito
 */
async function detectLocationAnomaly(lat, lon, busLine) {
  try {
    const result = await pool.query(
      `SELECT latitude, longitude, timestamp_location 
       FROM bus_location 
       WHERE bus_line = $1 
       ORDER BY timestamp_location DESC 
       LIMIT 1`,
      [busLine]
    );

    if (result.rows.length === 0) return false;

    const lastLat = result.rows[0].latitude;
    const lastLon = result.rows[0].longitude;
    const lastTime = new Date(result.rows[0].timestamp_location);
    const timeDiff = (Date.now() - lastTime.getTime()) / 1000; // segundos

    // Calcula distância aproximada (fórmula haversine simplificada)
    const R = 6371000; // Raio da Terra em metros
    const dLat = (lat - lastLat) * Math.PI / 180;
    const dLon = (lon - lastLon) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lastLat * Math.PI / 180) * Math.cos(lat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c; // metros

    // Velocidade em km/h
    const speed = (distance / timeDiff) * 3.6;

    // Ônibus urbano não deve ultrapassar 120 km/h
    if (speed > 120) {
      console.warn(`⚠️ Anomalia detectada: velocidade de ${speed.toFixed(2)} km/h`);
      return true;
    }

    return false;
  } catch (error) {
    console.error('Erro ao detectar anomalia:', error);
    return false;
  }
}

// ========================================================
// ENDPOINT PRINCIPAL: /data
// ========================================================

app.post('/data', async (req, res) => {
  const client = await pool.connect();
  
  try {
    console.log('\n📡 Dados recebidos do ESP32');
    
    // ========== ETAPA 1: VALIDAÇÃO INICIAL ==========
    const { bus_line, latitude, longitude, timestamp, image_base64 } = req.body;

    // Valida presença de campos obrigatórios
    if (!bus_line || latitude === undefined || longitude === undefined) {
      return res.status(400).json({ 
        error: 'Campos obrigatórios ausentes',
        required: ['bus_line', 'latitude', 'longitude']
      });
    }

    // ========== ETAPA 2: LIMPEZA E SANITIZAÇÃO ==========
    const cleanBusLine = sanitizeBusLine(bus_line);
    if (!cleanBusLine) {
      return res.status(400).json({ error: 'Linha do ônibus inválida' });
    }

    const lat = parseFloat(latitude);
    const lon = parseFloat(longitude);
    
    if (!validateGPS(lat, lon)) {
      return res.status(400).json({ error: 'Coordenadas GPS inválidas' });
    }

    const timestampLocation = parseTimestamp(timestamp);

    console.log(`✅ Dados validados: ${cleanBusLine} [${lat}, ${lon}]`);

    // ========== ETAPA 3: DETECÇÃO DE ANOMALIAS ==========
    const isAnomaly = await detectLocationAnomaly(lat, lon, cleanBusLine);
    if (isAnomaly) {
      console.warn('⚠️ Dados rejeitados por anomalia de velocidade');
      return res.status(422).json({ 
        error: 'Anomalia detectada: movimento suspeito',
        tip: 'Verifique o sensor GPS'
      });
    }

    // ========== ETAPA 4: TRANSAÇÃO NO BANCO ==========
    await client.query('BEGIN');

    // Insere localização
    const locationResult = await client.query(
      `INSERT INTO bus_location (bus_line, timestamp_location, latitude, longitude)
       VALUES ($1, $2, $3, $4)
       RETURNING id`,
      [cleanBusLine, timestampLocation, lat, lon]
    );

    const locationId = locationResult.rows[0].id;
    console.log(`✅ Localização inserida: ID ${locationId}`);

    // Processa imagem se presente
    if (image_base64) {
      const imageBuffer = decodeBase64ToBuffer(image_base64);
      
      if (!imageBuffer) {
        console.warn('⚠️ Imagem Base64 inválida, continuando sem imagem');
      } else if (imageBuffer.length > 5 * 1024 * 1024) {
        console.warn('⚠️ Imagem muito grande (>5MB), rejeitada');
      } else {
        await client.query(
          `INSERT INTO bus_image (location_id, image_data, timestamp_image)
           VALUES ($1, $2, $3)`,
          [locationId, imageBuffer, timestampLocation]
        );
        console.log(`✅ Imagem inserida: ${imageBuffer.length} bytes`);
      }
    }

    await client.query('COMMIT');

    // ========== ETAPA 5: RESPOSTA DE SUCESSO ==========
    res.status(201).json({
      success: true,
      location_id: locationId,
      message: 'Dados armazenados com sucesso',
      timestamp: timestampLocation.toISOString()
    });

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ Erro no pipeline:', error);
    res.status(500).json({ 
      error: 'Erro interno do servidor',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  } finally {
    client.release();
  }
});

// ========================================================
// ENDPOINT DE HEALTH CHECK
// ========================================================

app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ 
      status: 'healthy',
      database: 'connected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({ 
      status: 'unhealthy',
      database: 'disconnected',
      error: error.message
    });
  }
});

// ========================================================
// ENDPOINT DE ESTATÍSTICAS
// ========================================================

app.get('/stats', async (req, res) => {
  try {
    const locationCount = await pool.query('SELECT COUNT(*) FROM bus_location');
    const imageCount = await pool.query('SELECT COUNT(*) FROM bus_image');
    const busLines = await pool.query('SELECT DISTINCT bus_line FROM bus_location');

    res.json({
      total_locations: parseInt(locationCount.rows[0].count),
      total_images: parseInt(imageCount.rows[0].count),
      active_lines: busLines.rows.map(r => r.bus_line)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ========================================================
// INICIALIZAÇÃO DO SERVIDOR
// ========================================================

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🚀 Servidor IoT rodando na porta ${PORT}`);
  console.log(`📍 Endpoint principal: http://localhost:${PORT}/data`);
  console.log(`💚 Health check: http://localhost:${PORT}/health`);
  console.log(`📊 Estatísticas: http://localhost:${PORT}/stats\n`);
});

// Tratamento de encerramento gracioso
process.on('SIGINT', async () => {
  console.log('\n🛑 Encerrando servidor...');
  await pool.end();
  process.exit(0);
});