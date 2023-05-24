from machine import Pin
import time

led = Pin("LED", Pin.OUT)

while True:
    led.high()
    time.sleep(1)
    led.low()
    time.sleep(1)
