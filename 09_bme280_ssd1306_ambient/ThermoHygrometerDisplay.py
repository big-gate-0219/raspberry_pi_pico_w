class ThermoHygrometerDisplay:
    """
    SSD1306グラフィックディスプレイ
    """
    
    def __init__(self, display):
        """
        SSD1306_Displayクラスのコンストラクタ
        
        Args:
            display(SSD1306_I2C): SSD1306情報
        """
        self.__display = display
    
    
    def display_wifi_connecting(self):
        """
        WiFi接続画面の初期表示を行う。
        """
        self.__display.fill(0)
        self.__display.text("WiFi Connecting", 2, 2, True)
        self.__display.fill_rect(0, 15, 121, 12, True)
        self.__display.show()    
    
    def update_wifi_connecting(self, count):
        """
        WiFi接続画面の更新表示を行う。
        
        Args:
            count(int): WiFi接続試行回数
        """
        self.__display.fill_rect(120 - count - 2, 16, 2, 10, False)
        self.__display.show()    
    
    def display_thermo_hygrometer(self, now, data):
        """
        """
        self.__display.fill(0)
        self.__display.text("{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(now[1], now[2], now[3], now[4], now[5]), 2, 2, True)
        self.__display.hline(0, 12, 128, True)
        self.__display.vline(70, 12, 14, True)
        self.__display.hline(0, 26, 128, True)
        self.__display.hline(0, 42, 128, True)
        self.__display.text("{:.01f}deg.".format(data.temperature), 2, 16, True)
        self.__display.text("{:.01f}%".format(data.humidity), 75, 16, True)
        self.__display.text("{:.01f}hPa".format(data.pressure), 2, 30, True)
        self.__display.text(data.feeling, 2, 46, True)
        self.__display.show()
    
    
    def display_not_connect_wifi(self):
        """
        WiFi接続が出来なかったことを画面に表示する
        """
        self.__display.fill(0)
        self.__display.text("NotConnect WiFi", 2, 2, True)
        self.__display.show()
