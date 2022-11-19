from enum import Enum
from constants import WIDGET_TYPES, INVERSE_WIDGET_TYPES, Format, COORDINATES_TABLE, INVERSE_COORDINATES_TABLE


class WidgetType:
    def __init__(self, wtype, category, wformat, coordinate_types):
        self.wtype = wtype
        self.category = category
        self.wformat = Format(wformat)
        self.coordinate_types = COORDINATES_TABLE.get(coordinate_types)

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
            INVERSE_COORDINATES_TABLE[self.coordinate_types.cid]

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

        wformat = Format[wformat_d]
        coordinate_types = INVERSE_COORDINATES_TABLE.get(coordinate_types_d)

        return WidgetType(wtype, category, wformat, coordinate_types)


