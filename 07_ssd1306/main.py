from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import math

WIDTH = 128
HEIGHT = 64

i2c = I2C(0, sda=Pin(16), scl=Pin(17))
addr = i2c.scan()

print("OLED I2C Address : " + hex(addr[0]))
print("I2C Configuration: " +str(i2c))

display = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def circle(x, y, l, color):
    for r in range(360):
        display.pixel(int(x + l * math.cos(math.radians(r))), int(y - l * math.sin(math.radians(r))), color)

def fill_circle(x, y, l, color):
    for r in range(360):
        display.line(x, y, int(x + l * math.cos(math.radians(r))), int(y - l * math.sin(math.radians(r))), color)

def triangle(x1, y1, x2, y2, x3, y3, color):
    display.line(x1, y1, x2, y2, color)
    display.line(x2, y2, x3, y3, color)
    display.line(x1, y1, x3, y3, color)
    
def fill_triangle(x, y, l, color):
    for i in range(int(l/2 * math.tan(math.radians(60)))):
        h = l/2 * math.tan(math.radians(60))
        display.hline(x + math.ceil((i*l/h)/2), y - i, l - math.ceil(i*l/h), color)


display.fill(0)
display.text("OLED Test ", 17, 2, True)
display.hline(0, 12, 128, True)
display.vline(64, 12, 20, True)
display.line(0, 32, 128, 32, True)
display.rect(88, 41, 18, 18, True)
display.fill_rect(109, 41, 18, 18, True)
circle(9, 50, 9, True)
fill_circle(31, 50, 9, True)
triangle(42, 58, 52, 42, 62, 58, True)
fill_triangle(65, 58, 20, True)

display.show()