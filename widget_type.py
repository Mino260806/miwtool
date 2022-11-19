from enum import Enum
from constants import WIDGET_TYPES, INVERSE_WIDGET_TYPES


class WidgetType:
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

    class CoordinateRelative:
        def __init__(self, cid, relx, rely, is_number=True, is_clock=False, zero_padding=False):
            self.cid = cid
            self.relx = relx
            self.rely = rely
            self.zero_padding = zero_padding
            self.is_number = is_number
            self.is_clock = is_clock

        def __eq__(self, other):
            if isinstance(other, str):
                return self.cid == other
            if isinstance(other, self.__class__):
                return self.relx == other.relx and \
                       self.rely == other.rely and \
                       self.zero_padding == other.zero_padding and \
                       self.is_number == other.is_number and \
                       self.is_clock == other.is_clock
            return super().__eq__(other)

        def __str__(self):
            return f"CoordinateRelative({self.relx.name}, {self.rely.name}, " \
                   f"zero_padding={self.zero_padding}, is_number={self.is_number}, is_clock={self.is_clock})"

        def __hash__(self):
            return hash(self.cid)

    COORDINATES_TABLE = {
        0x10: CoordinateRelative("NES", CoordType.END, CoordType.START),
        0x11: CoordinateRelative("NSS", CoordType.START, CoordType.START),
        0x12: CoordinateRelative("NCS", CoordType.CENTER, CoordType.START),

        0x15: CoordinateRelative("NSS0", CoordType.START, CoordType.START, zero_padding=True),
        0x16: CoordinateRelative("NCS0", CoordType.CENTER, CoordType.START, zero_padding=True), # TODO unsure

        0x20: CoordinateRelative("SS", CoordType.START, CoordType.START, is_number=False),

        0x30: CoordinateRelative("RSS", CoordType.START, CoordType.START, is_number=True, is_clock=True),
    }
    INVERSE_COORDINATES_TABLE = {}

    def __init__(self, wtype, category, wformat, coordinate_types):
        self.wtype = wtype
        self.category = category
        self.wformat = WidgetType.Format(wformat)
        self.coordinate_types = WidgetType.COORDINATES_TABLE.get(coordinate_types)

    def __str__(self):
        category = self.get_category_string()
        type_string = self.get_type_string()
        return f"<{category} {type_string}>"

    def get_category_string(self):
        category = WIDGET_TYPES.get(self.category)
        if category is None:
            return hex(self.category)
        return category.category_name

    def get_type_string(self):
        category = WIDGET_TYPES.get(self.category)
        if category is None:
            return hex(self.wtype)
        type_string = category[self.wtype]
        if type_string is None:
            return hex(self.wtype)
        return type_string

    def dump(self):
        return {
            "category": self.get_category_string(),
            "type": self.get_type_string(),
            "format": self.wformat.name,
            "coordinate_types": self.coordinate_types.cid
        }

    def get_int_properties(self):
        return self.wtype, self.category, self.wformat.value, \
            self.INVERSE_COORDINATES_TABLE[self.coordinate_types.cid]

    @classmethod
    def load_from_dump(cls, dump):
        category_d = dump.get("category")
        wtype_d = dump.get("type")
        wformat_d = dump.get("format")
        coordinate_types_d = dump.get("coordinate_types")

        wtype = None
        category = None

        if category_d is not None:
            category = INVERSE_WIDGET_TYPES.get(category_d)
            if category is not None:
                wtype = WIDGET_TYPES.get(category).inverse_get(wtype_d)

        wformat = WidgetType.Format[wformat_d]
        coordinate_types = WidgetType.INVERSE_COORDINATES_TABLE.get(coordinate_types_d)

        return WidgetType(wtype, category, wformat, coordinate_types)


CTABLE = WidgetType.COORDINATES_TABLE
for value, coord_type in tuple(CTABLE.items()):
    WidgetType.INVERSE_COORDINATES_TABLE[coord_type.cid] = value
