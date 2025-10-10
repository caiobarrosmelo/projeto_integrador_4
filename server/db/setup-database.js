// ========================================================
// Script de Setup Automático do Banco de Dados
// ========================================================
// Uso: node scripts/setup-database.js
// ========================================================

const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

// Configuração do banco
const config = {
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  password: process.env.DB_PASSWORD || 'sua_senha',
  port: process.env.DB_PORT || 5432,
};

// SQL para criar o banco de dados
const CREATE_DATABASE = `
CREATE DATABASE bus_monitoring
WITH ENCODING = 'UTF8'
     LC_COLLATE = 'en_US.UTF-8'
     LC_CTYPE = 'en_US.UTF-8'
     TEMPLATE = template0;
`;

// SQL para criar as tabelas
const CREATE_TABLES = `
-- Tabela: bus_location
CREATE TABLE IF NOT EXISTS bus_location (
    id SERIAL PRIMARY KEY,
    bus_line VARCHAR(30) NOT NULL,
    timestamp_location TIMESTAMP NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

-- Tabela: bus_image
CREATE TABLE IF NOT EXISTS bus_image (
    id SERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    image_data BYTEA NOT NULL,
    timestamp_image TIMESTAMP NOT NULL,
    occupancy_count SMALLINT,
    CONSTRAINT fk_bus_image_location
        FOREIGN KEY(location_id)
        REFERENCES bus_location(id)
        ON DELETE CASCADE
);

-- Tabela: request_interval
CREATE TABLE IF NOT EXISTS request_interval (
    id SERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    interval_seconds SMALLINT NOT NULL,
    CONSTRAINT fk_request_interval_location
        FOREIGN KEY(location_id)
        REFERENCES bus_location(id)
        ON DELETE CASCADE
);

-- Tabela: prediction_confidence
CREATE TABLE IF NOT EXISTS prediction_confidence (
    id SERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    predicted_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP,
    confidence_percent DECIMAL(5,2),
    timestamp_prediction TIMESTAMP NOT NULL,
    CONSTRAINT fk_prediction_confidence_location
        FOREIGN KEY(location_id)
        REFERENCES bus_location(id)
        ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_bus_location_line_time 
    ON bus_location(bus_line, timestamp_location DESC);

CREATE INDEX IF NOT EXISTS idx_bus_location_time 
    ON bus_location(timestamp_location DESC);

CREATE INDEX IF NOT EXISTS idx_bus_image_location 
    ON bus_image(location_id);

CREATE INDEX IF NOT EXISTS idx_bus_location_coords 
    ON bus_location(latitude, longitude);

-- Views úteis
CREATE OR REPLACE VIEW v_locations_with_images AS
SELECT 
    bl.id,
    bl.bus_line,
    bl.timestamp_location,
    bl.latitude,
    bl.longitude,
    bi.id IS NOT NULL as tem_imagem,
    LENGTH(bi.image_data) as tamanho_imagem
FROM bus_location bl
LEFT JOIN bus_image bi ON bi.location_id = bl.id;

CREATE OR REPLACE VIEW v_stats_realtime AS
SELECT 
    (SELECT COUNT(*) FROM bus_location) as total_localizacoes,
    (SELECT COUNT(*) FROM bus_image) as total_imagens,
    (SELECT COUNT(DISTINCT bus_line) FROM bus_location) as linhas_ativas,
    (SELECT pg_size_pretty(pg_database_size(current_database()))) as tamanho_banco,
    (SELECT MAX(timestamp_location) FROM bus_location) as ultima_atualizacao;
`;

// Função principal
async function setupDatabase() {
  console.log('========================================');
  console.log('🚀 Setup do Banco de Dados');
  console.log('========================================\n');

  // Conecta ao PostgreSQL (sem especificar banco)
  const clientDefault = new Client(config);

  try {
    await clientDefault.connect();
    console.log('✅ Conectado ao PostgreSQL\n');

    // Verifica se o banco já existe
    const result = await clientDefault.query(
      "SELECT 1 FROM pg_database WHERE datname = 'bus_monitoring'"
    );

    if (result.rows.length === 0) {
      console.log('📦 Criando banco de dados bus_monitoring...');
      await clientDefault.query(CREATE_DATABASE);
      console.log('✅ Banco de dados criado com sucesso!\n');
    } else {
      console.log('ℹ️  Banco de dados bus_monitoring já existe\n');
    }

    await clientDefault.end();

    // Conecta ao banco específico para criar tabelas
    const clientBus = new Client({
      ...config,
      database: 'bus_monitoring'
    });

    await clientBus.connect();
    console.log('✅ Conectado ao banco bus_monitoring\n');

    // Cria tabelas, índices e views
    console.log('🔨 Criando estrutura do banco...');
    await clientBus.query(CREATE_TABLES);
    console.log('✅ Tabelas criadas com sucesso!\n');

    // Verifica estrutura criada
    const tables = await clientBus.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_type = 'BASE TABLE'
      ORDER BY table_name
    `);

    console.log('📋 Tabelas criadas:');
    tables.rows.forEach(row => {
      console.log(`   ✓ ${row.table_name}`);
    });

    const views = await clientBus.query(`
      SELECT table_name 
      FROM information_schema.views 
      WHERE table_schema = 'public'
      ORDER BY table_name
    `);

    console.log('\n👁️  Views criadas:');
    views.rows.forEach(row => {
      console.log(`   ✓ ${row.table_name}`);
    });

    const indexes = await clientBus.query(`
      SELECT indexname 
      FROM pg_indexes 
      WHERE schemaname = 'public'
      AND indexname NOT LIKE '%_pkey'
      ORDER BY indexname
    `);

    console.log('\n🔍 Índices criados:');
    indexes.rows.forEach(row => {
      console.log(`   ✓ ${row.indexname}`);
    });

    await clientBus.end();

    console.log('\n========================================');
    console.log('✅ Setup concluído com sucesso!');
    console.log('========================================');
    console.log('\n📝 Próximos passos:');
    console.log('   1. Configure o arquivo .env');
    console.log('   2. Execute: npm start');
    console.log('   3. Configure o ESP32 com o IP do servidor');
    console.log('   4. Monitore os logs no Serial Monitor\n');

  } catch (error) {
    console.error('\n❌ Erro durante o setup:', error.message);
    console.error('\n💡 Dicas:');
    console.error('   - Verifique se o PostgreSQL está rodando');
    console.error('   - Confirme as credenciais no .env');
    console.error('   - Verifique se o usuário tem permissões de CREATE DATABASE');
    process.exit(1);
  }
}

// Executa o setup
setupDatabase();