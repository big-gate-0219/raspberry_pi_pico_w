from picozero import pico_temp_sensor, pico_led
from machine import Pin, I2C
from time import sleep
from bme280 import BME280

i2c = I2C(0, sda = Pin(0), scl = Pin(1), freq = 40000)
addr = i2c.scan()
print(hex(addr[0]))

bme = BME280(i2c = i2c)

for i in range(0, 20, 1):
    result = bme.read_compensated_data()
    temp = result[0] / 100
    pressure = result[1] / 25600
    humidity = result[2] / 1024
    print(temp)
    print(pressure)
    print(humidity)
    print(bme.values)
    print("-------")
    sleep(2)
