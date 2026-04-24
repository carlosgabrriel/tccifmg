<div align="center">

# 🔧 Sistema de Monitoramento de Vibrações Mecânicas em Motores Elétricos

![ESP32](https://img.shields.io/badge/ESP32-WROOM--32-blue?style=for-the-badge&logo=espressif)
![Python](https://img.shields.io/badge/Python-3.x-yellow?style=for-the-badge&logo=python)
![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-green?style=for-the-badge&logo=mqtt)
![FFT](https://img.shields.io/badge/FFT-Fast%20Fourier%20Transform-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen?style=for-the-badge)

*Trabalho de Conclusão de Curso — Técnico em Automação Industrial*  
*Instituto Federal de Minas Gerais (IFMG) — Campus Avançado Itabirito*  
*Janeiro de 2026*

</div>

---

## 👥 Autores

| Nome | Curso |
|------|-------|
| Arthur Augusto da Silva Viana | Técnico em Automação Industrial |
| Carlos Gabriel Pereira | Técnico em Automação Industrial |
| Henrique Madeira Gomes | Técnico em Automação Industrial |
| Victor Rodrigues de Andrade | Técnico em Automação Industrial |

**Orientadores:** Prof. Dr. Diego Augusto Gonzaga · Prof. Ms. Adriana Luziê de Almeida

---

## 📋 Resumo

Este projeto propõe um **sistema de baixo custo** para aquisição, transmissão, processamento e visualização de dados de vibração em motores elétricos, viabilizando a **manutenção preditiva** e aumentando a vida útil dos equipamentos.

O sistema utiliza um microcontrolador **ESP32** para coletar os dados de um sensor acelerômetro **MPU6050** e transmiti-los via protocolo **MQTT** a um software desenvolvido em **Python**. O software aplica a **Transformada Rápida de Fourier (FFT)** para converter o sinal do domínio do tempo para o domínio da frequência, permitindo identificar padrões de vibração associados a falhas como desbalanceamento, desalinhamento e desgaste.

**Palavras-chave:** vibração · motores elétricos · FFT · manutenção preditiva · ESP32 · MQTT

---

## 🎯 Objetivos

### Objetivo Geral
Construir um sistema de baixo custo capaz de fazer a aquisição, transmissão, processamento e exibição dos sinais de vibração emitidos por um motor elétrico, auxiliando na detecção de falhas em estágios iniciais.

### Objetivos Específicos
- Coletar dados de vibração usando o sensor/acelerômetro MPU6050
- Estabelecer comunicação entre o ESP32 e o software via protocolo MQTT
- Aplicar a FFT (Transformada Rápida de Fourier) em Python nos dados coletados
- Filtrar ruídos via software
- Exibir gráficos de amplitude × frequência para os 3 eixos de vibração (X, Y, Z)

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐        I2C        ┌─────────────────┐
│   MPU6050       │ ────────────────► │    ESP32        │
│  (Acelerômetro) │                   │  WROOM-32       │
└─────────────────┘                   └────────┬────────┘
                                               │ Wi-Fi + MQTT
                                               ▼
                                    ┌─────────────────────┐
                                    │   MQTT Broker       │
                                    │  (broker.hivemq.com)│
                                    └──────────┬──────────┘
                                               │ Subscribe
                                               ▼
                                    ┌─────────────────────┐
                                    │   Software Python   │
                                    │  FFT + Gráfico      │
                                    └─────────────────────┘
```

### Fluxo de Funcionamento

1. O ESP32 conecta-se à rede Wi-Fi e ao servidor Broker MQTT
2. O acelerômetro MPU6050 inicia a coleta de dados de vibração (eixos X, Y, Z)
3. O microcontrolador transmite os dados via protocolo MQTT ao Broker
4. O software Python recebe os dados via *subscribe* no tópico configurado
5. A FFT é aplicada, convertendo o sinal do domínio do tempo ao domínio da frequência
6. Os resultados são exibidos em gráfico de amplitude × frequência em tempo real

---

## 🔩 Hardware

| Componente | Modelo | Função |
|---|---|---|
| Microcontrolador | ESP32 WROOM-32 | Processamento e transmissão de dados via Wi-Fi/MQTT |
| Acelerômetro | MPU6050 | Coleta de vibração nos 3 eixos (interface I2C) |
| LEDs de Alto Brilho | — | Sinalização de conexão Wi-Fi e MQTT |
| Placa de Prototipagem | Protoboard | Montagem do circuito sem solda |

### Limitações de Hardware
- O MPU6050 possui limite de leitura de **1 kHz** e alto nível de ruído interno
- A protoboard apresenta tamanho superior ao ideal para acoplamento em motores

---

## 💻 Software

### Firmware do ESP32 (C++ / Arduino)
- Comunicação com o MPU6050 via **interface I2C**
- Conexão com rede Wi-Fi e servidor MQTT (HiveMQ)
- Publicação dos dados de aceleração (X, Y, Z) no tópico `sensedata`
- Sinalização de status de conexão via LEDs

### Aplicação Python
- Recepção dos dados via **MQTT subscribe**
- Aplicação da **FFT** com biblioteca NumPy
- Filtros de ruído:
  - Filtro de frequências abaixo de 10 Hz (ruído de offset do sensor)
  - Filtro de amplitudes abaixo de 0,003 (ruído contínuo)
- Normalização da amplitude para melhor visualização
- Interface gráfica em tempo real com **PyQtGraph** (20 FPS)

---

## 📦 Dependências

### ESP32 (Bibliotecas Arduino)
```
WiFi.h
PubSubClient.h
Wire.h
MPU6050_light.h
```

### Python
```bash
pip install paho-mqtt pyqtgraph numpy PyQt5
```

---

## 🚀 Como Executar

### 1. Configurar o Firmware do ESP32

Abra o arquivo `esp32_firmware.ino` e edite as credenciais de rede:

```cpp
const char* ssid     = "SEU_WIFI";       // Nome da rede Wi-Fi
const char* password = "SUA_SENHA";      // Senha da rede Wi-Fi
const char* mqtt_server = "broker.hivemq.com"; // Broker MQTT
```

Faça o upload para o ESP32 via Arduino IDE.

### 2. Executar o Software Python

```bash
python vibration_monitor.py
```

O software se conectará automaticamente ao broker MQTT e iniciará a exibição do espectro de frequências em tempo real.

### 3. Interpretar os Resultados

| Padrão no Espectro | Diagnóstico |
|---|---|
| Amplitudes baixas e uniformes | Motor em boas condições |
| Picos elevados em 50–250 Hz | Indicativo de **desbalanceamento** |
| Harmônicos múltiplos da frequência de rotação | Possível desalinhamento ou folga |

---

## 📊 Resultados

Os testes foram realizados acoplando o protótipo a um ventilador elétrico. A falha de desbalanceamento foi simulada fixando uma fita em uma das hélices.

### Motor em Boas Condições
O espectro FFT apresentou **amplitudes baixas e uniformes** ao longo de todo o espectro de 0 a 500 Hz, confirmando estabilidade mecânica.

### Motor Desbalanceado
O espectro FFT evidenciou **picos de maior amplitude nas frequências de 50 Hz a 250 Hz**, padrão característico de desbalanceamento mecânico, conforme previsto pela literatura técnica.

> ✅ O sistema foi capaz de identificar com clareza a diferença entre os dois estados de operação do motor.

---

## 🔮 Melhorias Futuras

- [ ] Carcaça em impressão 3D para melhor acoplamento em motores industriais
- [ ] Banco de dados para monitoramento histórico de desgastes
- [ ] Aplicativo mobile para visualização dos diagramas
- [ ] Implementação de **Inteligência Artificial** para diagnóstico automático de diferentes tipos de falhas
- [ ] Suporte a múltiplos motores simultâneos

---

## 📁 Estrutura do Repositório

```
.
├── firmware/
│   └── esp32_firmware.ino       # Código do microcontrolador ESP32
├── software/
│   └── vibration_monitor.py     # Aplicação Python (FFT + Interface gráfica)
├── docs/
│   └── TCC_Monitoramento_Vibracao.pdf   # Trabalho completo
└── README.md
```

---

## 📚 Referências Principais

- RAO, S. *Vibrações Mecânicas*. 4. ed. Pearson Prentice Hall, 2009.
- KARDEC, A.; NASCIF, J. *Manutenção: função estratégica*. 3. ed. Qualitymark, 2009.
- TAYLOR, J. *The Vibration Analysis Handbook*. 1990.
- BENETI, L. C. *Análise de vibração para uso na manutenção preditiva utilizando dispositivo de baixo custo*. UFSJ, 2021.
- DOS SANTOS, J. C. et al. *Análise de vibração em motores elétricos da classe 1 da norma ISO 10816*. 2024.

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos no âmbito do Curso Técnico Integrado em Automação Industrial do IFMG — Campus Avançado Itabirito.

---

<p align="center">
  Desenvolvido com ❤️ por alunos do IFMG Campus Avançado Itabirito · 2026
</p>
