/*
  ESP32 -> GPRS (SIM800L) + GPS (NEO-6M) + Camera OV2640
  ------------------------------------------------------
  Este sketch realiza:
    - Captura de imagem via OV2640
    - Leitura de coordenadas GPS via NEO-6M
    - Envio de dados JSON para backend PostgreSQL via SIM800L (GPRS)

  Observações:
    - Módulo GSM precisa de fonte externa 4V-4.2V
    - GPS precisa de antena externa para fix rápido
    - Câmera OV2640 exige configuração de pinos correta

  Estrutura de dados enviada:
    {
      "bus_line": "L1",            // Linha do ônibus
      "latitude": <decimal>,       // Latitude GPS
      "longitude": <decimal>,      // Longitude GPS
      "timestamp": <millis>,       // Timestamp local do ESP32
      "image_base64": "<string>"   // Imagem capturada codificada em Base64
    }

  Observações técnicas:
    - INTERVAL_MS define intervalo entre envios (atualmente 30s)
    - encodeBase64 converte bytes de imagem para Base64 inline, sem dependência de bibliotecas externas
    - sendViaSIM800 envia JSON via comandos AT para o SIM800L usando GPRS
    - readGPS lê coordenadas do NEO-6M via TinyGPS++
    - captureImageBase64 captura a imagem da câmera OV2640 e retorna Base64
*/

#include <Arduino.h>
#include "esp_camera.h"
#include <HardwareSerial.h>
#include <TinyGPS++.h>

// ---------------- CONFIGURAÇÃO DE PINS ----------------
#define CAM_PIN_PWDN    -1   // Não utilizado
#define CAM_PIN_RESET   -1   // Não utilizado
#define CAM_PIN_XCLK     21
#define CAM_PIN_SIOD     26
#define CAM_PIN_SIOC     27
#define CAM_PIN_D7       35
#define CAM_PIN_D6       34
#define CAM_PIN_D5       39
#define CAM_PIN_D4       36
#define CAM_PIN_D3       19
#define CAM_PIN_D2       18
#define CAM_PIN_D1        5
#define CAM_PIN_D0        4
#define CAM_PIN_VSYNC    25
#define CAM_PIN_HREF     23
#define CAM_PIN_PCLK     22

// SIM800L UART (HardwareSerial1)
#define SIM_RX_PIN 16
#define SIM_TX_PIN 17

// GPS UART (HardwareSerial2)
#define GPS_RX_PIN 32
#define GPS_TX_PIN 33

// APN da operadora
const char APN[] = "SEU_APN_AQUI";

// Endpoint backend PostgreSQL
const char SERVER_URL[] = "http://<IP_DO_SERVIDOR>:3000/data";

// Intervalo de envio (2 minutos sugerido para produção)
#define INTERVAL_MS 120000

// ---------------- VARIÁVEIS ----------------
HardwareSerial SerialSIM(1);   // Comunicação com SIM800L
HardwareSerial SerialGPS(2);   // Comunicação com GPS
TinyGPSPlus gps;               // Parser de GPS

// Tabela Base64 inline (sem dependências)
const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// ---------------- FUNÇÕES AUXILIARES ----------------

// Codifica bytes em Base64
String encodeBase64(uint8_t* buf, size_t len) {
  String out = "";
  int val = 0, valb = -6;
  for (size_t i = 0; i < len; i++) {
    val = (val << 8) | buf[i];
    valb += 8;
    while (valb >= 0) {
      out += b64_table[(val >> valb) & 0x3F];
      valb -= 6;
    }
  }
  if (valb > -6) out += b64_table[((val << 8) >> (valb + 8)) & 0x3F];
  while (out.length() % 4) out += '=';  // padding Base64
  return out;
}

