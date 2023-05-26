import time
import network
import urequests
from machine import Pin, I2C
from picozero import pico_led
from ssd1306 import SSD1306_I2C
from bme280 import BME280

import config

# I2C CONSTANT
SDA_PIN = Pin(0)
SCL_PIN = Pin(1)

# SSD1306 CONSTANT
WIDTH = 128
HEIGHT = 64

#####################
## WiFiに接続する
#####################
def connect(display, ssid, password):
    """WiFiに接続する
    Args:
        display : SSD1306情報
        ssid: 接続対象WifiのSSID
        password: 接続対象Wifiのパスワード
    Returns:
        string : 接続した時のIPアドレス
        None : 接続失敗
    """
    display.fill(0)
    display.text("WiFi Connecting", 2, 2, True)
    display.fill_rect(0, 15, 121, 12, True)
    display.show()

    pico_led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    for i in range(60):
        pico_led.toggle()
        display.fill_rect(120 - i - 2, 16, 2, 10, False)
        display.show()
        if wlan.isconnected():
            pico_led.off()
            return wlan.ifconfig()[0]
        time.sleep(1)
    
    pico_led.off()
    return None

#####################
# BME280の補正済データから気温を取得する
#####################
def get_temperature(bme280_compensated_data):
    """BME280の補正済データから気温を取得する
    Args:
        bme280_compensated_data: BME280で計測した補正済データ
    Returns:
        float: BME280の補正済データから計算した気温
    """
    return bme280_compensated_data[0] / 100

#####################
# BME280の補正済データから気圧を取得する
#####################
def get_pressure(bme280_compensated_data):
    """BME280の補正済データから気圧を取得する
    Args:
        bme280_compensated_data: BME280で計測した補正済データ
    Returns:
        float: BME280の補正済データから気圧した気温
    """
    return bme280_compensated_data[1] / 25600

# BME280の補正済データから湿度を取得する
def get_humidity(bme280_compensated_data):
    """BME280の補正済データから湿度を取得する
    Args:
        bme280_compensated_data: BME280で計測した補正済データ
    Returns:
        float: BME280の補正済データから湿度した気温
    """
    return bme280_compensated_data[2] / 1024

#####################
# 温度と湿度から不快指数を取得する
#####################
def get_discomfort_index(temp, humidity):
    """温度と湿度から不快指数を取得する
    Args:
        temp: 温度
        humidity: 湿度
    Returns:
        float: 不快指数
    """
    return 0.81 * temp + 0.01*humidity*(0.99 * temp - 14.3) + 46.3

# 不快指数から人が感じる感覚を取得する
def get_feeling(discomfort_index):
    """不快指数から人がかじる感覚を取得する
    Args:
        discomfort_index: 不快指数
    Returns:
        String: 人が感じる感覚
    """
    if discomfort_index < 55:
        feeling = "Colod"
    elif discomfort_index < 60:
        feeling = "Chilly"
    elif discomfort_index < 65:
        feeling = "Don't feel"
    elif discomfort_index < 70:
        feeling = "Pleasant"
    elif discomfort_index < 75:
        feeling = "Not hot" 
    elif discomfort_index < 80:
        feeling = "Slightly hot"
    elif discomfort_index < 85:
        feeling = "Hot and sweaty"
    else:
        feeling = "Too hot"
    return feeling

#####################
# 温湿度気圧情報を画面に表示する
#####################
def display_thermo_hygrometer(display, temp, humidity, pressure, feeling):
    """温湿度気圧情報を画面に表示する
    Args:
        display : SSD1306情報
        temp: 温度
        humidity: 湿度
        pressure: 気圧
        feeling: 人が感じる感覚
    Returns:
        Nothing
    """
    now = time.localtime()
    display.fill(0)
    display.text("{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(now[1], now[2], now[3], now[4],now[5]), 2, 2, True)
    display.hline(0, 12, 128, True)
    display.vline(70, 12, 14, True)
    display.hline(0, 26, 128, True)
    display.hline(0, 42, 128, True)
    display.text("{:.01f}deg.".format(temp), 2, 16, True)
    display.text("{:.01f}%".format(humidity), 75, 16, True)
    display.text("{:.01f}hPa".format(pressure), 2, 30, True)
    display.text(feeling, 2, 46, True)
    display.show()

#####################
# 温湿度気圧情報表示機能を実行
#####################
def do_thermo_hygrometer(display, bme280):
    """温湿度気圧情報を画面に表示する
    Args:
        display : SSD1306情報
        bme280: bme280の接続情報
    """
    ## Setting Ambient Information
    url = 'http://ambidata.io/api/v2/channels/'+config.ambient_chid+'/data'
    head = {'Content-Type':'application/json'}
    body = {'writeKey':config.ambient_wkey, 'amdient_tag':0.0}
    communication_count = 0 # ambientに通信するタイミング用カウント

    ## 定期的に温湿度気圧を計測
    while True:
        bme280_result = bme280.read_compensated_data()
        temperature = get_temperature(bme280_result)
        pressure = get_pressure(bme280_result)
        humidity = get_humidity(bme280_result)
        discomfort_index = get_discomfort_index(temperature, humidity)
        feeling = get_feeling(discomfort_index)
        display_thermo_hygrometer(display, temperature, humidity, pressure, feeling)
        communication_count = communication_count + 1
        if communication_count > 10:
            communication_count = 0
            pico_led.on()
            body = {'d1': temperature, 'd2': humidity, 'd3': pressure, 'd4': discomfort_index, 'd5': feeling}
            res = urequests.post(url, json=body, headers=head)
            res.close()
            pico_led.off()
        time.sleep(1)
        
#####################
# WiFi接続が出来なかったことを画面に表示する
#####################
def display_not_connect_wifi(display):
    """WiFi接続が出来なかったことを画面に表示する
    Args:
        display : SSD1306情報
    """
    display.fill(0)
    display.text("NotConnect WiFi", 2, 2, True)
    display.show()
    
#####################
# Main Logic
#####################
## センサーに接続
i2c = I2C(0, sda = SDA_PIN, scl = SCL_PIN)
bme280 = BME280(i2c = i2c)
ssd1306 = SSD1306_I2C(WIDTH, HEIGHT, i2c)

## WIFIに接続
ip = connect(ssd1306, config.wifi_ssid, config.wifi_pass)

## WiFi接続成功したら音湿度気圧表示を行う
if ip is not None:
    do_thermo_hygrometer(ssd1306, bme280)
else:
    display_not_connect_wifi(ssd1306)
