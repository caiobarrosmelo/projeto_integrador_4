-- ========================================================
-- Scripts SQL Úteis - Sistema de Monitoramento de Ônibus
-- ========================================================

-- ==============================
-- CONSULTAS DE MONITORAMENTO
-- ==============================

-- 1. Últimas 10 localizações com imagens associadas
SELECT 
    bl.id,
    bl.bus_line,
    bl.timestamp_location,
    bl.latitude,
    bl.longitude,
    CASE 
        WHEN bi.id IS NOT NULL THEN '✓'
        ELSE '✗'
    END as tem_imagem,
    LENGTH(bi.image_data) as tamanho_imagem_bytes
FROM bus_location bl
LEFT JOIN bus_image bi ON bi.location_id = bl.id
ORDER BY bl.timestamp_location DESC
LIMIT 10;

-- 2. Estatísticas por linha de ônibus
SELECT 
    bus_line,
    COUNT(*) as total_registros,
    COUNT(DISTINCT DATE(timestamp_location)) as dias_ativos,
    MIN(timestamp_location) as primeiro_registro,
    MAX(timestamp_location) as ultimo_registro
FROM bus_location
GROUP BY bus_line
ORDER BY total_registros DESC;

-- 3. Taxa de captura de imagens (%)
SELECT 
    bl.bus_line,
    COUNT(bl.id) as total_localizacoes,
    COUNT(bi.id) as total_imagens,
    ROUND(100.0 * COUNT(bi.id) / COUNT(bl.id), 2) as taxa_captura_percent
FROM bus_location bl
LEFT JOIN bus_image bi ON bi.location_id = bl.id
GROUP BY bl.bus_line;

-- 4. Verificar velocidade entre pontos (detectar anomalias)
WITH velocidades AS (
    SELECT 
        bus_line,
        latitude,
        longitude,
        timestamp_location,
        LAG(latitude) OVER (PARTITION BY bus_line ORDER BY timestamp_location) as lat_anterior,
        LAG(longitude) OVER (PARTITION BY bus_line ORDER BY timestamp_location) as lon_anterior,
        LAG(timestamp_location) OVER (PARTITION BY bus_line ORDER BY timestamp_location) as tempo_anterior
    FROM bus_location
)
SELECT 
    bus_line,
    timestamp_location,
    ROUND(CAST(
        -- Fórmula de Haversine simplificada (aproximação)
        111320 * SQRT(
            POWER(latitude - lat_anterior, 2) + 
            POWER((longitude - lon_anterior) * COS(RADIANS(latitude)), 2)
        ) / 
        NULLIF(EXTRACT(EPOCH FROM (timestamp_location - tempo_anterior)), 0) * 3.6
    AS NUMERIC), 2) as velocidade_kmh
FROM velocidades
WHERE lat_anterior IS NOT NULL
    AND EXTRACT(EPOCH FROM (timestamp_location - tempo_anterior)) > 0
ORDER BY velocidade_kmh DESC
LIMIT 20;

-- 5. Localizações recentes (últimas 24 horas)
SELECT 
    bus_line,
    COUNT(*) as registros_24h,
    AVG(EXTRACT(EPOCH FROM (timestamp_location - LAG(timestamp_location) 
        OVER (PARTITION BY bus_line ORDER BY timestamp_location)))) as intervalo_medio_seg
FROM bus_location
WHERE timestamp_location > NOW() - INTERVAL '24 hours'
GROUP BY bus_line;

-- 6. Tamanho total de imagens armazenadas
SELECT 
    COUNT(*) as total_imagens,
    pg_size_pretty(SUM(LENGTH(image_data))) as tamanho_total,
    pg_size_pretty(AVG(LENGTH(image_data))::bigint) as tamanho_medio,
    pg_size_pretty(MIN(LENGTH(image_data))) as menor_imagem,
    pg_size_pretty(MAX(LENGTH(image_data))) as maior_imagem
FROM bus_image;

-- ==============================
-- MANUTENÇÃO E LIMPEZA
-- ==============================

