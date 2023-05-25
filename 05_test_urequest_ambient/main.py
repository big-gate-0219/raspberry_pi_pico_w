import config

import network
import random
import urequests
from time import sleep
from picozero import pico_temp_sensor, pico_led

def connect(ssid, password):
    pico_led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print('Waiting for connection', end='')
    while not wlan.isconnected():
        pico_led.toggle()
        print('.', end='')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print('')
    print(f'Connected on {ip}')
    pico_led.off()
    return ip

# Setting Ambient Information
url = 'http://ambidata.io/api/v2/channels/'+config.ambient_chid+'/data'
head = {'Content-Type':'application/json'}
body = {'writeKey':config.ambient_wkey, 'amdient_tag':0.0}

# Main logic
connect(config.wifi_ssid, config.wifi_pass)
for i in range(0, 20, 1):
    pico_led.on()
    temperature = pico_temp_sensor.temp
    body['d1'] = temperature
    res = urequests.post(url, json=body, headers=head)
    print(' HTTP Status=', res.status_code)
    res.close()
    pico_led.off()
    sleep(60)
