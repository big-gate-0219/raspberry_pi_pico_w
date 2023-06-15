from machine import Pin
import rp2
import time
import rp2
from machine import Pin
import time

LED_PIN = 15
SW_PIN = 16
STATE_MACHINE_LED = 0
STATE_MACHINE_SW = 1
STATE_MACHINE_FREQ = 2000

pin_led = Pin(LED_PIN, Pin.OUT)
sw_pin = Pin(SW_PIN, Pin.IN, Pin.PULL_UP)

@rp2.asm_pio()
def checkpin():
    wrap_target()
    wait(0, pin, 0)
    set(x, 0)
    mov(isr, x)
    push()
    irq(1)
    nop() [31]
    wait(1, pin, 0)
    set(x, 1)
    mov(isr, x)
    push()
    irq(1)
    nop() [31]
    wrap()


def handle_switch(sm_sw):
    value = sm_sw.get()
    print("Switch value: [{}]".format(value))
    if value == 1:
        pin_led.low()
    else:
        pin_led.high()

def initialize():
    sm_sw = rp2.StateMachine(STATE_MACHINE_SW, checkpin, freq=STATE_MACHINE_FREQ, in_base=sw_pin)
    sm_sw.irq(handle_switch)
    sm_sw.active(1)


initialize()
count = 0
while True:
    count += 1
    print("Count: {},".format(count))
    time.sleep(1)



