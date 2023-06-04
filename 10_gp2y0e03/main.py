from machine import Pin, I2C
import time

GP2Y0E03_ADDR = 0x40
I2C_SDA = 12
I2C_SCL = 13
I2C_CH  =0

i2c = I2C(I2C_CH, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=100000)
i2c.scan()

while True:
    shift = i2c.readfrom_mem( GP2Y0E03_ADDR, 0x35, 1 )[0]
    d_h = i2c.readfrom_mem( GP2Y0E03_ADDR, 0x5e, 1 )[0]
    d_l = i2c.readfrom_mem( GP2Y0E03_ADDR, 0x5f, 1 )[0]
    distance = (d_h * 16 + d_l) / 16 / pow(2, shift)
    print("Distance : {:.1f}cm".format(distance))
    time.sleep(.5)
