from lib.mfrc522 import MFRC522
from time import sleep, sleep_ms
import network
import urequests
    
reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)

supabaseURL = "https://oevhgojxrdpovzfdnksw.supabase.co/rest/v1/rfid"

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


print("Bring TAG closer...")
print("")
    
    
while True:
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            print("CARD ID: "+str(card))
            
            headers = {
                "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ldmhnb2p4cmRwb3Z6ZmRua3N3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwOTkwMTIsImV4cCI6MjA2MjY3NTAxMn0.IYoCadmcDVmrp7PAUOQOw60dx2kOsmHzNHT17zs13L8",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ldmhnb2p4cmRwb3Z6ZmRua3N3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzA5OTAxMiwiZXhwIjoyMDYyNjc1MDEyfQ.hrcuj3lPJyLNvO-unjMrXl9BDa4sgmctU-JU5Ab8RUo",
                "Prefer": "return=representation",
                "Content-Type": "application/json"
            }

            url = f"{supabaseURL}?rfid=eq.{str(card)}"
            req = makeRequest(url, "GET", headers)
            if req:
                print(f"Welcome {req[0]["name"]}")
            else:
                print("Denied")

        sleep_ms(500) 