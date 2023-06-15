from machine import Pin
import time

PIR_PIN = 2

pir = Pin(PIR_PIN, Pin.IN)

while True:
    value = pir.value()
    print(value)
#     if value == 1:
#         print("Visitor.")
#     else:
#         print("Nobody.")
    
    time.sleep(1)
