import time
from machine import Pin, PWM, I2C
import rp2

GP2Y0E03_ADDR = 0x40
I2C_SDA = 12
I2C_SCL = 13
I2C_CH  =0

LED_PIN = 15
SW_PIN = 16
SERVO_PIN = 18
PWM_FREQ = 50

STATE_MACHINE_SW = 0
STATE_MACHINE_FREQ = 2000

pin_led = Pin(LED_PIN, Pin.OUT)
sw_pin = Pin(SW_PIN, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(SERVO_PIN))
servo.freq(PWM_FREQ)
i2c = I2C(I2C_CH, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=100000)
i2c.scan()

@rp2.asm_pio()
def checkpin():
    wrap_target()
    wait(0, pin, 0)
    set(x, 0)
    mov(isr, x)
    push()
    irq(0)
    nop() [31]
    wait(1, pin, 0)
    set(x, 1)
    mov(isr, x)
    push()
    irq(0)
    nop() [31]
    wrap()


def handle_switch(sm_sw):
    value = sm_sw.get()
    print("Switch value: [{}]".format(value))
    if value == 0:
        WAIT_SEC = 1
        pin_led.high()
        duty = pulse_width(1500)
        servo.duty_u16(duty)
        time.sleep(WAIT_SEC)

        duty = pulse_width(2500)
        servo.duty_u16(duty)
        pin_led.low()

def pulse_width(val, freq =PWM_FREQ, resol = 65535):
    pulse = freq * val * 1e-6 * resol
    return int(pulse)


sm_sw = rp2.StateMachine(STATE_MACHINE_SW, checkpin, freq=STATE_MACHINE_FREQ, in_base=sw_pin)
sm_sw.irq(handle_switch)
sm_sw.active(1)


count = 0
while True:
    count += 1
    
    shift = i2c.readfrom_mem( GP2Y0E03_ADDR, 0x35, 1 )[0]
    d_h = i2c.readfrom_mem( GP2Y0E03_ADDR, 0x5e, 1 )[0]
    d_l = i2c.readfrom_mem( GP2Y0E03_ADDR, 0x5f, 1 )[0]
    distance = (d_h * 16 + d_l) / 16 / pow(2, shift)
    print("Distance : {:.1f}cm".format(distance))
    
    if distance < 6:
        WAIT_SEC = 1
        pin_led.high()
        duty = pulse_width(1500)
        servo.duty_u16(duty)
    elif distance > 10:
        duty = pulse_width(2500)
        servo.duty_u16(duty)
        pin_led.low()
    time.sleep(.5)





