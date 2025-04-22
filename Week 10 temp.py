from machine import Pin, ADC, PWM
from time import sleep
import _thread
     
pir = Pin(0)
leds = [
    Pin(2, Pin.OUT), # Red
    Pin(3, Pin.OUT), # Green
    Pin(4, Pin.OUT)  # Blue
]

buzzers = [
    PWM(Pin(10)),
    PWM(Pin(11))
]

max_volume = 2000
alarm_cycles = 2

global isTriggered
isTriggered = False

def led_off():
    for led in leds:
        led.off()

def led_on():
     for led in leds:
        led.on()

def alarm():
    global isTriggered
    while True:
        if isTriggered:
            print("triggered")
            freq = 800
            for i in range(alarm_cycles):
                leds[0].on()
                for buzzer in buzzers:
                    led_on()
                    buzzer.duty_u16(max_volume)
                    buzzer.freq(freq)
                    sleep(0.1)
                    buzzer.duty_u16(0)
                led_off()
                sleep(0.1)

_thread.start_new_thread(alarm, ())
    
while True:
        brightness = pir.value()
        
        if brightness == 1:
            isTriggered = True
        else:
            isTriggered = False