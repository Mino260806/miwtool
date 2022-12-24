from structure import OffsetInfo, WidgetCategory, CoordinateRelative, CoordType
from util.dict import inverse_dict
from bidict import bidict

HEADER = b"\x5A\xA5\x34\x12"


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
    "ctype": OffsetInfo(0x3, size=0x1),
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

    "RMSS": {
        "masked_image_property_index": OffsetInfo(0xc, size=0x1),
        "masked_image_property_type": OffsetInfo(0xf, size=0x1),
        "mask_max_value": OffsetInfo(0x19, size=0x2),
        "mask_pivot_x": OffsetInfo(0x1c, size=0x2),
        "mask_pivot_y": OffsetInfo(0x1e, size=0x2),
        "mask_max_degrees": OffsetInfo(0x22, size=0x2),
        "mask_unk_1": OffsetInfo(0x24, size=0x2),
        "mask_unk_2": OffsetInfo(0x26, size=0x2)
    }
}


COLOR_PROFILES = {
    0x4: "little",
    0x7: "big"
}


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

INVERSE_WIDGET_TYPES = inverse_dict(WIDGET_TYPES, lambda category: category.category_name)

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

INVERSE_COORDINATES_TABLE = inverse_dict(COORDINATES_TABLE, lambda offset_info: offset_info.cid)
