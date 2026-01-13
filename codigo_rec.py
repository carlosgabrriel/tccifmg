import random
import threading
from paho.mqtt import client as mqtt_client
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets

#  Config MQTT 
broker = 'broker.hivemq.com'
port = 1883
sensedata = "sensedata"
client_id = f'subscribe-{random.randint(0, 100)}'

#  Parâmetros FFT 
fs = 1000
N = 1024
amplixx, amplixy, amplixz = [], [], []

#  Interface 
app = pg.mkQApp("vibrac")
window = QtWidgets.QMainWindow()
window.setWindowTitle("Monitoramento em tempo real")
window.resize(800, 600)


central_widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

plot1 = pg.PlotWidget(title="Vibração em função da frequência")
plot1.setBackground("w")
plot1.setXRange(0,500)
plot1.setYRange(0,1)
plot1.setLabel('left', "Amplitude")
plot1.setLabel('bottom', "Frequência (Hz)")
plot1.showGrid(x=True, y=True)
plot1.addLegend()
layout.addWidget(plot1)

curve1 = plot1.plot(pen=pg.mkPen('r', width=2), name="Eixo X")
curve2 = plot1.plot(pen=pg.mkPen('b', width=2), name="Eixo Y")
curve3 = plot1.plot(pen=pg.mkPen('g', width=2), name="Eixo Z")

#  MQTT 
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        print("Connected!" if rc == 0 else f"Failed, code={rc}")
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global amplixx, amplixy, amplixz
        try:
            x, y, z = map(float, msg.payload.decode().split(":"))
        except:
            return

        amplixx.append(x)
        amplixy.append(y)
        amplixz.append(z)

        # elimina valores antigos do vetor
        if len(amplixx) > N: amplixx.pop(0)
        if len(amplixy) > N: amplixy.pop(0)
        if len(amplixz) > N: amplixz.pop(0)

    client.subscribe(sensedata)
    client.on_message = on_message

def mqtt_thread():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

#  FFT + Atualização de Gráfico (controlada por Timer) + pequenos filtros
def atualizar_grafico():
    if len(amplixx) == N:
        t = 1/fs
        freq = np.fft.fftfreq(N, t)[:N//2]

        fftx = np.fft.fft(amplixx)
        fftxx = (2 / N) * np.abs(fftx[:N//2])

        ffty = np.fft.fft(amplixy)
        fftyy = (2 / N) * np.abs(ffty[:N//2])
        
        fftz = np.fft.fft(amplixz)
        fftzz = (2 / N) * np.abs(fftz[:N//2])

        #filtro de ruido inicial do proprio sensor
        filtro_ini= freq <= 10
        fftxx[filtro_ini] = 0
        fftyy[filtro_ini] = 0
        fftzz[filtro_ini] = 0

        #flitro do ruido continuo do sensor 
        fftxx[fftxx < 0.003] = 0
        fftyy[fftyy < 0.003] = 0
        fftzz[fftzz < 0.003] = 0

        curve1.setData(freq, fftxx)
        curve2.setData(freq, fftyy)
        curve3.setData(freq, fftzz)

#  Timer do Qt (20 FPS = 50 ms) 
timer = QtCore.QTimer()
timer.timeout.connect(atualizar_grafico)
timer.start(50)

#  Thread MQTT 
t = threading.Thread(target=mqtt_thread)
t.daemon = True
t.start()

#  Inicia a interface 
window.show()
app.exec()
