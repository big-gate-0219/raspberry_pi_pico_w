# Ambientへのデータ送信テスト

このままでは、RaspberryPi pico wで動作不可。

PCでのPythonでは動作確認済み。

### IDE

Thonnyを使用。

### 使用言語

Python

### 使用ライブラリ

- ambient

### WIFI接続情報

WIFI接続情報は、`config.json`の以下２変数で設定する。

```json
{
    "wifi_ssid": "Enter WIFI ssid",
    "wifi_pass": "Enter Wifi password"
}
```

### Ambient接続情報

Ambient接続情報は、`main.py`の以下２変数で設定する。

```python

channelId = 'MY_AMBIENT_CHID'
writeKey = 'MY_AMBIENT_WKEY'
```

## Ambientの設定

Ambientの項目には下表のように情報が登録される

| Ambientの項目 | 登録される値             |
| ------------- | ------------------------ |
| d1            | 登録対象の値（ランダム） |
