
#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <string.h>

Adafruit_MPU6050 mpu;
sensors_event_t a, g, temp;

// WiFi / MQTT
const char* ssid = "...";//nome da rede que vai ser conectado 
const char* password = "...";//senha da rede que vai ser conectado 
const char* mqtt_server = "broker.hivemq.com";
WiFiClient espClient;
PubSubClient client(espClient);

char payload[64];
char tempor[64];

unsigned long lastSend = 0;
const unsigned long sendInterval = 1; // ms

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);   // LED WiFi
  pinMode(15, OUTPUT);  // LED MQTT

  // Inicia WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi");
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print(".");
    if (millis() - t0 > 10000) break; // timeout simples
  }
  Serial.println();
  Serial.print("WiFi status: "); Serial.println(WiFi.status());

  // Inicializa MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to start MPU6050");
    while (1) delay(10);
  }
  // Configs opcionais:
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  client.setServer(mqtt_server, 1883);
}

void loop() {
  // Mantém MQTT vivo
  if (!client.connected()) reconnectMQTT();
  client.loop();

  // Atualiza LEDs de status
  digitalWrite(2, WiFi.status() == WL_CONNECTED ? HIGH : LOW);
  digitalWrite(15, client.connected() ? HIGH : LOW);

  // Lê sensor uma vez por loop
  mpu.getEvent(&a, &g, &temp);

  unsigned long now = millis();
  if (now - lastSend >= sendInterval) {
    lastSend = now;

    // converte para string segura (evita String())
    dtostrf(a.acceleration.x, 6, 3, tempor);
    strcpy(payload,tempor);
    strcat(payload,":");
    dtostrf(a.acceleration.y, 6, 3, tempor);
    strcat(payload,tempor);
    strcat(payload,":");
    dtostrf(a.acceleration.z, 6, 3, tempor);
    strcat(payload,tempor);
    
    client.publish("sensedata", payload);

    
    
    // Debug mínimo (pode desativar se quiser testar sem Serial)
    Serial.print("x,y,z = "); Serial.println(payload);
  }
}

void reconnectMQTT() {
  if (client.connected()) return;
  Serial.print("MQTT connecting...");
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);
  if (client.connect(clientId.c_str())) {
    Serial.println("ok");
  } else {
    Serial.print("failed, rc=");
    Serial.println(client.state());
    delay(2000);
  }
}
