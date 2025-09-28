# recebimento dos dados do mpu6050

# importação das libs
import random
from paho.mqtt import client as mqtt_client

# config do broker e topicos
broker = 'test.mosquitto.org'
port = 1883
topicx = "sensors/motor1/accel_x"
topicy = "sensors/motor1/accel_y"
topicz = "sensors/motor1/accel_z"

# criando um id aleatorio para o client
client_id = f'subscribe-{random.randint(0, 100)}'


# callback da coneção com o broker 
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# função que recebe os dados 
def subscribe(client: mqtt_client):
    
    #envia valores de z
    def on_message(client, userdata, msg):
        
        mapa = {
            topicx: "X",
            topicy: "Y",
            topicz: "Z"
        }
        
        valuede = mapa.get(msg.topic, " eixo não encontrado")
        
        print(f"valor de {valuede} ={msg.payload.decode()}, from '{msg.topic}' topic")
    
    client.subscribe(topicx)
    client.subscribe(topicy)
    client.subscribe(topicz)
    client.on_message = on_message

# função que mantem o client conectado e o sistema em loop
def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
