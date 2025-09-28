Requisitos IOT 

Hardware 

Módulo GSM – SIM800L – R$49,90 

Cartão SIM – R$0,00 

Módulo GPS – NEO-6M com antena – R$49,90 

Placa controladora ESP32S3 – R$30,00 

Fonte de Alimentação (para a placa) - 5v 2A – R$30,00 

Câmera OV2640 (Compatível com a ESP32S3) - R$20,00 

Totem-Display – R$0,00 

*Necessário confirmar se a câmera do ônibus é IP Digital ou outro tipo, caso sim, irá requerer uma placa mais robusta para o processamento das imagens e conversão em JPEG 

Fluxo do protótipo 

ESP32-S3 + OV2640 → captura imagens periódicas (1–3 min). 

ESP32-S3 + GPS → coleta coordenadas (latitude e longitude). 

ESP32-S3 + Módulo GSM → envia JPEG + coordenadas para o servidor via GPRS (HTTP POST). 

Servidor na nuvem → processa imagem com YOLO → retorna número de passageiros e previsão de chegada (via API Maps ou OSRM). 

Exibição → totem ou dashboard web. 

 

 

Utilização do padrão de envio GPRS (dados móveis 2G/3G/4G): 

Permite envio via HTTP/MQTT para o servidor; 

Escalável, já que dá pra mandar pacotes com coordenadas, timestamp, ID do veículo, lotação etc; 

Integra bem com APIs (Google Maps Google Maps Platform ou OSRM - Open Source Routing Machine Open Street Map Documentation, OSRM API Documentation). 

 

Requisitos Banco de Dados 

-- 1. Registro da localização e horário do ônibus  

CREATE TABLE bus_location (  

id SERIAL PRIMARY KEY,  

bus_line VARCHAR(30) NOT NULL,  

timestamp_location TIMESTAMP NOT NULL,  

latitude DOUBLE PRECISION NOT NULL, longitude  

DOUBLE PRECISION NOT NULL );  

 

-- 2. Registro das imagens capturadas pela câmera associadas à localização e horário CREATE TABLE bus_image ( 

id SERIAL PRIMARY KEY, 

location_id INT NOT NULL,  

image_data BYTEA NOT NULL,  

timestamp_image TIMESTAMP NOT NULL,  

occupancy_count SMALLINT,  

CONSTRAINT fk_bus_image_location FOREIGN KEY (location_id) REFERENCES bus_location(id) ON DELETE CASCADE );  

 

-- 3. Registro do intervalo adaptativo entre requisições  

CREATE TABLE request_interval ( 

id SERIAL PRIMARY KEY,  

location_id INT NOT NULL,  

start_time TIMESTAMP NOT NULL,  

end_time TIMESTAMP NOT NULL,  

interval_seconds SMALLINT NOT NULL,  

CONSTRAINT fk_request_interval_location FOREIGN KEY (location_id) REFERENCES bus_location(id) ON DELETE CASCADE );  

 

 

 

-- 4. Registro da confiabilidade das previsões de chegada dos ônibus  

CREATE TABLE prediction_confidence (  

id SERIAL PRIMARY KEY,  

location_id INT NOT NULL,  

predicted_arrival TIMESTAMP NOT NULL,  

actual_arrival TIMESTAMP,  

confidence_percent DECIMAL(5,2),  

timestamp_prediction TIMESTAMP NOT NULL,  

CONSTRAINT fk_prediction_confidence_location FOREIGN KEY (location_id) REFERENCES bus_location(id) ON DELETE CASCADE); 

 

* Modelo de ML poderia aprender padrões de atraso por linha, horário e tráfego, ajustando ETA e confiabilidade dinamicamente. 

 

Requisitos Segurança da Informação 

Requisitos Cloud Computing 

Requisitos Comportamento do Consumidor 

Requisitos Qualidade de Software 

 

 

 

 

 

 

 

 

 

 

 

 