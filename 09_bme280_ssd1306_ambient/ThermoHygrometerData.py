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
