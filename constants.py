from enum import Enum

from bidict import bidict

HEADER = b"\x5A\xA5\x34\x12"


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


HEADER_OFFSETS = {
    "header_constant": OffsetInfo(0x0, size=0x4, dtype=OffsetInfo.DTYPE_BYTES),
    "mysterious_metadata": OffsetInfo(0x10, size=0x10, dtype=OffsetInfo.DTYPE_BYTES),
    "preview_offset": OffsetInfo(0x20, size=0x4),
    "preview_offset2": OffsetInfo(0xAC, size=0x4),
    "face_id": OffsetInfo(0x28, size=0x40, dtype=OffsetInfo.DTYPE_STR),
    "name": OffsetInfo(0x68, size=0x40, dtype=OffsetInfo.DTYPE_STR),
    "components_details": OffsetInfo(0xB0, size=0x50, dtype=OffsetInfo.DTYPE_BYTES),
    "components_count": OffsetInfo(0xB0, size=4),
    "components_offsets_end": OffsetInfo(0xfc, size=4),
    "components_offsets": OffsetInfo(0x100, size=-1, dtype=OffsetInfo.DTYPE_BYTES)
}


OFFSETS_DETAILS_OFFSETS = {
    "component_index": OffsetInfo(0x0, size=0x3),
    "offset_type": OffsetInfo(0x3, size=0x1),
    "component_offset": OffsetInfo(0x8, size=0x4),
    "block_size": OffsetInfo(0xc, size=0x4),
}

COMPONENT_DETAILS_OFFSETS = {
    "property_index": OffsetInfo(0x0, size=1),
    "next_property_type": OffsetInfo(0x3, size=1),
    "x": OffsetInfo(0x4, size=0x2),
    "y": OffsetInfo(0x6, size=0x2),
}

IMAGE_COMPONENT_OFFSETS = {
    "color_profile": OffsetInfo(0x0, size=0x1),
    "frames_count": OffsetInfo(0x1, size=0x1),
    "width": OffsetInfo(0x4, size=0x2),
    "height": OffsetInfo(0x6, size=0x2),
    "mystery_number": OffsetInfo(0x8, size=0x4),
    "pixel_array": OffsetInfo(0xc, size=-1)
}

WIDGET_CONFIGURATION_OFFSETS = {
    "widget_type": OffsetInfo(0x0, size=0x1),
    "category": OffsetInfo(0x1, size=0x1),
    "widget_format": OffsetInfo(0x2, size=0x1),
    "coordinate_types": OffsetInfo(0x3, size=0x1),
    "property_index": OffsetInfo(0x8, size=0x1),
    "next_property_type": OffsetInfo(0xb, size=0x1),
    "has_values_ranges": OffsetInfo(0xd, size=0x1), # TODO see what this does
    "second_property_index": OffsetInfo(0x10, size=0x1),
    "second_property_type": OffsetInfo(0x13, size=0x1),

    "max_value": OffsetInfo(0x11, size=0x2),
    "pivot_x": OffsetInfo(0x14, size=0x2),
    "pivot_y": OffsetInfo(0x16, size=0x2),
    "max_degrees": OffsetInfo(0x1a, size=0x2), # 2pi -> 3600°
    # max_value -> max_degrees

    "values_ranges_start": OffsetInfo(0x10, size=-1),

    "masked_image_property_index": OffsetInfo(0xc, size=0x1),
    "masked_image_property_type": OffsetInfo(0xf, size=0x1),
    "mask_max_value": OffsetInfo(0x19, size=0x2),
    "mask_pivot_x": OffsetInfo(0x1c, size=0x2),
    "mask_pivot_y": OffsetInfo(0x1e, size=0x2),
    "mask_max_degrees": OffsetInfo(0x22, size=0x2),
    "mask_unk_1": OffsetInfo(0x24, size=0x2),
    "mask_unk_2": OffsetInfo(0x26, size=0x2),
}


COLOR_PROFILES = {
    0x4: "little",
    0x7: "big"
}


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


WIDGET_TYPES = {
    0x11: WidgetCategory("TIME", bidict({
        0x8: "HOUR",
        0x10: "MINUTE",
        0x18: "SECOND"
    })),
    0x12: WidgetCategory("DAY", bidict({
        0x20: "DAY_OF_WEEK",
        0x10: "MONTH",
        0x18: "DAY_OF_MONTH"
    })),
    0x41: WidgetCategory("BATTERY", bidict({
        0x8: "NORMAL",
        0x10: "PERCENTAGE" # TODO unsure
    })),
    0x21: WidgetCategory("STEPS", bidict({
        0x8: "NORMAL",
        0x10: "PERCENTAGE",
    })),
    0x22: WidgetCategory("HEART_RATE", bidict({
        0x8: "NORMAL"
    })),
    0x23: WidgetCategory("CALORIES", bidict({
        0x8: "NORMAL",
        0x10: "PERCENTAGE"
    })),
    0x31: WidgetCategory("WEATHER", bidict({
        0x20: "TEMPERATURE",
        0x30: "TYPE"  # rainy, cloudy, sunny, ...
    })),
}

INVERSE_WIDGET_TYPES = {}

for value, category in list(WIDGET_TYPES.items()):
    INVERSE_WIDGET_TYPES[category.category_name] = value



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


COORDINATES_TABLE = {
    0x10: CoordinateRelative("NES", CoordType.END, CoordType.START),
    0x11: CoordinateRelative("NSS", CoordType.START, CoordType.START),
    0x12: CoordinateRelative("NCS", CoordType.CENTER, CoordType.START),

    0x15: CoordinateRelative("NSS0", CoordType.START, CoordType.START, zero_padding=True),
    0x16: CoordinateRelative("NCS0", CoordType.CENTER, CoordType.START, zero_padding=True), # TODO unsure

    0x20: CoordinateRelative("SS", CoordType.START, CoordType.START, is_number=False),

    0x30: CoordinateRelative("RSS", CoordType.START, CoordType.START, is_number=True, is_clock=True),
    0x40: CoordinateRelative("RMSS", CoordType.START, CoordType.START, is_number=True, is_clock=True),
}

INVERSE_COORDINATES_TABLE = {}
for value, coord_type in tuple(COORDINATES_TABLE.items()):
    INVERSE_COORDINATES_TABLE[coord_type.cid] = value
