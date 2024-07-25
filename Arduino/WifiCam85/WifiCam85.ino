#include "WifiCam.hpp"
#include <WiFi.h>

// Credenciales WiFi
static const char* WIFI_SSID = "CarBox";
static const char* WIFI_PASS = "Espe2024*";

// Resolución inicial de la cámara
esp32cam::Resolution initialResolution;
// Servidor web en el puerto 80
WebServer server(80);

// Pin del LED
const int LED_PIN = 4;

void setup()
{
  Serial.begin(115200);
  Serial.println();
  delay(2000);

  // Configurar el pin del LED como salida
  pinMode(LED_PIN, OUTPUT);
  // Encender el LED
  digitalWrite(LED_PIN, HIGH);

  // Configurar WiFi
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("WiFi failure");
    delay(5000);
    ESP.restart();
  }
  Serial.println("WiFi connected");

  // Configurar dirección IP estática (opcional)
  // IPAddress local_IP(192, 168, 192, 85); // Dirección IP estática que deseas asignar al ESP32-CAM
  // IPAddress gateway(192, 168, 255, 1);    // Dirección de la puerta de enlace
  // IPAddress subnet(255, 255, 255, 0);   // Máscara de subred
  // WiFi.config(local_IP, gateway, subnet);

  // Inicializar la cámara
  {
    using namespace esp32cam;

    initialResolution = Resolution::find(1024, 768);

    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(initialResolution);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    if (!ok) {
      Serial.println("camera initialize failure");
      delay(5000);
      ESP.restart();
    }
    Serial.println("camera initialize success");
  }

  // Iniciar servidor web
  Serial.println("camera starting");
  Serial.print("http://");
  Serial.println(WiFi.localIP());

  addRequestHandlers(); // Añadir manejadores de solicitudes HTTP
  server.begin();
}

void loop()
{
  server.handleClient(); // Manejar las solicitudes HTTP entrantes
}