-- 7. Deletar registros antigos (mais de 30 dias)
-- ATENÇÃO: Executar com cuidado! Faz backup antes.
DELETE FROM bus_location
WHERE timestamp_location < NOW() - INTERVAL '30 days';
-- Por causa do CASCADE, imagens relacionadas também serão deletadas

-- 8. Deletar imagens corrompidas (tamanho anormal)
DELETE FROM bus_image
WHERE LENGTH(image_data) < 100  -- Menor que 100 bytes (muito pequeno)
   OR LENGTH(image_data) > 10485760;  -- Maior que 10MB (muito grande)

-- 9. Vacuumar tabelas para recuperar espaço
VACUUM ANALYZE bus_location;
VACUUM ANALYZE bus_image;
VACUUM ANALYZE request_interval;
VACUUM ANALYZE prediction_confidence;

-- ==============================
-- ÍNDICES PARA PERFORMANCE
-- ==============================

-- 10. Criar índices para otimizar consultas frequentes

-- Índice por linha e timestamp (para buscar histórico de uma linha)
CREATE INDEX IF NOT EXISTS idx_bus_location_line_time 
ON bus_location(bus_line, timestamp_location DESC);

-- Índice por timestamp (para consultas temporais)
CREATE INDEX IF NOT EXISTS idx_bus_location_time 
ON bus_location(timestamp_location DESC);

-- Índice na foreign key de imagens
CREATE INDEX IF NOT EXISTS idx_bus_image_location 
ON bus_image(location_id);

-- Índice composto para localização geográfica (bounding box queries)
CREATE INDEX IF NOT EXISTS idx_bus_location_coords 
ON bus_location(latitude, longitude);

-- ==============================
-- VIEWS ÚTEIS
-- ==============================

-- 11. View: Localizações com status de imagem
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

-- Usar a view:
-- SELECT * FROM v_locations_with_images WHERE bus_line = 'L101' LIMIT 10;

-- 12. View: Estatísticas em tempo real
CREATE OR REPLACE VIEW v_stats_realtime AS
SELECT 
    (SELECT COUNT(*) FROM bus_location) as total_localizacoes,
    (SELECT COUNT(*) FROM bus_image) as total_imagens,
    (SELECT COUNT(DISTINCT bus_line) FROM bus_location) as linhas_ativas,
    (SELECT pg_size_pretty(pg_database_size(current_database()))) as tamanho_banco,
    (SELECT MAX(timestamp_location) FROM bus_location) as ultima_atualizacao;

-- Usar a view:
-- SELECT * FROM v_stats_realtime;

-- ==============================
-- TRIGGERS PARA AUDITORIA
-- ==============================

-- 13. Tabela de log de alterações
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    record_id INT,
    changed_at TIMESTAMP DEFAULT NOW(),
    changed_by VARCHAR(100)
);

-- 14. Trigger function para registrar deleções
CREATE OR REPLACE FUNCTION log_deletion()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id)
    VALUES (TG_TABLE_NAME, 'DELETE', OLD.id);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger em bus_location
CREATE TRIGGER trigger_log_bus_location_delete
BEFORE DELETE ON bus_location
FOR EACH ROW
EXECUTE FUNCTION log_deletion();

-- ==============================
-- FUNÇÕES PERSONALIZADAS
-- ==============================

-- 15. Função: Calcular distância entre dois pontos (Haversine)
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 DOUBLE PRECISION,
    lon1 DOUBLE PRECISION,
    lat2 DOUBLE PRECISION,
    lon2 DOUBLE PRECISION
) RETURNS DOUBLE PRECISION AS $$
DECLARE
    R CONSTANT DOUBLE PRECISION := 6371000; -- Raio da Terra em metros
    dLat DOUBLE PRECISION;
    dLon DOUBLE PRECISION;
    a DOUBLE PRECISION;
    c DOUBLE PRECISION;
