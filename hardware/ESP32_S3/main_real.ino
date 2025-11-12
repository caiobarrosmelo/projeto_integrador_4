/*  

  ESP32-WROVER-DEV + OV2640 + GPS (NEO-6M) + ThingSpeak 

  -------------------------------------------------------  

  Funcionalidades:  

    - Captura imagem (OV2640 integrada)  

    - Lê coordenadas GPS (NEO-6M)  

    - Envia dados via WiFi para ThingSpeak 

*/  

 

#include <Arduino.h> 

#include <WiFi.h> 

#include <HTTPClient.h> 

#include "esp_camera.h" 

#include <TinyGPS++.h> 

#include <esp_task_wdt.h> 

 

// ---------------- CONFIGURAÇÃO DE PINS (ESP32-WROVER com OV2640) ----------------  

#define CAM_PIN_PWDN    -1 

#define CAM_PIN_RESET   -1 

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

 

// UART GPS 

#define GPS_RX_PIN 13 

#define GPS_TX_PIN 15 

 

// Configurações WiFi e ThingSpeak 

const char* WIFI_SSID = "SENAC-Mesh";                             // Rede

const char* WIFI_PASSWORD = "";                                   // Senha da rede

const char* THINGSPEAK_API_KEY = "";                              // Substituir pela API do projeto

const char* THINGSPEAK_SERVER = "https://api.thingspeak.com";     // Substituir pela API do projeto

 

#define INTERVAL_MS 30000  // 30 segundos (mínimo ThingSpeak é 15s) 

#define WDT_TIMEOUT 30      // Aumentado para 30s devido ao envio de imagens 

 

// ---------------- OBJETOS GLOBAIS ----------------  

HardwareSerial SerialGPS(2); 

TinyGPSPlus gps; 

const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"; 

 

// ---------------- FUNÇÕES AUXILIARES ----------------  

 

// Codifica buffer em Base64 por blocos 

String encodeBase64Chunked(uint8_t *buf, size_t len) { 

  String out = ""; 

  out.reserve(((len + 2) / 3) * 4); // Pre-aloca memória 

  size_t i = 0; 

  uint8_t block[3]; 

   

  while (i < len) { 

    size_t chunkLen = min((size_t)3, len - i); 

    memcpy(block, buf + i, chunkLen); 

    i += chunkLen; 

 

    uint32_t val = 0; 

    for (int j = 0; j < 3; j++) { 

      val = (val << 8) | (j < chunkLen ? block[j] : 0); 

    } 

     

    for (int j = 0; j < 4; j++) { 

      if (j <= chunkLen) { 

        out += b64_table[(val >> (18 - 6 * j)) & 0x3F]; 

      } else { 

        out += '='; 

      } 

    } 

 

    // Reset WDT periodicamente 

    if (i % 3000 == 0) { 

      yield(); 

      esp_task_wdt_reset(); 

    } 

  } 

  return out; 

} 

 

// URL encode para strings 

String urlEncode(String str) { 

  String encoded = ""; 

  char c; 

  for (size_t i = 0; i < str.length(); i++) { 

    c = str.charAt(i); 

    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') { 

      encoded += c; 

    } else { 

      encoded += '%'; 

      char hex[3]; 

      sprintf(hex, "%02X", c); 

      encoded += hex; 

    } 

  } 

  return encoded; 

} 

 

// Conecta ao WiFi 

bool connectWiFi() { 

  Serial.print("Conectando ao WiFi"); 

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD); 

   

  int attempts = 0; 

  while (WiFi.status() != WL_CONNECTED && attempts < 30) { 

    delay(500); 

    Serial.print("."); 

    attempts++; 

    esp_task_wdt_reset(); 

  } 

   

  if (WiFi.status() == WL_CONNECTED) { 

    Serial.println("\nWiFi conectado!"); 

    Serial.print("IP: "); 

    Serial.println(WiFi.localIP()); 

    return true; 

  } else { 

    Serial.println("\nFalha ao conectar WiFi"); 

    return false; 

  } 

} 

 

// Envia dados para ThingSpeak via HTTP GET 

