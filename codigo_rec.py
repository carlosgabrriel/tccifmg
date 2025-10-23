# recebimento dos dados do mpu6050

import random
import threading
from paho.mqtt import client as mqtt_client
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets

# Config do broker e tópicos
broker = 'test.mosquitto.org'
port = 1883
sensedata = "sensedata"

# Criando um id aleatório para o client
client_id = f'subscribe-{random.randint(0, 100)}'

# Função que normaliza os dados
def normalize(x):
    normalizado = (x - (-19.613)) / (19.613 - (-19.613))
    return round(normalizado, 2)

# --- Interface (PyQtGraph) ---
app = pg.mkQApp("vibrac")
window = QtWidgets.QMainWindow()
window.setWindowTitle("Monitoramento em tempo real")
window.resize(800, 600)

central_widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

plot1 = pg.PlotWidget(title="Vibração em função do tempo")
plot1.showGrid(x=True, y=True)
layout.addWidget(plot1)

curve1 = plot1.plot(pen='r', name="Vibração X")

ciclo = []
amplix = []

# --- MQTT ---
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global amplix, ciclo

        divi = msg.payload.decode().split(":")
        try:
            x = normalize(float(divi[0]))
            y = normalize(float(divi[1]))
            z = normalize(float(divi[2]))
        except:
            return

        print(f"x, y, z = {x, y, z} from topic '{msg.topic}'")

        ciclo.append(ciclo[-1] + 1 if ciclo else 0)
        amplix.append(x)
        if len(ciclo) > 50:
            ciclo.pop(0)
            amplix.pop(0)

        curve1.setData(ciclo, amplix)

    client.subscribe(sensedata)
    client.on_message = on_message


def mqtt_thread():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


# --- Roda MQTT em thread paralela ---
t = threading.Thread(target=mqtt_thread)
t.daemon = True
t.start()

# --- Executa interface ---
window.show()
app.exec()
