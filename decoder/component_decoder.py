import numpy as np
from PIL import Image

from constants import COMPONENT_DETAILS_OFFSETS, IMAGE_COMPONENT_OFFSETS, WIDGET_CONFIGURATION_OFFSETS, Format, \
    COLOR_PROFILES, INVERSE_COORDINATES_TABLE
from decoder.base_decoder import Decoder
from component import Component
from image import ImageDecoder
from decoder.offsets_decoder import ComponentOffset
from widget_type import WidgetType


class ComponentDecoder(Decoder):
    def __init__(self, file, offsets=ComponentOffset(), component_type=Component.WIDGET):
        super().__init__(file)

        self.offsets_info = offsets
        self.component = Component(component_type)

        self.parse_file(component_type)

    def parse_file(self, component_type):
        component = self.component

        for otype, offset_info in self.offsets_info:
            if otype == 0x0:
                self.seek(offset_info.value)
                self.pin_offset()

                component.x = COMPONENT_DETAILS_OFFSETS["x"].extract(self)
                component.y = COMPONENT_DETAILS_OFFSETS["y"].extract(self)

            elif otype == 0x2:
                self.offset = 0
                self.seek(offset_info.value)
                self.pin_offset()
                self.parse_image(ComponentDecoder.STATIC)

            elif otype == 0x3:
                self.offset = 0
                self.seek(offset_info.value)
                self.pin_offset()
                self.parse_image(ComponentDecoder.DYNAMIC)

            elif otype == 0x7:
                self.unpin_offset()
                self.seek(offset_info.value)
                self.pin_offset()
                wtype = WIDGET_CONFIGURATION_OFFSETS["widget_type"].extract(self)
                category = WIDGET_CONFIGURATION_OFFSETS["category"].extract(self)
                wformat = WIDGET_CONFIGURATION_OFFSETS["widget_format"].extract(self)
                coordinate_types = WIDGET_CONFIGURATION_OFFSETS["coordinate_types"].extract(self)

                if coordinate_types == INVERSE_COORDINATES_TABLE["RSS"]: # clock
                    assert offset_info.size >= 0x20
                    component.max_value = WIDGET_CONFIGURATION_OFFSETS["max_value"].extract(self)
                    component.pivot_x = WIDGET_CONFIGURATION_OFFSETS["pivot_x"].extract(self)
                    component.pivot_y = WIDGET_CONFIGURATION_OFFSETS["pivot_y"].extract(self)
                    component.max_degrees = WIDGET_CONFIGURATION_OFFSETS["max_degrees"].extract(self)

                if coordinate_types == INVERSE_COORDINATES_TABLE["RMSS"]: # rotational masked
                    # TODO support for multiple static images
                    # raise RuntimeError("Unsupported coordinates type: RMSS")
                    component.mask_new_value = WIDGET_CONFIGURATION_OFFSETS["mask_max_value"].extract(self)
                    component.mask_pivot_x = WIDGET_CONFIGURATION_OFFSETS["mask_pivot_x"].extract(self)
                    component.mask_pivot_y = WIDGET_CONFIGURATION_OFFSETS["mask_pivot_y"].extract(self)
                    component.mask_max_degrees = WIDGET_CONFIGURATION_OFFSETS["mask_max_degrees"].extract(self)
                    component.mask_unk_1 = WIDGET_CONFIGURATION_OFFSETS["mask_unk_1"].extract(self)
                    component.mask_unk_2 = WIDGET_CONFIGURATION_OFFSETS["mask_unk_2"].extract(self)

                has_values_ranges = WIDGET_CONFIGURATION_OFFSETS["has_values_ranges"].extract(self)
                if has_values_ranges == 0x2:
                    assert wformat == Format.FORMAT_IMAGE.value
                    WIDGET_CONFIGURATION_OFFSETS["values_ranges_start"].goto(self)
                    doffset = WIDGET_CONFIGURATION_OFFSETS["values_ranges_start"].value
                    for i in range(0, offset_info.size - doffset, 0x4):
                        r = self.read_ile(0x4)
                        component.values_ranges.append(r)

                component.widget_type = WidgetType(wtype, category, wformat, coordinate_types)

    DYNAMIC = 0
    STATIC = 1

    def parse_image(self, image_type):
        component = self.component

        color_profile = IMAGE_COMPONENT_OFFSETS["color_profile"].extract(self)
        component.frames_count = IMAGE_COMPONENT_OFFSETS["frames_count"].extract(self)
        if image_type == self.DYNAMIC:
            component.width = IMAGE_COMPONENT_OFFSETS["width"].extract(self)
            component.height = IMAGE_COMPONENT_OFFSETS["height"].extract(self)
        else:
            component.swidth = IMAGE_COMPONENT_OFFSETS["width"].extract(self)
            component.sheight = IMAGE_COMPONENT_OFFSETS["height"].extract(self)
        self.seek(0x8)
        component.unknowns.append(self.read_ile(4))
        offset = IMAGE_COMPONENT_OFFSETS["pixel_array"].value

        if image_type == self.STATIC:
            image = self.extract_image(offset, component.swidth, component.sheight, color_profile)
            if component.static_image is None:
                component.static_image = image
            else: # for now two static images always mean the second is a mask
                component.masked_image = image

        else:
            for i in range(component.frames_count):
                image = self.extract_image(offset, component.width, component.height, color_profile)
                component.images.append(image)
                offset += int((component.height * 3 / 2) * component.width * 2)

    def extract_image(self, offset,  w, h, color_profile):
        self.seek(offset)
        endianness = COLOR_PROFILES[color_profile]
        base_image = ImageDecoder(endianness=endianness).decode(self.f, w, h)
        offset += h * w * 2
        self.seek(offset)
        mask = ImageDecoder(mode="L", dtype="u1").decode(self.f, w, h)

        image = ImageDecoder().merge(base_image, mask)
        return image

    def get(self):
        return self.component