BEGIN
    dLat := RADIANS(lat2 - lat1);
    dLon := RADIANS(lon2 - lon1);
    
    a := SIN(dLat/2) * SIN(dLat/2) +
         COS(RADIANS(lat1)) * COS(RADIANS(lat2)) *
         SIN(dLon/2) * SIN(dLon/2);
    
    c := 2 * ATAN2(SQRT(a), SQRT(1-a));
    
    RETURN R * c; -- Retorna distância em metros
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Exemplo de uso:
-- SELECT calculate_distance(-8.0630, -34.8710, -8.0640, -34.8720) as distancia_metros;

-- 16. Função: Buscar última localização de uma linha
CREATE OR REPLACE FUNCTION get_last_location(p_bus_line VARCHAR)
RETURNS TABLE(
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    timestamp_location TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT bl.latitude, bl.longitude, bl.timestamp_location
    FROM bus_location bl
    WHERE bl.bus_line = p_bus_line
    ORDER BY bl.timestamp_location DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Exemplo de uso:
-- SELECT * FROM get_last_location('L101');

-- ==============================
-- DADOS DE TESTE
-- ==============================

-- 17. Inserir dados fictícios para testes
INSERT INTO bus_location (bus_line, timestamp_location, latitude, longitude)
VALUES 
    ('L101', NOW() - INTERVAL '5 minutes', -8.0630, -34.8710),
    ('L101', NOW() - INTERVAL '4 minutes', -8.0631, -34.8711),
    ('L101', NOW() - INTERVAL '3 minutes', -8.0632, -34.8712),
    ('L202', NOW() - INTERVAL '5 minutes', -8.0700, -34.8800),
    ('L202', NOW() - INTERVAL '4 minutes', -8.0701, -34.8801);

-- 18. Inserir imagem fictícia para um registro
INSERT INTO bus_image (location_id, image_data, timestamp_image)
SELECT 
    id,
    decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64'),
    timestamp_location
FROM bus_location
WHERE bus_line = 'L101'
ORDER BY timestamp_location DESC
LIMIT 1;

-- ==============================
-- BACKUP E RESTORE
-- ==============================

-- 19. Comando para fazer backup (executar no terminal)
-- pg_dump -U seu_usuario -d bus_monitoring -F c -f backup_bus_$(date +%Y%m%d).dump

-- 20. Comando para restaurar backup (executar no terminal)
-- pg_restore -U seu_usuario -d bus_monitoring -c backup_bus_20251010.dump

-- ==============================
-- ANÁLISES AVANÇADAS
-- ==============================

-- 21. Mapa de calor: Regiões mais frequentadas
SELECT 
    ROUND(latitude::numeric, 3) as lat_bucket,
    ROUND(longitude::numeric, 3) as lon_bucket,
    COUNT(*) as frequencia,
    array_agg(DISTINCT bus_line) as linhas
FROM bus_location
GROUP BY lat_bucket, lon_bucket
HAVING COUNT(*) > 5
ORDER BY frequencia DESC
LIMIT 20;

-- 22. Padrão temporal: Horários de pico
SELECT 
    EXTRACT(HOUR FROM timestamp_location) as hora,
    COUNT(*) as registros,
    COUNT(DISTINCT bus_line) as linhas_ativas
FROM bus_location
GROUP BY hora
ORDER BY hora;

-- 23. Detectar ônibus parados (mesma posição por muito tempo)
WITH posicoes_consecutivas AS (
    SELECT 
        bus_line,
        latitude,
        longitude,
        timestamp_location,
        LAG(latitude) OVER (PARTITION BY bus_line ORDER BY timestamp_location) as lat_anterior,
        LAG(longitude) OVER (PARTITION BY bus_line ORDER BY timestamp_location) as lon_anterior,
        LAG(timestamp_location) OVER (PARTITION BY bus_line ORDER BY timestamp_location) as tempo_anterior
    FROM bus_location
)
SELECT 
    bus_line,
    latitude,
    longitude,
    MIN(timestamp_location) as inicio_parada,
    MAX(timestamp_location) as fim_parada,
    EXTRACT(EPOCH FROM (MAX(timestamp_location) - MIN(timestamp_location)))/60 as minutos_parado
FROM posicoes_consecutivas
WHERE ABS(latitude - lat_anterior) < 0.0001  -- Menos de ~11 metros
  AND ABS(longitude - lon_anterior) < 0.0001
GROUP BY bus_line, latitude, longitude
HAVING EXTRACT(EPOCH FROM (MAX(timestamp_location) - MIN(timestamp_location))) > 300  -- Mais de 5 minutos
ORDER BY minutos_parado DESC;

-- 24. Rota percorrida (ordenada por tempo)
SELECT 
    bus_line,
    timestamp_location,
    latitude,
    longitude,
    ROW_NUMBER() OVER (PARTITION BY bus_line ORDER BY timestamp_location) as ponto_sequencia
FROM bus_location
WHERE bus_line = 'L101'
  AND timestamp_location > NOW() - INTERVAL '1 hour'
ORDER BY timestamp_location;

-- 25. Qualidade dos dados: Identificar registros problemáticos
SELECT 
    'Latitude fora do Brasil' as problema,
    COUNT(*) as ocorrencias
FROM bus_location
WHERE latitude < -34 OR latitude > 5
UNION ALL
SELECT 
    'Longitude fora do Brasil' as problema,
    COUNT(*) as ocorrencias
FROM bus_location
WHERE longitude < -74 OR longitude > -34
UNION ALL
SELECT 
    'Timestamp futuro' as problema,
    COUNT(*) as ocorrencias
FROM bus_location
WHERE timestamp_location > NOW()
UNION ALL
SELECT 
    'Localizações sem imagem esperada' as problema,
    COUNT(*) as ocorrencias
FROM bus_location bl
LEFT JOIN bus_image bi ON bi.location_id = bl.id
WHERE bi.id IS NULL;

-- ==============================
-- RELATÓRIOS GERENCIAIS
-- ==============================

-- 26. Relatório diário de operação
SELECT 
    DATE(timestamp_location) as data,
    bus_line,
    COUNT(*) as total_registros,
    COUNT(DISTINCT EXTRACT(HOUR FROM timestamp_location)) as horas_operacao,
    MIN(timestamp_location) as primeira_leitura,
    MAX(timestamp_location) as ultima_leitura
FROM bus_location
WHERE timestamp_location > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp_location), bus_line
ORDER BY data DESC, bus_line;

