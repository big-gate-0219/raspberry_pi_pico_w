# Ambientへのデータ送信テスト

### IDE

Thonnyを使用。

### 使用言語

Python

### 使用ライブラリ

- picozero

### WIFI接続情報

WIFI接続情報は、`config.py`の以下２変数で設定する。

```python
wifi_ssid = 'FXC-MY_WIFI_SSID'
wifi_pass = 'MY_WIFI_PASSWORD'
```

### Ambient接続情報

Ambient接続情報は、`config.py`の以下２変数で設定する。

```python
ambient_chid = 'MY_AMBIENT_CHID'
ambient_wkey = 'MY_AMBIENT_WKEY'
```

## Ambientの設定

Ambientの項目には下表のように情報が登録される

| Ambientの項目 | 登録される値                     |
| ------------- | -------------------------------- |
| d1            | RaspberryPi Pico Wで計測した温度 |
