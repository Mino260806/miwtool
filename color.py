from PIL import Image


class Color:
    RGB888 = 0
    RGB565 = 1

    def __init__(self, r, g, b, type):
        self.r = r
        self.g = g
        self.b = b

        self.type = type

    def value(self, endianness="big"):
        if self.type == self.RGB888:
            value = (self.r << 16) + (self.g << 8) + self.b

        elif self.type == self.RGB565:
            value = (self.r << 11) + (self.g << 5) + self.b

        else:
            return 0

        if endianness == "little" and self.type == self.RGB565:
            return self.inversed(value)
        else:
            return value

    @staticmethod
    def inversed(value):
        b = bytearray(int(value).to_bytes(2, "big"))
        return int.from_bytes(b, "little")

    @classmethod
    def fromRGB565(cls, value, endianness="big"):
        if endianness == "little":
            value = cls.inversed(value)
        r = (value & 0xf800) >> (5 + 6)
        g = (value & 0x7e0) >> 5
        b = value & 0x1f
        return Color(r, g, b, cls.RGB565)

    @classmethod
    def fromRGB888(cls, value):
        r = (value & 0xff0000) >> 16
        g = (value & 0x00ff00) >> 8
        b = value & 0x0000ff
        return Color(r, g, b, cls.RGB888)

    def toRGB888(self):
        if self.type == self.RGB888:
            return self
        if self.type == self.RGB565:
            r = round(self.r * (255 / 31))
            g = round(self.g * (255 / 63))
            b = round(self.b * (255 / 31))
            return Color(r, g, b, self.RGB888)
        return None

    def toRGB565(self):
        if self.type == self.RGB565:
            return self
        if self.type == self.RGB888:
            r = round(self.r * (31 / 255))
            g = round(self.g * (63 / 255))
            b = round(self.b * (31 / 255))
            return Color(r, g, b, self.RGB565)
        return None

    def show(self, w=50, h=50):
        color = self.toRGB888()
        image = Image.new("RGB", (w, h), (color.r, color.g, color.b))
        image.show()

    def __str__(self):
        return hex(self.value())