-- 27. Eficiência de coleta de dados
WITH registros_esperados AS (
    SELECT 
        bus_line,
        DATE(timestamp_location) as data,
        24 * 60 / 0.5 as registros_esperados_30s  -- Esperado a cada 30s
    FROM bus_location
    GROUP BY bus_line, DATE(timestamp_location)
),
registros_reais AS (
    SELECT 
        bus_line,
        DATE(timestamp_location) as data,
        COUNT(*) as registros_recebidos
    FROM bus_location
    GROUP BY bus_line, DATE(timestamp_location)
)
SELECT 
    re.bus_line,
    re.data,
    rr.registros_recebidos,
    re.registros_esperados_30s,
    ROUND(100.0 * rr.registros_recebidos / re.registros_esperados_30s, 2) as taxa_eficiencia_percent
FROM registros_esperados re
JOIN registros_reais rr ON re.bus_line = rr.bus_line AND re.data = rr.data
ORDER BY re.data DESC, taxa_eficiencia_percent ASC;

-- 28. Crescimento do banco de dados ao longo do tempo
SELECT 
    DATE(timestamp_location) as data,
    COUNT(*) as novos_registros_localizacao,
    SUM(COUNT(*)) OVER (ORDER BY DATE(timestamp_location)) as total_acumulado
FROM bus_location
GROUP BY DATE(timestamp_location)
ORDER BY data DESC
LIMIT 30;

-- ==============================
-- EXPORTAÇÃO DE DADOS
-- ==============================

-- 29. Exportar CSV com dados de uma linha específica
-- (Executar no terminal)
-- \copy (SELECT bus_line, timestamp_location, latitude, longitude FROM bus_location WHERE bus_line = 'L101' ORDER BY timestamp_location) TO '/tmp/linha_l101.csv' WITH CSV HEADER;

