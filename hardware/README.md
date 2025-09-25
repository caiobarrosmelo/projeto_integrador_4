ESP32 IoT Bus Monitoring - Projeto Simulado e Real
==================================================

Resumo do Projeto
----------------
Este repositório contém dois códigos para ESP32:
1. Modelo Simulado (Mock) - envia dados fictícios de GPS e imagens para backend PostgreSQL.
2. Modelo Real - integra ESP32-S3 com:
   - Câmera OV2640
   - Módulo GPS NEO-6M com antena
   - Módulo GSM SIM800L (GPRS 2G/3G/4G)
   Envia dados JSON para backend PostgreSQL via HTTP.

Arquitetura
-----------
- ESP32 coleta dados de GPS e imagem.
- Módulo GSM transmite via GPRS para backend.
- Backend (Node.js + PostgreSQL) armazena dados em tabelas:
    - bus_location (coordenadas e timestamp)
    - bus_image (imagem Base64 convertida para BYTEA)
    - request_interval (intervalo de requisições adaptativo)
    - prediction_confidence (confiabilidade de previsão de chegada)

Estrutura do Código
------------------
- Simulado:
  - Função getFakeGPS() gera coordenadas simuladas.
  - Função encodeImageBase64() converte imagem mock em Base64 inline.
  - Envio via HTTP POST para backend.

- Real:
  - Integração com câmera OV2640, GPS NEO-6M e GSM SIM800L.
  - Leitura de GPS com TinyGPS++.
  - Captura de imagens JPEG via OV2640.
  - Envio de JSON via comandos AT do SIM800L.

Dependências
------------
- Bibliotecas Arduino:
  - esp_camera.h
  - TinyGPS++.h
  - HardwareSerial.h
- Alimentação do SIM800L: fonte externa 4–4.2 V
- Antena externa recomendada para GPS

Pinos Configurados (ESP32-S3)
-----------------------------
- Câmera OV2640: D0–D7, XCLK, PCLK, VSYNC, HREF, SDA, SCL
- GSM SIM800L: RX=16, TX=17
- GPS NEO-6M: RX=32, TX=33

Intervalos de Envio
------------------
- Modelo Simulado: 30 segundos
- Modelo Real: 2 minutos (configurável via INTERVAL_MS)

Instruções de Uso
-----------------
1. Carregar o código no ESP32-S3 via Arduino IDE ou PlatformIO.
2. Ajustar APN, servidor backend e pinos conforme hardware.
3. Conectar alimentação externa para SIM800L.
4. Abrir monitor serial para verificar logs e envio de dados.
5. Backend recebe JSON e insere em PostgreSQL.

Notas
-----
- Função Base64 inline evita dependência externa durante simulação.
- Estrutura modular permite integração futura de módulos adicionais (sensor de ocupação, Wi-Fi alternativo, etc.).
- Código documentado inline para facilitar manutenção e evolução do projeto.
