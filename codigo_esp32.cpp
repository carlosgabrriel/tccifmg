#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <MPU6050_light.h>

MPU6050 mpu(Wire);

// wifi e MQTT  
const char* ssid = "...";          //Nome da rede Wi-Fi
const char* password = "...";          //Senha da rede Wi-Fi
const char* mqtt_server = "broker.hivemq.com"; // Broker MQTT utilizado 

WiFiClient espClient;
PubSubClient client(espClient);

char payload[64];
char tempor[64];

unsigned long lastSend = 0;
const unsigned long sendInterval = 1;  // intervalo de envio em ms

// função que so roda uma vez 
void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);   // LED WiFi
  pinMode(15, OUTPUT);  // LED MQTT

  // conexão com wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao WiFi");
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print(".");
    if (millis() - t0 > 10000) break; // timeout
  }
  Serial.println();
  Serial.print("WiFi status: "); Serial.println(WiFi.status());

  //Inicialização do MPU6050
  Wire.begin();
  byte status = mpu.begin();
  Serial.print("MPU6050 status: ");
  Serial.println(status);
  while (status != 0) {
    Serial.println("Erro ao iniciar MPU6050, tentando novamente...");
    delay(1000);
    status = mpu.begin();
  }
  Serial.println("MPU6050 iniciado com sucesso!");
  mpu.calcOffsets();  // Calibra com o sensor parado

  //Configuração do MQTT
  client.setServer(mqtt_server, 1883);
}

//função loop
void loop() {
  // Mantém MQTT conectado
  if (!client.connected()) reconnectMQTT();
  client.loop();

  // Atualiza LEDs
  digitalWrite(2, WiFi.status() == WL_CONNECTED ? HIGH : LOW);
  digitalWrite(15, client.connected() ? HIGH : LOW);

  // Atualiza o sensor
  mpu.update();

  unsigned long now = millis();
  if (now - lastSend >= sendInterval) {
    lastSend = now;

    // Converte valores em string 
    dtostrf(mpu.getAccX(), 6, 3, tempor);
    strcpy(payload, tempor);
    strcat(payload, ":");
    dtostrf(mpu.getAccY(), 6, 3, tempor);
    strcat(payload, tempor);
    strcat(payload, ":");
    dtostrf(mpu.getAccZ(), 6, 3, tempor);
    strcat(payload, tempor);

    // Publica no tópico MQTT
    client.publish("sensedata", payload);

    //visualização no serial 
    Serial.print("x,y,z = ");
    Serial.println(payload);
  }
}

//função de reconexão 
void reconnectMQTT() {
  if (client.connected()) return;
  Serial.print("Conectando ao MQTT...");
  String clientId = "ESP32Client-";
  clientId += String(random(0xffff), HEX);
  if (client.connect(clientId.c_str())) {
    Serial.println("Conectado!");
  } else {
    Serial.print("Falha, rc=");
    Serial.println(client.state());
    delay(2000);
  }
}