bool sendToThingSpeak(String busLine, double lat, double lon, String timestamp, String imageB64) { 

  if (WiFi.status() != WL_CONNECTED) { 

    Serial.println("WiFi desconectado, tentando reconectar..."); 

    if (!connectWiFi()) { 

      return false; 

    } 

  } 

 

  HTTPClient http; 

   

  // Monta URL com campos do ThingSpeak 

  String url = String(THINGSPEAK_SERVER) + "/update?api_key=" + THINGSPEAK_API_KEY; 

  url += "&field1=" + urlEncode(busLine); 

  url += "&field2=" + String(lat, 6); 

  url += "&field3=" + String(lon, 6); 

  url += "&field4=" + urlEncode(timestamp); 

   

  // Field5: Imagem Base64 (limitada pelo ThingSpeak) 

  // IMPORTANTE: ThingSpeak tem limite de ~8KB por requisição 

  // Vamos truncar a imagem se necessário 

  if (imageB64.length() > 0) { 

    String truncatedImage = imageB64.substring(0, min(imageB64.length(), (size_t)6000)); 

    url += "&field5=" + urlEncode(truncatedImage); 

  } 

   

  Serial.println("Enviando para ThingSpeak..."); 

  Serial.printf("URL length: %d bytes\n", url.length()); 

   

  http.begin(url); 

  http.setTimeout(20000); // 20 segundos timeout 

   

  int httpResponseCode = http.GET(); 

   

  if (httpResponseCode > 0) { 

    Serial.printf("HTTP Response code: %d\n", httpResponseCode); 

    String response = http.getString(); 

    Serial.println("Resposta: " + response); 

     

    // ThingSpeak retorna o entry ID se sucesso (número > 0) 

    if (response.toInt() > 0) { 

      Serial.println("✓ Dados enviados com sucesso!"); 

      http.end(); 

      return true; 

    } else { 

      Serial.println("✗ ThingSpeak retornou erro (0)"); 

      http.end(); 

      return false; 

    } 

  } else { 

    Serial.printf("✗ Erro no GET: %s\n", http.errorToString(httpResponseCode).c_str()); 

    http.end(); 

    return false; 

  } 

} 

 

// Inicializa câmera OV2640 

bool initCamera() { 

  camera_config_t config; 

  config.ledc_channel = LEDC_CHANNEL_0; 

  config.ledc_timer = LEDC_TIMER_0; 

  config.pin_d0 = CAM_PIN_D0; 

  config.pin_d1 = CAM_PIN_D1; 

  config.pin_d2 = CAM_PIN_D2; 

  config.pin_d3 = CAM_PIN_D3; 

  config.pin_d4 = CAM_PIN_D4; 

  config.pin_d5 = CAM_PIN_D5; 

  config.pin_d6 = CAM_PIN_D6; 

  config.pin_d7 = CAM_PIN_D7; 

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

   

  // Configuração reduzida para caber no ThingSpeak 

  // ThingSpeak tem limite de ~8KB por request 

  if(psramFound()){ 

    config.frame_size = FRAMESIZE_QVGA;  // 320x240 (menor para caber no limit) 

    config.jpeg_quality = 15;             // Qualidade média 

    config.fb_count = 2; 

  } else { 

    config.frame_size = FRAMESIZE_QQVGA;  // 160x120 

    config.jpeg_quality = 20; 

    config.fb_count = 1; 

  } 

 

  esp_err_t err = esp_camera_init(&config); 

  if (err != ESP_OK) { 

    Serial.printf("Camera init failed with error 0x%x\n", err); 

    return false; 

  } 

   

  // Ajusta sensor para melhor qualidade 

  sensor_t * s = esp_camera_sensor_get(); 

  if (s != NULL) { 

    s->set_brightness(s, 0);     // -2 a 2 

    s->set_contrast(s, 0);       // -2 a 2 

    s->set_saturation(s, 0);     // -2 a 2 

  } 

   

  return true; 

} 

 

// Captura imagem em Base64 

String captureImageBase64() { 

  camera_fb_t *fb = esp_camera_fb_get(); 

  if (!fb) { 

    Serial.println("Falha ao capturar imagem"); 

    return ""; 

  } 

   

  Serial.printf("Imagem capturada: %u bytes JPEG\n", fb->len); 

   

  // Verifica se a imagem é muito grande 

  if (fb->len > 4500) { // ~6KB Base64 

    Serial.printf("⚠ Aviso: Imagem grande (%u bytes), será truncada pelo ThingSpeak\n", fb->len); 

  } 

   

  String encoded = encodeBase64Chunked(fb->buf, fb->len); 

  esp_camera_fb_return(fb); 

   

  Serial.printf("Imagem codificada: %u bytes Base64\n", encoded.length()); 

  return encoded; 

} 

 

// Lê coordenadas GPS 

