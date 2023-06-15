from machine import Pin
import time

LED_PIN =15
SW_PIN = 16

led = Pin(LED_PIN, Pin.OUT)
sw = Pin(SW_PIN, Pin.IN, Pin.PULL_DOWN)
counter = 0

while True:
    if (sw.value() ==1):
        if counter == 10:
            led.high()
        elif counter == 20:
            led.low()
        elif counter == 30:
            counter = 0
        counter = counter + 1
    else:
        counter = 0
        led.low()
    time.sleep(.01)
