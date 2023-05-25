import json
import random
import time
import ambient

# SETTING
CONFIG_FILE = 'config.json'

# Constant Values
WIFI_SSID = 'wifi_ssid'
WIFI_PASS = 'wifi_pass'

# MAIN LOGIC
config = json.load(open(CONFIG_FILE, 'r'))
print(config[WIFI_SSID])
print(config[WIFI_PASS])

channelId = 'MY_AMBIENT_CHID'
writeKey = 'MY_AMBIENT_WKEY'

am = ambient.Ambient(channelId, writeKey)

for i in range(0, 10, 1):
    r = am.send({'d1': random.uniform(10, 30)})
    print(r.status_code)
    time.sleep(10)
