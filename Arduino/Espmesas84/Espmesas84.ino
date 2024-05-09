// Incluye las librerías necesarias según el tipo de dispositivo
// y define algunos valores por defecto si no están definidos
#if defined(ESP8266)
#include <ESP8266WiFi.h>
#define THINGSBOARD_ENABLE_PROGMEM 0
#elif defined(ESP32) || defined(RASPBERRYPI_PICO) || defined(RASPBERRYPI_PICO_W)
#include <WiFi.h>
#endif

// Si no está definido LED_BUILTIN, se define como 99
#ifndef LED_BUILTIN
#define LED_BUILTIN 99
#endif


// Incluye las librerías necesarias para el cliente MQTT y ThingsBoard
#include <Arduino_MQTT_Client.h>
#include <ThingsBoard.h>

// Declaración del pin IR
const int ir = 16;
int datoanteriorir = LOW;

// Define las credenciales de la red WiFi y el token de acceso de ThingsBoard
constexpr char WIFI_SSID[] = "Mqtt1";
constexpr char WIFI_PASSWORD[] = "torresjairo";
constexpr char TOKEN[] = "HAQDuCCiSr1dpXiTmtzX";



// Define la dirección IP y el puerto del servidor ThingsBoard
constexpr char THINGSBOARD_SERVER[] = "192.168.0.86";
constexpr uint16_t THINGSBOARD_PORT = 1883U;

// Tamaño máximo de los paquetes MQTT
constexpr uint32_t MAX_MESSAGE_SIZE = 1024U;
constexpr uint32_t SERIAL_DEBUG_BAUD = 115200U; // Velocidad del puerto serie para debugging


// Inicializa el cliente WiFi y el cliente MQTT
WiFiClient wifiClient;
Arduino_MQTT_Client mqttClient(wifiClient);
ThingsBoard tb(mqttClient, MAX_MESSAGE_SIZE);

// Nombres de atributos y variables relacionadas con el LED
constexpr char BLINKING_INTERVAL_ATTR[] = "blinkingInterval";
constexpr char LED_MODE_ATTR[] = "ledMode";
constexpr char encenderunled[] = "encenderled";
constexpr char LED_STATE_ATTR[] = "ledState";

volatile bool attributesChanged = false; // Cambios en los atributos
volatile int ledMode = 0; // Modo del LED
volatile int encenderled = 0; // Encendido del LED
volatile bool ledState = false; // Estado actual del LED

// Configuración para el intervalo de parpadeo
constexpr uint16_t BLINKING_INTERVAL_MS_MIN = 10U;
constexpr uint16_t BLINKING_INTERVAL_MS_MAX = 60000U;
volatile uint16_t blinkingInterval = 1000U;

uint32_t previousStateChange;
constexpr int16_t telemetrySendInterval = 2000U; // Intervalo de envío de telemetría
uint32_t previousDataSend;

// Listas de atributos compartidos y del cliente para suscribirse y solicitarlos respectivamente
constexpr std::array<const char *, 2U> SHARED_ATTRIBUTES_LIST = {
  LED_STATE_ATTR,
  BLINKING_INTERVAL_ATTR
};
constexpr std::array<const char *, 1U> CLIENT_ATTRIBUTES_LIST = {
  LED_MODE_ATTR
};


// Inicializa la conexión WiFi
/// Inicializa la conexión WiFi,
/// esperará indefinidamente hasta que se establezca una conexión con éxito
void InitWiFi() {
  Serial.println("Conectando al punto de acceso ...");
  // Intenta establecer una conexión con la red WiFi proporcionada
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    // Retraso de 500ms hasta que se establezca una conexión con éxito
    delay(500);
    Serial.print(".");
  }
  Serial.println("Conectado al punto de acceso");

  // Define la dirección IP estática y los detalles de la red
  IPAddress staticIP(192, 168, 0, 84); // Dirección IP deseada
  IPAddress gateway(192, 168, 0, 1);     // Puerta de enlace
  IPAddress subnet(255, 255, 255, 0);    // Máscara de subred
  IPAddress dns(8, 8, 8, 8);             // Servidor DNS
}


/// Reconecta el WiFi utilizando InitWiFi si la conexión ha sido eliminada
/// Retorna true tan pronto como se haya establecido una conexión nuevamente
const bool reconnect() {
  // Comprueba que no estemos conectados aún
  const wl_status_t status = WiFi.status();
  if (status == WL_CONNECTED) {
    return true;
  }

  // Si no estamos conectados, establece una nueva conexión con la red WiFi proporcionada
  InitWiFi();
  return true;
}

