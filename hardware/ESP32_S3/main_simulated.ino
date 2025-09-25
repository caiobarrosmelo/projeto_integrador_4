/*
  ESP32 Mock -> PostgreSQL modular
  --------------------------------
  Este sketch simula a coleta de dados de um ônibus com ESP32:
    - GPS mock
    - Imagem mock
  e envia via HTTP POST para um backend modular que insere os dados
  nas tabelas PostgreSQL:
    - bus_location (localização e horário)
    - bus_image (imagem associada à localização)
  
  O código é estruturado para testes sem hardware real (mock)
  e utiliza Base64 inline para codificação de imagens.
*/

#include <Arduino.h>
#include <WiFi.h>         // Conexão WiFi do ESP32
#include <HTTPClient.h>   // Envio de requisições HTTP
//#include "Base64.h"      // Não utilizado: substituído por função inline

// ---------- CONFIGURAÇÕES GERAIS ----------
#define INTERVAL_MS (30*1000UL)  // Intervalo entre leituras (30s)
#define GPS_FAKE_STEP 0.0001     // Incremento de GPS a cada ciclo (simulação)

const char* WIFI_SSID = "SEU_SSID";           // Nome da rede WiFi
const char* WIFI_PASS = "SUA_SENHA";         // Senha da rede WiFi
const char* SERVER_URL = "http://<IP_DO_SERVIDOR>:3000/data"; // Endpoint do backend

// ---------- FUNÇÕES AUXILIARES ----------

// Simula a leitura do GPS, incrementando latitude e longitude
void getFakeGPS(double &lat, double &lon) {
  static double s_lat = -8.0630; // Recife aprox. inicial
  static double s_lon = -34.8710;
  s_lat += GPS_FAKE_STEP;
  s_lon += GPS_FAKE_STEP;
  lat = s_lat;
  lon = s_lon;
}

// Tabela Base64 inline
const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// Converte um buffer de bytes em Base64
String encodeImageBase64(uint8_t* buf, size_t len) {
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

// ---------- SETUP ----------
void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.println("=== ESP32 MOCK -> PostgreSQL modular ===");

  // Conecta à rede WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

// ---------- LOOP PRINCIPAL ----------
void loop() {
  static unsigned long lastTs = 0;
  unsigned long now = millis();
  
  // Controla intervalo entre leituras
  if(now - lastTs < INTERVAL_MS) {
    delay(200);
    return;
  }
  lastTs = now;

  Serial.println("\n--- Novo ciclo: GPS + Imagem + Envio POST ---");

  // 1) Captura de imagem MOCK
  size_t imgLen = 10;  
  uint8_t imgBuf[imgLen];
  for(size_t i=0; i<imgLen; i++) imgBuf[i] = i; // dados simulados
  String imgBase64 = encodeImageBase64(imgBuf, imgLen); // codifica em Base64
  Serial.printf("Imagem mock criada: %u bytes (codificada Base64)\n", imgLen);

  // 2) GPS mock
  double lat=0.0, lon=0.0;
  getFakeGPS(lat, lon);
  Serial.printf("GPS mock: lat=%.6f lon=%.6f\n", lat, lon);

  // 3) Monta JSON modular para envio
  String payload = "{";
  payload += "\"bus_line\":\"L1\",";                // Linha do ônibus
  payload += "\"latitude\":" + String(lat,6) + ","; // Latitude
  payload += "\"longitude\":" + String(lon,6) + ","; // Longitude
  payload += "\"timestamp\":\"" + String(millis()) + "\","; // Timestamp mock
  payload += "\"image_base64\":\"" + imgBase64 + "\"";       // Imagem Base64
  payload += "}";

  // 4) Envio HTTP POST
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type","application/json");

    int httpResponseCode = http.POST(payload);
    if(httpResponseCode > 0) {
      String resp = http.getString();
      Serial.printf("POST OK, resp: %s\n", resp.c_str());
    } else {
      Serial.printf("Erro POST: %d\n", httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi desconectado");
  }
}