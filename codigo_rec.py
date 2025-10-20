# recebimento dos dados do mpu6050

# importação das libs
import random
from paho.mqtt import client as mqtt_client

# config do broker e topicos
broker = 'test.mosquitto.org'
port = 1883
sensedata = "sensedata"


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


# função que normaliza os dados 
def normalize(x,):
    normalizado = (x-(-19.613))/(19.613-(-19.613))
    return round(normalizado,2)


# função que recebe os dados 
def subscribe(client: mqtt_client):
    
    #envia valores de z
    def on_message(client, userdata, msg):
        
        divi = msg.payload.decode().split(":")
        x = normalize(float(divi[0]))
        y = normalize(float(divi[1]))
        z = normalize(float(divi[2]))
        
        print(f"valor de x, y e z respectivamente ={x,y,z}, from '{msg.topic}' topic")
        
    client.subscribe(sensedata)

    client.on_message = on_message

# função que mantem o client conectado e o sistema em loop
def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
