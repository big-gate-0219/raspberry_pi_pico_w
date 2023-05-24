# RaspberryPi pico WをWIFI接続してWebサーバにする

 RaspberryPi pico WをWIFI接続してWebサーバにする。

 Webページのボタン押下でRaspberryPi pico WのLEDを操作する。

## 開発環境

### IDE

Thonnyを使用。

### 使用言語

MicroPython(Raspbery Pi Pico)

### 使用ライブラリ

- picozero

### WIFI接続情報

WIFI接続情報は、`main.py`の以下２変数で設定する。

```python
ssid = 'MY_WIFI_SSID'
password = 'MY_WIFI_PASSWORD'
```
