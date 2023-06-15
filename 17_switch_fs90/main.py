import time
from machine import Pin, PWM
import rp2

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
    print("Count: {},".format(count))
    time.sleep(1)




