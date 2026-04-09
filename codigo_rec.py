import random
import threading
from paho.mqtt import client as mqtt_client
import numpy as np
import asyncio
import websockets
import json
import time

#  Config MQTT 
broker = 'broker.hivemq.com'
port = 1883
sensedata = "sensedata"
client_id = f'subscribe-{random.randint(0, 100)}'

#  Parâmetros FFT 
fs = 1000
N = 1024
amplixx, amplixy, amplixz = [], [], []
fft_result = {"x": [], "y": [],"z": [],"freq": [] }

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
    global fft_result
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

        # salvar os dados 
        fft_result = {
            "freq": freq.tolist(),
            "x": fftxx.tolist(),
            "y": fftyy.tolist(),
            "z": fftzz.tolist()
        }

# theread atualizao grafiCUZINHO
def loop_att():
    while True:
        atualizar_grafico()
        time.sleep(0.05)


async def senddata(websocket):
    while True:
        await websocket.send(json.dumps(fft_result))
        await asyncio.sleep(0.05)

#vida ao servidor 
async def main():
    async with websockets.serve(senddata,"localhost", 8765):
        print("servidor vivo")
        await asyncio.Future()

def websoket_thread():
    asyncio.run(main())

t1 = threading.Thread(target=mqtt_thread)
t1.daemon = True
t1.start()


t1 = threading.Thread(target=loop_att)
t1.daemon = True
t1.start()

t1 = threading.Thread(target=websoket_thread)
t1.daemon = True
t1.start()

while True:
    time.sleep(1)   
