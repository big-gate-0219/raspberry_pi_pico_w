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


def get_temperature(bme280_compensated_data):
    """BME280の補正済データから気温を取得する
    Args:
        bme280_compensated_data: BME280で計測した補正済データ
    Returns:
        float: BME280の補正済データから計算した気温
    """
    return bme280_compensated_data[0] / 100


def get_pressure(bme280_compensated_data):
    """BME280の補正済データから気圧を取得する
    Args:
        bme280_compensated_data: BME280で計測した補正済データ
    Returns:
        float: BME280の補正済データから気圧した気温
    """
    return bme280_compensated_data[1] / 25600


def get_humidity(bme280_compensated_data):
    """BME280の補正済データから湿度を取得する
    Args:
        bme280_compensated_data: BME280で計測した補正済データ
    Returns:
        float: BME280の補正済データから湿度した気温
    """
    return bme280_compensated_data[2] / 1024


def get_discomfort_index(temp, humidity):
    """温度と湿度から不快指数を取得する
    Args:
        temp: 温度
        humidity: 湿度
    Returns:
        float: 不快指数
    """
    return 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3


def get_feeling(discomfort_index):
    """不快指数から人が感じる感覚を取得する
    Args:
        discomfort_index: 不快指数
    Returns:
        str: 人が感じる感覚
    """
    for low, high, feeling in THRESHOLDS:
        if discomfort_index >= low and discomfort_index < high:
            return feeling

    return "Unknown"


def display_thermo_hygrometer(display, data):
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
    display.text("{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(now[1], now[2], now[3], now[4], now[5]), 2, 2, True)
    display.hline(0, 12, 128, True)
    display.vline(70, 12, 14, True)
    display.hline(0, 26, 128, True)
    display.hline(0, 42, 128, True)
    display.text("{:.01f}deg.".format(data.temperature), 2, 16, True)
    display.text("{:.01f}%".format(data.humidity), 75, 16, True)
    display.text("{:.01f}hPa".format(data.pressure), 2, 30, True)
    display.text(data.feeling, 2, 46, True)
    display.show()


class ThermoHygrometerData:
    """
    温湿度気圧データを表すクラス
    """

    def __init__(self, temperature, humidity, pressure, discomfort_index, feeling):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.discomfort_index = discomfort_index
        self.feeling = feeling


def get_thermo_hygrometer_data(bme280_sensor):
    """
    温湿度気圧データを取得する関数

    Args:
        bme280_sensor (BME280): BME280センサーオブジェクト

    Returns:
        ThermoHygrometerData: 温湿度気圧データを表すThermoHygrometerDataオブジェクト

    """
    bme280_result = bme280_sensor.read_compensated_data()
    temperature = get_temperature(bme280_result)
    pressure = get_pressure(bme280_result)
    humidity = get_humidity(bme280_result)
    discomfort_index = get_discomfort_index(temperature, humidity)
    feeling = get_feeling(discomfort_index)
    return ThermoHygrometerData(temperature, humidity, pressure, discomfort_index, feeling)


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


def do_thermo_hygrometer(display, bme280_sensor, ambient_chid, ambient_wkey):
    """温湿度気圧情報を画面に表示する
    Args:
        display : SSD1306情報
        bme280_sensor: bme280の接続情報
        ambient_chid: AmbientチャンネルID
        ambient_wkey: Ambientの書き込みキー
    """
    ambient_url = 'http://ambidata.io/api/v2/channels/{}/data'.format(ambient_chid)
    ambient_headers = {'Content-Type': 'application/json'}
    ambient_tag = 0.0
    communication_interval = 10

    communication_count = 0
    while True:
        data = get_thermo_hygrometer_data(bme280_sensor)
        display_thermo_hygrometer(display, data)
        communication_count += 1
        if communication_count > communication_interval:
            communication_count = 0
            send_data_to_ambient(ambient_url, ambient_headers, data, ambient_wkey, ambient_tag)
        time.sleep(1)


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
# センサーに接続
i2c = I2C(0, sda=SDA_PIN, scl=SCL_PIN)
bme280 = BME280(i2c=i2c)
ssd1306 = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# WIFIに接続
ip = connect(ssd1306, config.wifi_ssid, config.wifi_pass)

# WiFi接続成功したら音湿度気圧表示を行う
if ip is not None:
    do_thermo_hygrometer(
        ssd1306, bme280, config.ambient_chid, config.ambient_wkey)
else:
    display_not_connect_wifi(ssd1306)
