-- ========================================================
-- Banco de Dados: Sistema de Monitoramento de Ônibus
-- Descrição: Estrutura modular para armazenamento de dados de GPS,
-- imagens, intervalos adaptativos e previsões de chegada.
-- ========================================================

-- ==============================
-- Tabela: bus_location
-- Descrição: Registro da localização e horário de cada ônibus
-- ==============================
CREATE TABLE bus_location (
    id SERIAL PRIMARY KEY,                 		-- Identificador único da localização
    bus_line VARCHAR(30) NOT NULL,        		-- Código ou nome da linha do ônibus
    timestamp_location TIMESTAMP NOT NULL,		-- Momento da leitura da localização
    latitude DOUBLE PRECISION NOT NULL,   		-- Latitude do GPS
    longitude DOUBLE PRECISION NOT NULL   		-- Longitude do GPS
);

-- ==============================
-- Tabela: bus_image
-- Descrição: Registro das imagens capturadas associadas à localização
-- ==============================
CREATE TABLE bus_image (
    id SERIAL PRIMARY KEY,                 		-- Identificador único da imagem
    location_id INT NOT NULL,              		-- Referência à tabela bus_location
    image_data BYTEA NOT NULL,             		-- Dados binários da imagem (JPEG)
    timestamp_image TIMESTAMP NOT NULL,    		-- Momento da captura da imagem
    occupancy_count SMALLINT,              		-- Contagem de passageiros (opcional, via YOLO)
    CONSTRAINT fk_bus_image_location       		-- Constraint para chave estrangeira
        FOREIGN KEY(location_id)
        REFERENCES bus_location(id)
        ON DELETE CASCADE                  		-- Se a localização for deletada, imagens relacionadas também
);

-- ==============================
-- Tabela: request_interval
-- Descrição: Registro do intervalo adaptativo entre requisições
-- ==============================
CREATE TABLE request_interval (
    id SERIAL PRIMARY KEY,                 		-- Identificador único do intervalo
    location_id INT NOT NULL,              		-- Referência à localização do ônibus
    start_time TIMESTAMP NOT NULL,       		-- Início do período de intervalo
    end_time TIMESTAMP NOT NULL,           		-- Fim do período de intervalo
    interval_seconds SMALLINT NOT NULL,    		-- Intervalo sugerido em segundos
    CONSTRAINT fk_request_interval_location
        FOREIGN KEY(location_id)
        REFERENCES bus_location(id)
        ON DELETE CASCADE                  		-- Se a localização for deletada, intervalos relacionados também
);

-- ==============================
-- Tabela: prediction_confidence
-- Descrição: Registro da confiabilidade das previsões de chegada dos ônibus
-- ==============================
CREATE TABLE prediction_confidence (
    id SERIAL PRIMARY KEY,                 		-- Identificador único da previsão
    location_id INT NOT NULL,              		-- Referência à localização do ônibus
    predicted_arrival TIMESTAMP NOT NULL,  		-- Horário estimado de chegada
    actual_arrival TIMESTAMP,              		-- Horário real de chegada
    confidence_percent DECIMAL(5,2),       		-- Confiabilidade da previsão (0 a 100%)
    timestamp_prediction TIMESTAMP NOT NULL,	-- Momento em que a previsão foi feita
    CONSTRAINT fk_prediction_confidence_location
        FOREIGN KEY(location_id)
        REFERENCES bus_location(id)
        ON DELETE CASCADE                  		-- Se a localização for deletada, previsões relacionadas também
);
