from constants import WIDGET_TYPES, INVERSE_WIDGET_TYPES, COORDINATES_TABLE, INVERSE_COORDINATES_TABLE
from structure import Format


class WidgetType:
    def __init__(self, wtype, category, wformat, ctypes):
        self.wtype = wtype
        self.category = category
        self.wformat = Format(wformat)
        self.ctype = COORDINATES_TABLE.get(ctypes)
        if self.ctype is None:
            raise RuntimeError(f"Unknown coordinates type: {hex(ctypes)}")

    @classmethod
    def from_string_attrs(cls, wtype_d, category_d, wformat_d, ctype):
        wtype = None
        category = None

        if category_d is not None:
            category = INVERSE_WIDGET_TYPES.get(category_d)
            if category is not None:
                wtype = WIDGET_TYPES.get(category).inverse_get(wtype_d)

        wformat = Format[wformat_d]
        ctype = INVERSE_COORDINATES_TABLE.get(ctype)

        return WidgetType(wtype, category, wformat, ctype)

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
            "ctype": self.ctype.cid
        }

    def get_int_properties(self):
        return self.wtype, self.category, self.wformat.value, \
            INVERSE_COORDINATES_TABLE[self.ctype.cid]

    @classmethod
    def load_from_dump(cls, dump):
        category_d = dump.get("category")
        wtype_d = dump.get("type")
        wformat_d = dump.get("format")
        ctype_d = dump.get("ctype")

        return cls.from_string_attrs(wtype_d, category_d, wformat_d, ctype_d)

