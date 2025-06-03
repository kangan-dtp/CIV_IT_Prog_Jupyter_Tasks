from machine import Pin, I2C, PWM
from lib.ssd1306 import SSD1306_I2C # OLDED driver
from lib.hcsr04 import HCSR04 # Ultrasonic sensor library
from time import sleep, localtime
import _thread
import network
import urequests
import dht

# Setup I2C connection
i2c = I2C(0, scl=Pin(13), sda=Pin(12))  # SCL on GP13, SDA on GP12
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Setup DHT
DHT = dht.DHT11(Pin(6))

# RGB light
light = [
    Pin(2, Pin.OUT),
    Pin(3, Pin.OUT),
    Pin(4, Pin.OUT)
]

buzzer = PWM(Pin(15))
buzzer.freq(1000) # Set pitch
buzzer.duty_u16(0) # Mute

volume = 2000

global status
status = "OFFLINE"

global supabaseURL
supabaseURL = "https://oevhgojxrdpovzfdnksw.supabase.co/rest/v1/weather_reading"

# Connect to WIFI
ssid = "CyFi"
password = "SecurityA40"

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    print("Connecting to Wi-Fi...")
    sleep(1)

print("Connected to Wi-Fi", station.ifconfig())
status = "ONLINE"


# Helper functions
def lightOff():
    for l in light:
        l.off()

def updateStats(sensor, temp, humidity):
    global status
    # Update OLED screen
    oled.fill(0) # Clear the screen
    oled.text("Weather Station", 0, 0)
    oled.text(f"Status: {status}", 0, 10)
    oled.text(f"Sensor ID: {sensor}", 0, 20)
    oled.text(f"Temperature: {temp}", 0, 30)
    oled.text(f"Humidity: {humidity}", 0, 40)
    oled.show()
    
lightOff()

def makeRequest(url, type = "GET", inputHeaders=None, inputData = None):
    try:
        print("Sending request to server")
        if type == "GET":
            if inputHeaders:
                request = urequests.get(url, headers=inputHeaders)
            else:
                request = urequests.get(url)
        elif type == "POST":
            if inputHeaders:
                request = urequests.post(url, headers=inputHeaders, json=inputData)
            else:
                request = urequests.post(url, json=inputData)
        
        data = request.json()
        request.close()

        print("Completed request", request.status_code)

        return data

    except Exception as error:
        print(error)
                                                                 

def sendWeatherData(sensor, temp, humidity, status):
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ldmhnb2p4cmRwb3Z6ZmRua3N3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwOTkwMTIsImV4cCI6MjA2MjY3NTAxMn0.IYoCadmcDVmrp7PAUOQOw60dx2kOsmHzNHT17zs13L8",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ldmhnb2p4cmRwb3Z6ZmRua3N3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzA5OTAxMiwiZXhwIjoyMDYyNjc1MDEyfQ.hrcuj3lPJyLNvO-unjMrXl9BDa4sgmctU-JU5Ab8RUo",
        "Prefer": "return=representation",
        "Content-Type": "application/json"
    }
    data = {
        "sensor":sensor,
        "temperature_c": temp,
        "humidity_percent":humidity,
        "status": status
    }
    req = makeRequest(supabaseURL, "POST", headers, data)

    if req:
        print(req)

    print(f"Sent weather data for sensor {sensor} (Temp: {temp}, Humidity: {humidity})")

#req = makeRequest(url) # Fetch


while True:
    try:
        DHT.measure()
        sendWeatherData(1, DHT.temperature(), DHT.humidity(), "OK")
        status = "OK"
        updateStats(1, DHT.temperature(), DHT.humidity())
    except Exception as e:
        print(e)

    sleep(1800) # 30 mins
      

    
