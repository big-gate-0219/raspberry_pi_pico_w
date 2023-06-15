from machine import Pin, PWM
import time

SERVO_PIN = 16
PWM_FREQ = 50

def pulse_width(val, freq =PWM_FREQ, resol = 65535):
    pulse = freq * val * 1e-6 * resol
    return int(pulse)

def smooth_move(servo, start, end, duration, steps):
    step_size = (end - start) / steps
    delay = duration / steps

    for _ in range(steps):
        duty = pulse_width(start)
        servo.duty_u16(duty)
        time.sleep(delay)
        start += step_size


servo = PWM(Pin(SERVO_PIN))
servo.freq(PWM_FREQ)

# 使用例
# duty = pulse_width(500)
# servo.duty_u16(duty)
# time.sleep(1)
# smooth_move(servo, 500, 2500, 1, 100)



WAIT_SEC = 1

while True:
    duty = pulse_width(500)
    servo.duty_u16(duty)
    time.sleep(WAIT_SEC)

    duty = pulse_width(2500)
    servo.duty_u16(duty)
    time.sleep(WAIT_SEC)


