import time
import _thread

class PwmController:
    """PWM (パルス幅変調) 制御を行うクラスです。

    Args:
        motor_controller (DCMotorController): DCモーターを制御するためのモーターコントローラーオブジェクト
        frequency (float): PWM信号の周波数
        duty_ratio (float): デューティ比（%）
    """
    
    
    QUEUE_TYPE_FREQUENCY = 'Frequency'
    """キューのタイプ: 周波数"""
    
    QUEUE_TYPE_DUTY_RATIO = 'DutyRatio'
    """キューのタイプ: デューティ比"""

    QUEUE_TYPE_DRIVE = 'Drive'
    """キューのタイプ: 運転モード"""
    
    
    def __init__(self, motor_controller, frequency, duty_ratio):
        self._queue = []
        self._stop = False
        self._motor_controller = motor_controller
        self._frequency = frequency
        self._duty_ratio = duty_ratio
        self._drive = motor_controller.stop
    
    
    def move_forward(self):
        """モーターへの前進指示を設定します。"""
        self._add_control_command(self.QUEUE_TYPE_DRIVE, 'move_forward')
    
    
    def move_backward(self):
        """モーターへの後進指示を設定します。"""
        self._add_control_command(self.QUEUE_TYPE_DRIVE, 'move_backward')
    
    
    def stop(self):
        """モーターへのt停止を設定します。"""
        self._add_control_command(self.QUEUE_TYPE_DRIVE, 'stop')
    
    
    def coast(self):
        """モーターへの空転指示を設定します。"""
        self._add_control_command(self.QUEUE_TYPE_DRIVE, 'coast')
    
    
    def frequency(self, frequency):
        """PWM信号の周波数を設定します。

        Args:
            frequency (float): PWM信号の周波数
        """
        self._add_control_command(self.QUEUE_TYPE_FREQUENCY, frequency)
    
    
    def duty_ratio(self, duty_ratio):
        """デューティ比（%）を設定します。

        Args:
            duty_ratio (float): デューティ比（%）
        """
        self._add_control_command(self.QUEUE_TYPE_DUTY_RATIO, duty_ratio)
    
    
    def _add_control_command(self, type, value):
        """制御指示キューに制御指示を追加します。

        Args:
            type (str): 制御指示種類
            value (any): 制御指示内容
        """
        self._queue.append({'type': type, 'value': value})
    
    
    def start(self):
        """PWM制御を開始します。"""
        _thread.start_new_thread(self._controller_thread,())
    
    
    def finish(self):
        """PWM制御を停止します。"""
        self._stop = True
    
    
    def _controller_thread(self):
        """メインのPWM制御スレッドです。"""
        counter = 0
        signal = True
        duty_ratio = self._duty_ratio

        while not self._stop:
            if self._process_queue():
                counter = 0
                signal = True
                duty_ratio = self._duty_ratio
                self._process_signal(signal)
            if counter >= duty_ratio:
                counter = 0
                signal = not signal
                duty_ratio = 100 - duty_ratio
                self._process_signal(signal)
            counter = counter + 1
            time.sleep(1.0 / self._frequency)
        _thread.exit()
    
    
    def _process_signal(self, signal):
        """PWM信号を処理します。

        Args:
            signal (bool): 処理するPWM信号
        """
        if signal:
            self._drive()
        else:
            self._motor_controller.coast()
    
    
    def _process_queue(self):
        """キューに登録された設定情報の処理を行います。"""
        ret = False
        
        while self._queue:
            data = self._queue.pop(0)
            if data['type'] == self.QUEUE_TYPE_FREQUENCY:
                self._frequency = data['value']
                ret = True
            elif data['type'] == self.QUEUE_TYPE_DUTY_RATIO:
                self._duty_ratio = data['value']
                ret = True
            elif data['type'] == self.QUEUE_TYPE_DRIVE:
                self._drive = getattr(self._motor_controller, data['value'])
                ret = True
        return ret
