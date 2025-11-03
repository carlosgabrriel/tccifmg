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

# Função que normaliza os dados(mexer quando fizer em função do tempo)
ciclo = []
def normalize(x):
    normalizado = (x - (-19.613)) / (19.613 - (-19.613))
    return round(normalizado, 2)
    ciclo.append(ciclo[-1] + 1 if ciclo else 0)
    ciclo.pop(0)

# --- Interface (PyQtGraph) ---
app = pg.mkQApp("vibrac")
window = QtWidgets.QMainWindow()
window.setWindowTitle("Monitoramento em tempo real")
window.resize(800, 600)

central_widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

plot1 = pg.PlotWidget(title="Vibração em função da frequencia")
plot1.setLabel('left', "amplitude", style = {'font-size': '100'})
plot1.setLabel('bottom', "frequencia", style = {'font-size': '100'})
plot1.showGrid(x=True, y=True)
plot1.addLegend()
layout.addWidget(plot1)

curve1 = plot1.plot(pen=pg.mkPen(color = 'r', width = 2), name="Vibração X")
curve2 = plot1.plot(pen=pg.mkPen(color = 'b', width = 2), name="Vibração y")
curve3 = plot1.plot(pen=pg.mkPen(color = 'g', width = 2), name="Vibração z")



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


#função da FFT
amplixx, amplixy, amplixz = [], [], []
fs = 2400
N = 512
update_counterx= 0  # variável global para controlar atualização
update_countery= 0
update_counterz= 0
updatebas = 0

def fft(eixo, curva, amplix,nome):
    global update_counterx, update_countery, update_counterz, updatebas

    # adiciona nova amostra
    amplix.append(eixo)

    # mantém buffer fixo
    if len(amplix) > N:
        amplix.pop(0)

    # contador de atualização
    if nome == 'x':
        update_counterx += 1
        updatebas = update_counterx
    elif nome == 'y':
        update_countery += 1
        updatebas = update_countery
    else:
        update_counterz += 1
        updatebas = update_counterz

    if updatebas % 15 == 0 and len(amplix) == N:
        t = 1 / fs
        fft_amplix = np.fft.fft(amplix)
        freq = np.fft.fftfreq(N, t)

        # metade positiva
        N2 = N // 2
        curva.setData(freq[:N2], np.abs(fft_amplix[:N2]))


# função que recebe os dados e mostra no grafico
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global amplix, ciclo
        global amplixx , amplixy , amplixz
        divi = msg.payload.decode().split(":")
        try:
            x = float(divi[0])
            y = float(divi[1])
            z = float(divi[2])
        except:
            return

        fft(x,curve1,amplixx,'x')
        fft(y,curve2,amplixy,'y')
        fft(z,curve3,amplixz,'z')

        # print(f"x, y, z = {x, y, z} from topic '{msg.topic}'")


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