/// Procesa la función RPC "setLedMode"
/// RPC_Data es una variante JSON, que puede consultarse utilizando el operador[]
/// Consulta https://arduinojson.org/v5/api/jsonvariant/subscript/ para más detalles
/// Datos que contienen el método RPC llamado y su valor actual
/// Respuesta que debe ser enviada a la nube. Útil para getMethods
RPC_Response processSetLedMode(const RPC_Data &data) {
  Serial.println("Recibido el método RPC para establecer el estado del LED");

  // Procesa los datos
  int new_mode = data;
  int prenderelled = data;

  Serial.print("Modo a cambiar: ");
  Serial.println(new_mode);

  Serial.print("LED a ser encendido");
  Serial.println(new_mode);

  if (new_mode != 0 && new_mode != 1) {
    return RPC_Response("error", "¡Modo desconocido!");
  }

  ledMode = new_mode;

  attributesChanged = true;

  // Retorna el modo actual
  return RPC_Response("newMode", (int)ledMode);
}

// Opcional, mantiene los atributos compartidos suscritos vacíos,
// y la devolución de llamada se llamará para cada atributo compartido cambiado en el dispositivo,
// en lugar de solo aquellos que se ingresaron
const std::array<RPC_Callback, 1U> callbacks = {
  RPC_Callback{ "setLedMode", processSetLedMode }
};


/// Callback de actualización que se llamará tan pronto como uno de los atributos compartidos proporcionados cambie de valor,
/// si no se proporciona ninguno, nos suscribimos a cualquier cambio en el atributo compartido en su lugar
/// Datos que contienen los atributos compartidos que cambiaron y su valor actual
void processSharedAttributes(const Shared_Attribute_Data &data) {
  for (auto it = data.begin(); it != data.end(); ++it) {
    // Si el atributo compartido cambiado es el intervalo de parpadeo
    if (strcmp(it->key().c_str(), BLINKING_INTERVAL_ATTR) == 0) {
      const uint16_t new_interval = it->value().as<uint16_t>();
      // Si el nuevo intervalo está dentro de los límites permitidos
      if (new_interval >= BLINKING_INTERVAL_MS_MIN && new_interval <= BLINKING_INTERVAL_MS_MAX) {
        blinkingInterval = new_interval;
        Serial.print("El intervalo de parpadeo se establece en: ");
        Serial.println(new_interval);
      }
    } 
    // Si el atributo compartido cambiado es el estado del LED
    else if (strcmp(it->key().c_str(), LED_STATE_ATTR) == 0) {
      ledState = it->value().as<bool>();
      // Si se ha definido un pin para el LED, cambia su estado
      if (LED_BUILTIN != 99) {
        digitalWrite(LED_BUILTIN, ledState);
      }
      Serial.print("El estado del LED se establece en: ");
      Serial.println(ledState);
    }
  }
  attributesChanged = true; // Marca que los atributos han cambiado
}

// Procesa los atributos del cliente
void processClientAttributes(const Shared_Attribute_Data &data) {
  for (auto it = data.begin(); it != data.end(); ++it) {
    // Si el atributo del cliente cambiado es el modo LED
    if (strcmp(it->key().c_str(), LED_MODE_ATTR) == 0) {
      const uint16_t new_mode = it->value().as<uint16_t>();
      ledMode = new_mode;
    }
    // Si el atributo del cliente cambiado es para encender un LED específico
    if (strcmp(it->key().c_str(), encenderunled) == 0) {
      const uint16_t prenderled = it->value().as<uint16_t>();
      ledMode = prenderled;
    }
  }
}


// Callback para manejar atributos compartidos
const Shared_Attribute_Callback attributes_callback(&processSharedAttributes, SHARED_ATTRIBUTES_LIST.cbegin(), SHARED_ATTRIBUTES_LIST.cend());

// Callback para manejar solicitudes de atributos compartidos
const Attribute_Request_Callback attribute_shared_request_callback(&processSharedAttributes, SHARED_ATTRIBUTES_LIST.cbegin(), SHARED_ATTRIBUTES_LIST.cend());