-- 30. Exportar dados para análise geoespacial (formato GeoJSON-like)
SELECT 
    json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(
            json_build_object(
                'type', 'Feature',
                'properties', json_build_object(
                    'bus_line', bus_line,
                    'timestamp', timestamp_location
                ),
                'geometry', json_build_object(
                    'type', 'Point',
                    'coordinates', json_build_array(longitude, latitude)
                )
            )
        )
    ) as geojson
FROM bus_location
WHERE bus_line = 'L101'
  AND timestamp_location > NOW() - INTERVAL '1 hour';

-- ==============================
-- PERFORMANCE E OTIMIZAÇÃO
-- ==============================

-- 31. Analisar tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as tamanho_total,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as tamanho_dados,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as tamanho_indices
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 32. Verificar uso dos índices
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as vezes_usado,
    idx_tup_read as tuplas_lidas,
    idx_tup_fetch as tuplas_retornadas
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- 33. Identificar índices não utilizados (candidatos para remoção)
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as tamanho_indice
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey';  -- Não mostrar primary keys

-- 34. Estatísticas de cache (buffer hit ratio)
SELECT 
    'bus_location' as tabela,
    heap_blks_read as blocos_lidos_disco,
    heap_blks_hit as blocos_lidos_cache,
    CASE 
        WHEN heap_blks_read + heap_blks_hit = 0 THEN 0
        ELSE ROUND(100.0 * heap_blks_hit / (heap_blks_read + heap_blks_hit), 2)
    END as cache_hit_ratio_percent
FROM pg_statio_user_tables
WHERE relname = 'bus_location'
UNION ALL
SELECT 
    'bus_image' as tabela,
    heap_blks_read,
    heap_blks_hit,
    CASE 
        WHEN heap_blks_read + heap_blks_hit = 0 THEN 0
        ELSE ROUND(100.0 * heap_blks_hit / (heap_blks_read + heap_blks_hit), 2)
    END
FROM pg_statio_user_tables
WHERE relname = 'bus_image';

-- ==============================
-- PARTICIONAMENTO (Para bancos grandes)
-- ==============================

-- 35. Criar tabela particionada por mês (para dados históricos)
-- ATENÇÃO: Só executar em bancos novos ou após migração planejada

-- Criar tabela principal particionada
CREATE TABLE IF NOT EXISTS bus_location_partitioned (
    id SERIAL,
    bus_line VARCHAR(30) NOT NULL,
    timestamp_location TIMESTAMP NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (id, timestamp_location)
) PARTITION BY RANGE (timestamp_location);

-- Criar partições mensais
CREATE TABLE bus_location_2025_10 PARTITION OF bus_location_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE bus_location_2025_11 PARTITION OF bus_location_partitioned
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Índices automáticos nas partições
CREATE INDEX idx_bus_location_part_line ON bus_location_partitioned(bus_line);
CREATE INDEX idx_bus_location_part_time ON bus_location_partitioned(timestamp_location);

-- ==============================
-- SEGURANÇA E PERMISSÕES
-- ==============================

-- 36. Criar usuário read-only para consultas
CREATE USER bus_readonly WITH PASSWORD 'senha_segura_readonly';
GRANT CONNECT ON DATABASE bus_monitoring TO bus_readonly;
GRANT USAGE ON SCHEMA public TO bus_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bus_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO bus_readonly;

-- Garantir que novas tabelas também tenham permissão
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bus_readonly;

-- 37. Criar usuário para aplicação (com escrita limitada)
CREATE USER bus_app WITH PASSWORD 'senha_segura_app';
GRANT CONNECT ON DATABASE bus_monitoring TO bus_app;
GRANT USAGE ON SCHEMA public TO bus_app;
GRANT SELECT, INSERT ON bus_location TO bus_app;
GRANT SELECT, INSERT ON bus_image TO bus_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bus_app;

