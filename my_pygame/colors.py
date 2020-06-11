# -*- coding: Utf-8 -*

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
GRAY_DARK = (135, 135, 135)
GRAY_LIGHT = (175, 175, 175)
RED = (255, 0, 0)
RED_DARK = (195, 0, 0)
RED_LIGHT = (255, 100, 100)
ORANGE = (255, 175, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GREEN_DARK = (0, 128, 0)
GREEN_LIGHT = (128, 255, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
BLUE_DARK = (0, 0, 128)
BLUE_LIGHT = (128, 128, 255)
MAGENTA = (255, 0, 255)
PURPLE = (165, 0, 255)
TRANSPARENT = (0, 0, 0, 0)

class Color(object):
    def __init__(self, red, green, blue, alpha=255):
        self.__red = 0
        self.__green = 0
        self.__blue = 0
        self.__alpha = 0
        self.__hue = 0
        self.__saturation = 0
        self.__value = 0
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    @classmethod
    def from_hsv(cls, h, s, v, alpha=255):
        color = cls(0, 0, 0, alpha)
        color.h = h
        color.s = s
        color.v = v
        return color

    @classmethod
    def from_hex(cls, hex_code, alpha=255):
        if not isinstance(hex_code, str):
            raise TypeError("hex_code must be a str")
        if hex_code[0] != "#":
            raise ValueError("hex_code must start with a '#' character")
        hex_code = hex_code[1:]
        if len(hex_code) != 6:
            raise ValueError("hex_code must be formatted by #RRGGBB")
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return cls(r, g, b, alpha)

    def __repr__(self):
        return f"Color: red={self.red}, green={self.green}, blue={self.blue}, alpha={self.alpha}"

    def __str__(self):
        return repr(self)

    def get(self):
        if self.alpha < 255:
            return (self.red, self.green, self.blue, self.alpha)
        return (self.red, self.green, self.blue)

    @property
    def red(self):
        return self.__red

    @red.setter
    def red(self, value):
        value = int(value)
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.__red = value
        self.__calculate_hsv_from_rgb()

    @property
    def green(self):
        return self.__green

    @green.setter
    def green(self, value):
        value = int(value)
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.__green = value
        self.__calculate_hsv_from_rgb()

    @property
    def blue(self):
        return self.__blue

    @blue.setter
    def blue(self, value):
        value = int(value)
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.__blue = value
        self.__calculate_hsv_from_rgb()

    @property
    def alpha(self):
        return self.__alpha

    @alpha.setter
    def alpha(self, value):
        value = int(value)
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.__alpha = value

    @property
    def h(self):
        return self.__hue

    @h.setter
    def h(self, value):
        while value < 0:
            value += 360
        while value >= 360:
            value -= 360
        self.__hue = value
        self.__calculate_rgb_from_hsv()

    @property
    def s(self):
        return self.__saturation

    @s.setter
    def s(self, value):
        if value < 0:
            value = 0
        elif value > 100:
            value = 100
        self.__saturation = value
        self.__calculate_rgb_from_hsv()

    @property
    def v(self):
        return self.__value

    @v.setter
    def v(self, value):
        if value < 0:
            value = 0
        elif value > 100:
            value = 100
        self.__value = value
        self.__calculate_rgb_from_hsv()

    @property
    def hex(self):
        value = "#"
        for color in (self.red, self.green, self.blue):
            value += "{0:0>2X}".format(color)
        return value

    def __calculate_hsv_from_rgb(self):
        r = self.red / 255
        g = self.green / 255
        b = self.blue / 255
        c_max = max((r, g, b))
        c_min = min((r, g, b))
        delta = c_max - c_min
        hue = {
            r: 0 if delta == 0 else 60 * (((g - b) / delta) % 6),
            g: 0 if delta == 0 else 60 * (((b - r) / delta) + 2),
            b: 0 if delta == 0 else 60 * (((r - g) / delta) + 4)
        }
        self.__hue = round(hue[c_max])
        self.__saturation = 0 if c_max == 0 else round(100 * delta / c_max)
        self.__value = round(100 * c_max)

    def __calculate_rgb_from_hsv(self):
        h = self.h
        s = self.s / 100
        v = self.v / 100
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        hue_colors = {
            (0, 60): (c, x, 0),
            (60, 120): (x, c, 0),
            (120, 180): (0, c, x),
            (180, 240): (0, x, c),
            (240, 300): (x, 0, c),
            (300, 360): (c, 0, x)
        }
        r = 0
        g = 0
        b = 0
        for interval, hue in hue_colors.items():
            v_min, v_max = interval
            if v_min <= h < v_max:
                r, g, b = hue
                break
        self.__red = round((r + m) * 255)
        self.__green = round((g + m) * 255)
        self.__blue = round((b + m) * 255)

def change_brightness(color: tuple, value: int) -> tuple:
    c = Color(*color)
    c.v += value
    return c.get()

def change_saturation(color: tuple, value: int) -> tuple:
    c = Color(*color)
    c.s += value
    return c.get()