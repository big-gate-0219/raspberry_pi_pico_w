import json

# SETTING
CONFIG_FILE = 'config.json'

# Constant Values
WIFI_SSID = 'wifi_ssid'
WIFI_PASS = 'wifi_pass'

# MAIN LOGIC
config = json.load(open(CONFIG_FILE, 'r'))
print(config[WIFI_SSID])
print(config[WIFI_PASS])
