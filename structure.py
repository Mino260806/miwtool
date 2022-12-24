from enum import Enum


class OffsetInfo:
    DTYPE_INT = 0
    DTYPE_STR = 1
    DTYPE_BYTES = 2

    def __init__(self, value, size=4, dtype=DTYPE_INT):
        self.value = value
        self.size = size
        self.dtype = dtype

    def extract(self, decoder, doffset=0):
        decoder.seek(self.value + doffset)
        if self.dtype == self.DTYPE_INT:
            return decoder.read_ile(self.size)
        if self.dtype == self.DTYPE_STR:
            return decoder.read_string()
        else:
            return decoder.read(self.size)

    def encode(self, encoder, value, doffset=0):
        encoder.seek(self.value + doffset)

        if self.dtype == self.DTYPE_INT:
            encoder.writele(value, self.size)
        elif self.dtype == self.DTYPE_STR:
            encoder.write_string(value, self.size)
        else:
            encoder.write(value)

    def goto(self, decoder):
        decoder.seek(self.value)


class WidgetCategory:
    def __init__(self, category_name, types):
        self.category_name = category_name
        self.types = types

    def __getitem__(self, item):
        return self.types.get(item)

    def get(self, item):
        return self.types.get(item)

    def inverse_get(self, item):
        return self.types.inverse.get(item)

    def __eq__(self, other):
        if isinstance(other, WidgetCategory):
            return self.category_name == other.category_name and \
                   self.types == other.types
        if isinstance(other, str):
            return self.category_name == other
        return super().__eq__(other)


class CoordinateRelative:
    def __init__(self, cid, relx, rely, is_number=True, is_clock=False, zero_padding=False, is_masked=False):
        self.cid = cid
        self.relx = relx
        self.rely = rely
        self.zero_padding = zero_padding
        self.is_number = is_number
        self.is_clock = is_clock
        self.is_masked = is_clock

    def __eq__(self, other):
        if isinstance(other, str):
            return self.cid == other
        if isinstance(other, self.__class__):
            return self.relx == other.relx and \
                   self.rely == other.rely and \
                   self.zero_padding == other.zero_padding and \
                   self.is_number == other.is_number and \
                   self.is_clock == other.is_clock and \
                   self.is_masked == other.is_masked
        return super().__eq__(other)

    def __str__(self):
        return f"CoordinateRelative({self.relx.name}, {self.rely.name}, " \
               f"zero_padding={self.zero_padding}, is_number={self.is_number}, " \
               f"is_clock={self.is_clock}, is_masked={self.is_masked})"

    def __hash__(self):
        return hash(self.cid)


class Format(Enum):
    FORMAT_IMAGE = 0x0
    FORMAT_DECIMAL_2_DIGITS = 0x2
    FORMAT_DECIMAL_3_DIGITS = 0x3
    FORMAT_DECIMAL_4_DIGITS = 0x4
    FORMAT_DECIMAL_5_DIGITS = 0x5


class CoordType(Enum):
    START = 0
    CENTER = 1
    END = 2
