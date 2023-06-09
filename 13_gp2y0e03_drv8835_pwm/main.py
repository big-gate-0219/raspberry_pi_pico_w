from machine import Pin
import time
from GP2Y0E03DistanceSensor import GP2Y0E03DistanceSensor
from DCMotorController import DCMotorController
from PwmController import PwmController
        
GP2Y0E03_I2C_SDA = 12
GP2Y0E03_I2C_SCL = 13
MOTOR_PIN1 = 18
MOTOR_PIN2 = 19

def map_value(value, in_min, in_max, out_min, out_max):
    """値を範囲内にマッピングするユーティリティ関数"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


distance_sensor = GP2Y0E03DistanceSensor(Pin(GP2Y0E03_I2C_SCL), Pin(GP2Y0E03_I2C_SDA))

motorController = DCMotorController(Pin(MOTOR_PIN1, Pin.OUT), Pin(MOTOR_PIN2, Pin.OUT))    
controller = PwmController(motorController, 10000, 50)

controller.start()
controller.move_forward()
controller.duty_ratio(50)

for i in range(500):
    distance = distance_sensor.distance()
    
    if distance['distance'] < 10:
        controller.stop()   
    else:
        duty_ratio = map_value(distance['distance'], 10, 40, 10, 50)
        controller.move_forward()
        controller.duty_ratio(duty_ratio)

    time.sleep(.1)

controller.stop()
controller.finish()
