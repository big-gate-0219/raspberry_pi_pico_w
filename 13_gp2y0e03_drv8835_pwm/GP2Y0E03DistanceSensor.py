from machine import I2C

class GP2Y0E03DistanceSensor:
    """GP2Y0E03距離センサーを制御するクラス"""

    I2C_ADDR_GP2Y0E03 = 0x40
    I2C_CH = 0
    REGISTER_ADDR_SHIFT_BIT = 0x35
    REGISTER_ADDR_DISTANCE_HIGH = 0x5e
    REGISTER_ADDR_DISTANCE_LOW = 0x5f

    def __init__(self, scl_pin, sda_pin):
        """GP2Y0E03DistanceSensorのコンストラクタ

        Args:
            scl_pin (machine.Pin): I2CのSCLピン
            sda_pin (machine.Pin): I2CのSDAピン
        """
        self._sensor_addr = self.I2C_ADDR_GP2Y0E03
        self._i2c = I2C(self.I2C_CH, scl=scl_pin, sda=sda_pin, freq=100000)
    
    
    def distance(self):
        """センサーからの距離を取得する

        Returns:
            dict: 距離と測定結果の辞書 {'distance': float, 'measured': bool}
        """
        try:
            shift = self._i2c.readfrom_mem(self._sensor_addr, self.REGISTER_ADDR_SHIFT_BIT, 1)[0]
            distance_high = self._i2c.readfrom_mem(self._sensor_addr, self.REGISTER_ADDR_DISTANCE_HIGH, 1)[0]
            distance_low = self._i2c.readfrom_mem(self._sensor_addr, self.REGISTER_ADDR_DISTANCE_LOW, 1)[0]

            distance = (distance_high * 16 + distance_low) / 16 / pow(2, shift)
            measured = (distance_high != 255) or (distance_low != 15)

            return {'distance': distance, 'measured': measured}
        except OSError as e:
            print("I2C通信エラー:", e)
            return {'distance': 0.0, 'measured': False}