-- 38. Revogar permissões de DELETE para usuário da aplicação (segurança)
REVOKE DELETE ON bus_location FROM bus_app;
REVOKE DELETE ON bus_image FROM bus_app;

-- ==============================
-- MONITORAMENTO DE QUERIES LENTAS
-- ==============================

-- 39. Habilitar log de queries lentas (executar como superuser)
-- ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Loga queries > 1s
-- SELECT pg_reload_conf();

-- 40. Ver queries mais lentas (requer pg_stat_statements)
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
-- 
-- SELECT 
--     query,
--     calls,
--     total_exec_time / 1000 as total_seg,
--     mean_exec_time / 1000 as media_seg,
--     max_exec_time / 1000 as max_seg
-- FROM pg_stat_statements
-- WHERE query LIKE '%bus_location%'
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;

-- ==============================
-- JOBS AUTOMATIZADOS (cron)
-- ==============================

-- 41. Instalar extensão pg_cron (para jobs agendados)
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 42. Agendar limpeza automática de dados antigos (diariamente às 2h)
-- SELECT cron.schedule(
--     'cleanup-old-data',
--     '0 2 * * *',  -- Todo dia às 2h
--     $ DELETE FROM bus_location WHERE timestamp_location < NOW() - INTERVAL '90 days' $
-- );

-- 43. Agendar vacuum automático (semanalmente aos domingos às 3h)
-- SELECT cron.schedule(
--     'weekly-vacuum',
--     '0 3 * * 0',  -- Domingo às 3h
--     $ VACUUM ANALYZE bus_location; VACUUM ANALYZE bus_image; $
-- );

-- Ver jobs agendados:
-- SELECT * FROM cron.job;

-- Remover job:
-- SELECT cron.unschedule('cleanup-old-data');

-- ==============================
-- DICAS DE USO
-- ==============================

/*
DICAS IMPORTANTES:

1. PERFORMANCE
   - Sempre use WHERE com índices (bus_line, timestamp_location)
   - LIMIT suas queries para evitar trazer todo o dataset
   - Use EXPLAIN ANALYZE antes de queries complexas

2. BACKUP
   - Faça backup diário: pg_dump -F c
   - Teste restore regularmente
   - Mantenha backups em local separado

3. MONITORAMENTO
   - Verifique pg_stat_user_tables regularmente
   - Monitore tamanho do banco (script 31)
   - Acompanhe cache hit ratio (script 34)

4. MANUTENÇÃO
   - VACUUM semanal para reclamar espaço
   - ANALYZE para manter estatísticas atualizadas
   - Reindex se necessário: REINDEX TABLE bus_location;

5. SEGURANÇA
   - Use usuários com permissões mínimas
   - Nunca exponha credenciais no código
   - Habilite SSL para conexões remotas
   - Mantenha PostgreSQL atualizado

6. ESCALABILIDADE
   - Considere particionamento para > 10M registros
   - Use connection pooling (pgBouncer)
   - Monitore queries lentas
   - Considere réplicas read-only para analytics

COMANDOS ÚTEIS DO PSQL:

\dt              -- Listar tabelas
\d bus_location  -- Descrever estrutura da tabela
\di              -- Listar índices
\du              -- Listar usuários
\l               -- Listar bancos de dados
\timing on       -- Habilitar timing de queries
\x               -- Modo expandido (melhor visualização)
\q               -- Sair

EXEMPLO DE WORKFLOW COMPLETO:

1. Conectar ao banco:
   psql -U seu_usuario -d bus_monitoring

2. Verificar dados recentes:
   SELECT * FROM v_stats_realtime;

3. Ver últimas localizações:
   SELECT * FROM v_locations_with_images LIMIT 10;

4. Analisar performance:
   SELECT * FROM pg_stat_user_tables WHERE relname = 'bus_location';

5. Limpar dados antigos (se necessário):
   DELETE FROM bus_location WHERE timestamp_location < NOW() - INTERVAL '30 days';

6. Vacuum:
   VACUUM ANALYZE;
*/

-- ========================================================
-- FIM DO SCRIPT
-- ========================================================