bool readGPS(double &lat, double &lon, unsigned long timeout = 10000) { 

  unsigned long start = millis(); 

  while (millis() - start < timeout) { 

    while (SerialGPS.available()) { 

      gps.encode(SerialGPS.read()); 

    } 

    if (gps.location.isUpdated()) { 

      lat = gps.location.lat(); 

      lon = gps.location.lng(); 

      return true; 

    } 

    esp_task_wdt_reset(); 

  } 

  return false; 

} 

 

// Obtém timestamp atual 

String getTimestamp() { 

  return String(millis()); 

} 

 

// ---------------- SETUP ----------------  

void setup() { 

  Serial.begin(115200); 

  delay(2000); 

   

  Serial.println("\n=== ESP32-WROVER + OV2640 + GPS + ThingSpeak ==="); 

   

  // Inicializa GPS 

  SerialGPS.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN); 

  Serial.println("GPS inicializado em GPIO13 (RX) e GPIO15 (TX)"); 

 

  // Configura Watchdog Timer 

  esp_task_wdt_config_t wdt_config = { 

    .timeout_ms = WDT_TIMEOUT * 1000, 

    .idle_core_mask = (1 << portNUM_PROCESSORS) - 1, 

    .trigger_panic = true 

  }; 

  esp_task_wdt_init(&wdt_config); 

  esp_task_wdt_add(NULL); 

   

  // Verifica PSRAM 

  if(psramFound()){ 

    Serial.println("✓ PSRAM encontrada!"); 

  } else { 

    Serial.println("⚠ PSRAM não encontrada - usando config reduzida"); 

  } 

 

  // Inicializa câmera 

  Serial.println("Inicializando câmera..."); 

  if (!initCamera()) { 

    Serial.println("✗ ERRO: Câmera não inicializada"); 

  } else { 

    Serial.println("✓ Câmera OK (resolução reduzida para ThingSpeak)"); 

  } 

 

  // Conecta ao WiFi 

  Serial.println("Inicializando WiFi..."); 

  if (!connectWiFi()) { 

    Serial.println("✗ ERRO: WiFi não conectado"); 

  } else { 

    Serial.println("✓ WiFi OK"); 

  } 

   

  Serial.println("\n✓ Sistema pronto!"); 

  Serial.printf("Intervalo de envio: %d segundos\n", INTERVAL_MS/1000); 

} 

 

// ---------------- LOOP ----------------  

void loop() { 

  static unsigned long lastTs = 0; 

  unsigned long now = millis(); 

  esp_task_wdt_reset(); 

 

  if (now - lastTs < INTERVAL_MS) { 

    delay(200); 

    return; 

  } 

  lastTs = now; 

 

  Serial.println("\n========================================"); 

  Serial.println("========== Novo Ciclo de Envio =========="); 

  Serial.println("========================================"); 

 

  // 1. Captura imagem 

  Serial.println("\n[1/4] Capturando imagem..."); 

  String imgB64 = captureImageBase64(); 

  if (imgB64 == "") { 

    Serial.println("✗ Imagem inválida, continuando sem imagem..."); 

    imgB64 = ""; // Envia vazio 

  } 

 

  // 2. Lê GPS 

  Serial.println("\n[2/4] Lendo GPS..."); 

  double lat = 0, lon = 0; 

  if (!readGPS(lat, lon, 15000)) { 

    Serial.println("⚠ GPS não obteve fixo (usando 0,0)"); 

  } else { 

    Serial.printf("✓ GPS: %.6f, %.6f\n", lat, lon); 

  } 

 

  // 3. Obtém timestamp 

  Serial.println("\n[3/4] Gerando timestamp..."); 

  String timestamp = getTimestamp(); 

  Serial.println("✓ Timestamp: " + timestamp); 

 

  // 4. Envia para ThingSpeak 

  Serial.println("\n[4/4] Enviando para ThingSpeak..."); 

  Serial.println("Campos:"); 

  Serial.println("  Field1 (bus_line): L1"); 

  Serial.printf("  Field2 (latitude): %.6f\n", lat); 

  Serial.printf("  Field3 (longitude): %.6f\n", lon); 

  Serial.println("  Field4 (timestamp): " + timestamp); 

  Serial.printf("  Field5 (image): %u bytes (truncado se necessário)\n", imgB64.length()); 

   

  if (sendToThingSpeak("L1", lat, lon, timestamp, imgB64)) { 

    Serial.println("\n✓✓✓ Dados enviados com sucesso! ✓✓✓"); 

  } else { 

    Serial.println("\n✗✗✗ Falha no envio ✗✗✗"); 

  } 

   

  Serial.println("========================================\n"); 

   

  // Aguarda para respeitar rate limit do ThingSpeak (15s mínimo) 

  delay(1000); 

} 