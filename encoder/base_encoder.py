from io import BytesIO


class Encoder:
    def __init__(self):
        self.offset = 0x0
        self.f = None

    def pin_offset(self):
        self.offset = self.f.tell()

    def unpin_offset(self):
        self.offset = 0x0

    def whereami(self):
        return self.offset + self.f.tell()

    def seek(self, x):
        self.f.seek(self.offset + x)

    def write(self, b):
        self.f.write(b)

    def writele(self, i: int, length):
        self.f.write(i.to_bytes(length, "little"))

    def write_string(self, s: str, length):
        self.f.write(s.encode("UTF-8"), )

    def set_buffer(self, size=0):
        self.f = BytesIO(bytearray(size))

    def pop_buffer(self):
        self.f.seek(0)
        data = self.f.read()
        self.f = None
        return data
