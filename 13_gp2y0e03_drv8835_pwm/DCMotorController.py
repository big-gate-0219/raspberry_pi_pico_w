
class DCMotorController:
    """DCモーターを制御するためのクラス。

    Args:
        pin1 (machine.Pin): モーターの制御に使用するピン1
        pin2 (machine.Pin): モーターの制御に使用するピン2
    """

    def __init__(self, pin1, pin2):
        self._pin1 = pin1
        self._pin2 = pin2

    def move_forward(self):
        """モーターを前進させます。"""
        self._set_pin_values(1, 0)

    def move_backward(self):
        """モーターを後退させます。"""
        self._set_pin_values(0, 1)

    def stop(self):
        """モーターを停止させます。"""
        self._set_pin_values(1, 1)

    def coast(self):
        """モーターをフリー回転させます。"""
        self._set_pin_values(0, 0)

    def _set_pin_values(self, value1, value2):
        """ピンの値を設定します。

        Args:
            value1 (int): ピン1の設定値 (0または1)
            value2 (int): ピン2の設定値 (0または1)
        """
        self._pin1.value(value1)
        self._pin2.value(value2)
