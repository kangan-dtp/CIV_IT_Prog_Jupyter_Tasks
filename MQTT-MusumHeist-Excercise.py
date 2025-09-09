# Example MicroPython code for Pico W
import mip
import time
import network
import ujson
import _thread
from machine import Pin, PWM

# Wi-Fi credentials
WIFI_SSID = "CyFi"
WIFI_PASSWORD = "SecurityA40"

# MQTT broker details
MQTT_BROKER_IP = "10.52.126.2"  # Replace with your laptop's IP
MQTT_CLIENT_ID = "pico-w-client"
MQTT_USER = None       # The username you created
MQTT_PASSWORD = None  # The password you created
MQTT_PORT = 1883

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Connecting to Wi-Fi...")
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
    pass
print("Connected to Wi-Fi")

# Install packages only if they don't exist
try:
    import umqtt.simple
except ImportError:
    mip.install("umqtt.simple")

try:
    import umqtt.robust
except ImportError:
    mip.install("umqtt.robust")

try:
    import dht
except ImportError:
    mip.install("dht")

import dht
from umqtt.simple import MQTTClient

# Ports
PIRSensor = Pin(0, Pin.IN)
Buzzer = PWM(Pin(1))
Buzzer.freq(1000)
Buzzer.duty_u16(0)  # Start with buzzer off
LED = Pin(2, Pin.OUT)

# Connect to MQTT broker
client = MQTTClient(
    client_id=MQTT_CLIENT_ID,
    server=MQTT_BROKER_IP,
    port=MQTT_PORT
)
client.set_last_will("pico/status", "offline", retain=True)
client.connect()
print("Connected to MQTT Broker")

# You can now publish and subscribe
client.publish("pico/status", "online")

# Set state variables
armed = True
alarm_triggered = False

def alarm():
    # Make buzzer sound and led blink
    client.publish("pico/alarm", "triggered")
    for _ in range(5):
        Buzzer.duty_u16(32768)  # 50% duty cycle
        LED.value(1)
        time.sleep(0.2)
        Buzzer.duty_u16(0)
        LED.value(0)
        time.sleep(0.2)

def listenForCommands():
    global armed, alarm_triggered

    while True:
        client.check_msg()
        time.sleep(1)
        if not armed and alarm_triggered:
            alarm_triggered = False
            client.publish("pico/alarm", "reset")
            print("Alarm reset")
time.sleep(2)  # Wait before the first reading

_thread.start_new_thread(listenForCommands, ())

while True:
    client.check_msg()
    
    if armed and PIRSensor.value() and not alarm_triggered:
        print("Motion detected!")
        alarm_triggered = True
        alarm()

    time.sleep(1)