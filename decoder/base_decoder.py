class Decoder:
    def __init__(self, file):
        self.f = file
        self.offset = 0x0

    def pin_offset(self):
        self.offset = self.f.tell()

    def unpin_offset(self):
        self.offset = 0x0

    def read_string(self):
        string = []
        while (c := self.f.read(1)) != b"\x00":
            string.append(c)

        bstring = b"".join(string)
        return bstring.decode("UTF-8")

    def seek(self, x):
        self.f.seek(self.offset + x)

    def read(self, count):
        return self.f.read(count)

    def read_ile(self, bytes_count):
        return self.ile(self.read(bytes_count))

    @staticmethod
    def ile(x): return int.from_bytes(x, "little")


