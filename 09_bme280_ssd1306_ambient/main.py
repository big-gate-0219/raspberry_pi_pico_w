import time
import network
import urequests
from machine import Pin, I2C
from picozero import pico_led
from ssd1306 import SSD1306_I2C
from bme280 import BME280

from ThermoHygrometerData import ThermoHygrometerData
from ThermoHygrometerDisplay import ThermoHygrometerDisplay
import config

# I2C Settings
SDA_PIN = Pin(0)
SCL_PIN = Pin(1)
i2c = I2C(0, sda=SDA_PIN, scl=SCL_PIN)

# BME280 Settings
bme280_sensor = BME280(i2c=i2c)

# SSD1306 Settings
SSD1306_WIDTH = 128
SSD1306_HEIGHT = 64
ssd1306_display = SSD1306_I2C(SSD1306_WIDTH, SSD1306_HEIGHT, i2c)
display = ThermoHygrometerDisplay(ssd1306_display)


def connect(wifi_config):
    """WiFiに接続する
    Args:
        ssid: 接続対象WifiのSSID
        password: 接続対象Wifiのパスワード
    Returns:
        string : 接続した時のIPアドレス
        None : 接続失敗
    """
    display.display_wifi_connecting()
    pico_led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_config['ssid'], wifi_config['password'])

    for i in range(60):
        pico_led.toggle()
        display.update_wifi_connecting(i)
        if wlan.isconnected():
            pico_led.off()
            return wlan.ifconfig()[0]
        time.sleep(1)

    pico_led.off()
    return None    


def post_data_to_ambient(ambient_config, data):
    """
    Ambientにデータを送信する関数

    Args:
        url (str): Ambient APIのURL
        headers (dict): リクエストヘッダー
        data (ThermoHygrometerData): 送信する温湿度気圧データを表すThermoHygrometerDataオブジェクト
        ambient_wkey (str): Ambientの書き込みキー
        ambient_tag (float): Ambientのタグ

    """
    ambient_tag = 0.0
    url = 'http://ambidata.io/api/v2/channels/{}/data'.format(ambient_config['chid'])
    headers = {'Content-Type': 'application/json'}
    body = {
        'writeKey': ambient_config['wkey'],
        'ambient_tag': ambient_tag,
        'd1': data.temperature,
        'd2': data.humidity,
        'd3': data.pressure,
        'd4': data.discomfort_index,
        'd5': data.feeling
    }
    
    res = urequests.post(url, json=body, headers=headers)
    res.close()


def do_thermo_hygrometer(ambient_config):
    """温湿度気圧情報を画面に表示する
    Args:
        ambient_chid: AmbientチャンネルID
        ambient_wkey: Ambientの書き込みキー
    """
    communication_interval = 10

    communication_count = 0
    while True:
        now = time.localtime()
        compensated_data = bme280_sensor.read_compensated_data()
        data = ThermoHygrometerData(compensated_data)
        display.display_thermo_hygrometer(now, data)
        communication_count += 1
        if communication_count > communication_interval:
            pico_led.on()
            communication_count = 0
            post_data_to_ambient(ambient_config, data)
            pico_led.off()
        time.sleep(1)


#####################
# Main Logic
#####################

# WIFIに接続
ip = connect(config.wifi)

# WiFi接続成功したら音湿度気圧表示を行う
if ip is not None:
    do_thermo_hygrometer(config.ambient)
else:
    display.display_not_connect_wifi()