// Envia JSON via SIM800L (GPRS) usando comandos AT
void sendViaSIM800(String jsonPayload) {
  SerialSIM.println("AT"); delay(500);
  SerialSIM.println("AT+CPIN?"); delay(500);
  SerialSIM.println("AT+CSQ"); delay(500);

  // Configuração do bearer GPRS
  SerialSIM.println("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\""); delay(500);
  SerialSIM.printf("AT+SAPBR=3,1,\"APN\",\"%s\"\r\n", APN); delay(500);
  SerialSIM.println("AT+SAPBR=1,1"); delay(2000);
  SerialSIM.println("AT+SAPBR=2,1"); delay(500);

  // Inicializa HTTP
  SerialSIM.println("AT+HTTPINIT"); delay(500);
  SerialSIM.printf("AT+HTTPPARA=\"URL\",\"%s\"\r\n", SERVER_URL); delay(500);
  SerialSIM.println("AT+HTTPPARA=\"CONTENT\",\"application/json\""); delay(500);

  // Envia dados
  SerialSIM.printf("AT+HTTPDATA=%u,10000\r\n", jsonPayload.length()); delay(500);
  SerialSIM.print(jsonPayload); delay(1000);

  // POST
  SerialSIM.println("AT+HTTPACTION=1"); delay(3000);
  SerialSIM.println("AT+HTTPREAD"); delay(1000);
  SerialSIM.println("AT+HTTPTERM"); delay(500);
}

// Inicializa a câmera OV2640
bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = CAM_PIN_D0; config.pin_d1 = CAM_PIN_D1; config.pin_d2 = CAM_PIN_D2;
  config.pin_d3 = CAM_PIN_D3; config.pin_d4 = CAM_PIN_D4; config.pin_d5 = CAM_PIN_D5;
  config.pin_d6 = CAM_PIN_D6; config.pin_d7 = CAM_PIN_D7;
  config.pin_xclk = CAM_PIN_XCLK;
  config.pin_pclk = CAM_PIN_PCLK;
  config.pin_vsync = CAM_PIN_VSYNC;
  config.pin_href = CAM_PIN_HREF;
  config.pin_sscb_sda = CAM_PIN_SIOD;
  config.pin_sscb_scl = CAM_PIN_SIOC;
  config.pin_pwdn = CAM_PIN_PWDN;
  config.pin_reset = CAM_PIN_RESET;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  return esp_camera_init(&config) == ESP_OK;
}

// Captura imagem e retorna Base64
String captureImageBase64() {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) return "";
  String b64 = encodeBase64(fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return b64;
}

// Lê coordenadas GPS (com timeout)
bool readGPS(double &lat, double &lon, unsigned long timeout=5000) {
  unsigned long start = millis();
  while (millis() - start < timeout) {
    while (SerialGPS.available()) gps.encode(SerialGPS.read());
    if (gps.location.isUpdated()) {
      lat = gps.location.lat();
      lon = gps.location.lng();
      return true;
    }
  }
  return false;
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  SerialSIM.begin(9600, SERIAL_8N1, SIM_RX_PIN, SIM_TX_PIN);
  SerialGPS.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  Serial.println("=== ESP32 -> GPRS + GPS + Camera OV2640 ===");
  if (!initCamera()) Serial.println("Falha ao inicializar camera!");
}

// ---------------- LOOP ----------------
void loop() {
  static unsigned long lastTs = 0;
  unsigned long now = millis();
  if (now - lastTs < INTERVAL_MS) { delay(200); return; }
  lastTs = now;

  Serial.println("\n--- Novo ciclo ---");

  // Captura imagem
  String imgB64 = captureImageBase64();
  Serial.printf("Imagem capturada e codificada (%u bytes Base64)\n", imgB64.length());

  // Leitura GPS
  double lat=0, lon=0;
  if (!readGPS(lat, lon)) {
    Serial.println("Falha ao ler GPS"); return;
  }
  Serial.printf("GPS: lat=%.6f lon=%.6f\n", lat, lon);

  // Monta JSON
  String payload = "{";
  payload += "\"bus_line\":\"L1\",";
  payload += "\"latitude\":" + String(lat,6) + ",";
  payload += "\"longitude\":" + String(lon,6) + ",";
  payload += "\"timestamp\":\"" + String(millis()) + "\",";
  payload += "\"image_base64\":\"" + imgB64 + "\"";
  payload += "}";

  // Envio via SIM800L
  sendViaSIM800(payload);
  Serial.println("Dados enviados via GPRS.");
}
