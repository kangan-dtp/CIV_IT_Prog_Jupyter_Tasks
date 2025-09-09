# Example MicroPython code for Pico W
import mip
import time
import network
import ujson

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
from machine import Pin
from umqtt.simple import MQTTClient

# Ports
DHT11 = dht.DHT11(Pin(0))

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

def getTempHumid():
    # DHT11 temp reading
    try:
        DHT11.measure()
        if DHT11.temperature() is not None and DHT11.humidity() is not None:
            return {
                "temp": DHT11.temperature(),
                "hum": DHT11.humidity()
            }
    except OSError as e:
        print(f"DHT11 error: {e}")
        return None

time.sleep(2)  # Wait before the first reading

while True:
    client.check_msg()
    sensor_data = getTempHumid()
    if sensor_data:
        client.publish("pico/temphumid", ujson.dumps(sensor_data))

    time.sleep(10)