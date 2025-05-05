from time import sleep
from machine import Pin, I2C, time_pulse_us
from ssd1306 import SSD1306_I2C
import dht
import time
import _thread


DHT = dht.DHT11(Pin(0))
light = [
    Pin(2, Pin.OUT),
    Pin(3, Pin.OUT),
    Pin(4, Pin.OUT)
]
global lightEnabled
lightEnabled = True

ir = Pin(6, Pin.IN, Pin.PULL_UP)

# Setup I2C connection
i2c = I2C(0, scl=Pin(13), sda=Pin(12))  # SCL on GP13, SDA on GP12
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)


def lightOff():
    for l in light:
        l.off()


def updateStats():
    global lightEnabled
    while True:
        # Date and time
        formatted_time = time.localtime()
        year, month, mday, hour, minute, second, weekday, yearday = formatted_time
        time_str = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
        date_str = "{:02d}-{:02d}-{:04d}".format(mday, month, year)


        # Temp and Humidity
        DHT.measure()
        temperature = DHT.temperature()
        humidity = DHT.humidity()
        temp_str = ('Temp: ' + str(temperature) + 'C')
        humid_str = ('Humidity:' + str(humidity) + '%')

        # LED light
        if lightEnabled == True:
            if temperature > 25:
                lightOff()
                light[0].on()
            elif temperature < 15:
                lightOff()
                light[2].on()
            else:
                lightOff()
                light[1].on()
        else:
            lightOff()


        # Update OLED screen
        oled.fill(0)
        oled.text(str(time_str), 0, 0)
        oled.text(str(date_str), 0, 10)
        oled.text(str(temp_str), 0, 30)
        oled.text(str(humid_str), 0, 40)
        oled.show()

# Have this run on a different thread
_thread.start_new_thread(updateStats, ())

while True:
    # ——— Detect start of a button press ———
    # The IR receiver output idles HIGH; pressing any key pulls it LOW.
    
    while ir.value() == 1:
        pass  # wait here until it goes LOW

    # ——— the sync pulses ———
    time_pulse_us(ir, 0)  # wait out the long LOW
    time_pulse_us(ir, 1)  # wait out the long HIGH

    
    for _ in range(16):
        time_pulse_us(ir, 0)  # skip each short LOW
        time_pulse_us(ir, 1)  # skip each short HIGH

    # ——— Read the 8 bits of the command byte ———
    command = 0
    for bit in range(8):
        time_pulse_us(ir, 0)         
        high_time = time_pulse_us(ir, 1)  
        
        if high_time > 1000:
            command |= 1 << bit     # set this bit to 1

    # ——— Print the result ———
    print("Button code =", hex(command))
    if command == 0:
        lightEnabled = True
    if command == 1:
        lightEnabled = False

    # tiny pause so repeats are clean
    sleep(0.3)
    