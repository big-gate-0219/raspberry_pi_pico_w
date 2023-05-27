import time
import network
import urequests
from machine import Pin, I2C
from picozero import pico_led
from ssd1306 import SSD1306_I2C
from bme280 import BME280

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


class ThermoHygrometerData:
    """
    温湿度気圧データを表すクラス
    """

    # 不快指数と人が感じる感覚の関係
    THRESHOLDS = [
        (0, 55, "Cold"),
        (55, 60, "Chilly"),
        (60, 65, "Don't feel"),
        (65, 70, "Pleasant"),
        (70, 75, "Not hot"),
        (75, 80, "Slightly hot"),
        (80, 85, "Hot and sweaty"),
        (85, 1000, "Too hot")
    ]
    
    
    def __init__(self, compensated_data):
        self.temperature = compensated_data[0] / 100
        self.humidity = compensated_data[2] / 1024
        self.pressure = compensated_data[1] / 25600
        self.discomfort_index = self.__calculate_discomfort_index(self.temperature, self.humidity)
        self.feeling = self.__get_feeling(self.discomfort_index)
        
    
    def __calculate_discomfort_index(self, temperature, humidity):
        """温度と湿度から不快指数を取得する
        Args:
            temperature: 温度
            humidity: 湿度
        Returns:
            float: 不快指数
        """
        return 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3
    
    
    def __get_feeling(self, discomfort_index):
        """不快指数から人が感じる感覚を取得する
        Args:
            discomfort_index: 不快指数
        Returns:
            str: 人が感じる感覚
        """
        for low, high, feeling in ThermoHygrometerData.THRESHOLDS:
            if discomfort_index >= low and discomfort_index < high:
                return feeling

        return "Unknown"


def connect(ssid, password):
    """WiFiに接続する
    Args:
        ssid: 接続対象WifiのSSID
        password: 接続対象Wifiのパスワード
    Returns:
        string : 接続した時のIPアドレス
        None : 接続失敗
    """
    ssd1306_display.fill(0)
    ssd1306_display.text("WiFi Connecting", 2, 2, True)
    ssd1306_display.fill_rect(0, 15, 121, 12, True)
    ssd1306_display.show()

    pico_led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    for i in range(60):
        pico_led.toggle()
        ssd1306_display.fill_rect(120 - i - 2, 16, 2, 10, False)
        ssd1306_display.show()
        if wlan.isconnected():
            pico_led.off()
            return wlan.ifconfig()[0]
        time.sleep(1)

    pico_led.off()
    return None


def display_thermo_hygrometer(data):
    """温湿度気圧情報を画面に表示する
    Args:
        temp: 温度
        humidity: 湿度
        pressure: 気圧
        feeling: 人が感じる感覚
    Returns:
        Nothing
    """
    now = time.localtime()
    ssd1306_display.fill(0)
    ssd1306_display.text("{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(now[1], now[2], now[3], now[4], now[5]), 2, 2, True)
    ssd1306_display.hline(0, 12, 128, True)
    ssd1306_display.vline(70, 12, 14, True)
    ssd1306_display.hline(0, 26, 128, True)
    ssd1306_display.hline(0, 42, 128, True)
    ssd1306_display.text("{:.01f}deg.".format(data.temperature), 2, 16, True)
    ssd1306_display.text("{:.01f}%".format(data.humidity), 75, 16, True)
    ssd1306_display.text("{:.01f}hPa".format(data.pressure), 2, 30, True)
    ssd1306_display.text(data.feeling, 2, 46, True)
    ssd1306_display.show()
    

def get_thermo_hygrometer_data():
    """
    温湿度気圧データを取得する関数

    Returns:
        ThermoHygrometerData: 温湿度気圧データを表すThermoHygrometerDataオブジェクト

    """
    compensated_data = bme280_sensor.read_compensated_data()
    return ThermoHygrometerData(compensated_data)


def post_data_to_ambient(url, headers, body):
    """
    Ambientにデータをポストする関数

    Args:
        url (str): Ambient APIのURL
        headers (dict): リクエストヘッダー
        body (dict): ポストするデータの本文

    """
    res = urequests.post(url, json=body, headers=headers)
    res.close()


def send_data_to_ambient(url, headers, data, ambient_wkey, ambient_tag):
    """
    Ambientにデータを送信する関数

    Args:
        url (str): Ambient APIのURL
        headers (dict): リクエストヘッダー
        data (ThermoHygrometerData): 送信する温湿度気圧データを表すThermoHygrometerDataオブジェクト
        ambient_wkey (str): Ambientの書き込みキー
        ambient_tag (float): Ambientのタグ

    """
    body = {
        'writeKey': ambient_wkey,
        'ambient_tag': ambient_tag,
        'd1': data.temperature,
        'd2': data.humidity,
        'd3': data.pressure,
        'd4': data.discomfort_index,
        'd5': data.feeling
    }
    post_data_to_ambient(url, headers, body)


def do_thermo_hygrometer(ambient_chid, ambient_wkey):
    """温湿度気圧情報を画面に表示する
    Args:
        ambient_chid: AmbientチャンネルID
        ambient_wkey: Ambientの書き込みキー
    """
    ambient_url = 'http://ambidata.io/api/v2/channels/{}/data'.format(ambient_chid)
    ambient_headers = {'Content-Type': 'application/json'}
    ambient_tag = 0.0
    communication_interval = 10

    communication_count = 0
    while True:
        data = get_thermo_hygrometer_data()
        display_thermo_hygrometer(data)
        communication_count += 1
        if communication_count > communication_interval:
            communication_count = 0
            send_data_to_ambient(ambient_url, ambient_headers, data, ambient_wkey, ambient_tag)
        time.sleep(1)


def display_not_connect_wifi():
    """WiFi接続が出来なかったことを画面に表示する
    """
    ssd1306_display.fill(0)
    ssd1306_display.text("NotConnect WiFi", 2, 2, True)
    ssd1306_display.show()


#####################
# Main Logic
#####################
# WIFIに接続
ip = connect(config.wifi_ssid, config.wifi_pass)

# WiFi接続成功したら音湿度気圧表示を行う
if ip is not None:
    do_thermo_hygrometer(config.ambient_chid, config.ambient_wkey)
else:
    display_not_connect_wifi()