// Callback para manejar solicitudes de atributos del cliente
const Attribute_Request_Callback attribute_client_request_callback(&processClientAttributes, CLIENT_ATTRIBUTES_LIST.cbegin(), CLIENT_ATTRIBUTES_LIST.cend());

void setup() {
  // Inicializa la conexión serial para la depuración
  Serial.begin(SERIAL_DEBUG_BAUD);

  // Configura el pin del LED incorporado si está definido
  if (LED_BUILTIN != 99) {
    pinMode(LED_BUILTIN, OUTPUT);
  }

  // Espera 1 segundo
  delay(1000);

  // Inicializa la conexión WiFi
  InitWiFi();
}


void loop() {
  // Espera breve para evitar la saturación de la CPU
  delay(10);

  // Verifica si es necesario reconectarse a la red WiFi
  if (!reconnect()) {
    return;
  }

  // Verifica si el dispositivo está conectado a ThingsBoard
  if (!tb.connected()) {
    // Intenta conectar al servidor de ThingsBoard
    Serial.print("Connecting to: ");
    Serial.print(THINGSBOARD_SERVER);
    Serial.print(" with token ");
    Serial.println(TOKEN);
    if (!tb.connect(THINGSBOARD_SERVER, TOKEN, THINGSBOARD_PORT)) {
      Serial.println("Failed to connect");
      return;
    }

    // Envía la dirección MAC como atributo
    tb.sendAttributeData("macAddress", WiFi.macAddress().c_str());

    Serial.println("Subscribing for RPC...");
    // Suscribe a los métodos RPC
    if (!tb.RPC_Subscribe(callbacks.cbegin(), callbacks.cend())) {
      Serial.println("Failed to subscribe for RPC");
      return;
    }

    // Suscribe a los atributos compartidos
    if (!tb.Shared_Attributes_Subscribe(attributes_callback)) {
      Serial.println("Failed to subscribe for shared attribute updates");
      return;
    }

    Serial.println("Subscribe done");

    // Solicita los estados actuales de los atributos compartidos
    if (!tb.Shared_Attributes_Request(attribute_shared_request_callback)) {
      Serial.println("Failed to request for shared attributes");
      return;
    }

    // Solicita los estados actuales de los atributos del cliente
    if (!tb.Client_Attributes_Request(attribute_client_request_callback)) {
      Serial.println("Failed to request for client attributes");
      return;
    }
  }


  if (attributesChanged) {
      attributesChanged = false;
      if (ledMode == 0) {
          previousStateChange = millis();
      }
      tb.sendTelemetryData(LED_MODE_ATTR, ledMode);
      tb.sendTelemetryData(LED_STATE_ATTR, ledState);
      tb.sendAttributeData(LED_MODE_ATTR, ledMode);
      tb.sendAttributeData(LED_STATE_ATTR, ledState);
  }

  if (ledMode == 1 && millis() - previousStateChange > blinkingInterval) {
      previousStateChange = millis();
      ledState = !ledState;
      tb.sendTelemetryData(LED_STATE_ATTR, ledState);
      tb.sendAttributeData(LED_STATE_ATTR, ledState);
      if (LED_BUILTIN == 99) {
          Serial.print("LED state changed to: ");
          Serial.println(ledState);
      } else {
          digitalWrite(LED_BUILTIN, ledState);
      }
  }

// Lectura del sensor infrarrojo
int presencia = digitalRead(ir);

  // Comprobar si ha cambiado el valor del sensor
  if (presencia != datoanteriorir) {
      // Imprimir el valor del sensor solo si ha cambiado
      Serial.print("Valor del Sensor Infrarrojo: ");
      Serial.println(presencia);
      tb.sendTelemetryData("temperature", presencia);
      tb.sendAttributeData("Caja", presencia);
      // Actualizar el valor anterior del sensor
      datoanteriorir = presencia;
  }

  // Envío de datos de telemetría periódicamente
  if (millis() - previousDataSend > telemetrySendInterval) {
      previousDataSend = millis();
      
      tb.sendAttributeData("rssi", WiFi.RSSI());
      tb.sendAttributeData("channel", WiFi.channel());
      tb.sendAttributeData("bssid", WiFi.BSSIDstr().c_str());
      tb.sendAttributeData("localIp", WiFi.localIP().toString().c_str());
      tb.sendAttributeData("ssid", WiFi.SSID().c_str());
  }

  tb.loop();
}
