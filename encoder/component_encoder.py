from constants import COMPONENT_DETAILS_OFFSETS, WIDGET_CONFIGURATION_OFFSETS, IMAGE_COMPONENT_OFFSETS
from structure import Format
from encoder.base_encoder import Encoder
from image import ImageEncoder


class ComponentEncoder(Encoder):
    color_endianness = "big"

    def __init__(self, component, is_preview=False):
        super().__init__()

        self.is_preview = is_preview
        self.component = component
        self.encoded_data = []
        self.properties_counter = None
        self.properties_indexes = None

        self._next_property_type = None

    def encode(self, properties_counter=None):
        if properties_counter is None:
            properties_counter = {0x0: 0, 0x2: 0, 0x3: 0, 0x7: 0}

        self.properties_counter = properties_counter
        self.properties_indexes = properties_counter.copy()

        if self.component.masked_image is not None:
            assert self.component.static_image is not None
            self.add_property(0x2, self.encoded_property_2(is_mask=True))
            self.add_property(0x2, self.encoded_property_2(is_mask=False))
            self.add_property(0x7, self.encoded_property_7())

        elif self.component.static_image is not None:
            self.add_property(0x2, self.encoded_property_2(is_mask=False))
            if self.component.pivot_x is not None:
                self.add_property(0x7, self.encoded_property_7())

        if self.component.images:
            self.add_property(0x3, self.encoded_property_3())
            assert self.component.widget_type is not None
            self.add_property(0x7, self.encoded_property_7())

        if not self.is_preview:
            self.add_property(0x0, self.encoded_property_0())
            # print(" ".join(hex(b) for b in self.encoded_data[0]))
            properties_counter[0] += 1

    def has_property(self, property_type):
        return property_type in self.encoded_data

    def sort_properties(self):
        def custom_key(p):
            if p[0] == 0x2:
                return 0x3
            elif p[0] == 0x3:
                return 0x2
            return p[0]
        self.encoded_data.sort(key=custom_key)
        # if 0x2 in result and 0x3 in result:
        #     i2, i3 = result.index(0x2), result.index(0x3)
        #     result[i2], result[i3] = result[i3], result[i2]

    # def get_bytes(self, property_type):
    #     return self.encoded_data[property_type]

    def iter_properties(self):
        self.sort_properties()
        return self.encoded_data.__iter__()

    def add_property(self, property_type, property_data):
        self.encoded_data.append((property_type, self.properties_counter[property_type], property_data))

    def encoded_property_0(self):
        self.set_buffer(0x10)

        property_index = self.bump_property()

        COMPONENT_DETAILS_OFFSETS["property_index"].encode(self, property_index)
        COMPONENT_DETAILS_OFFSETS["next_property_type"].encode(self, self._next_property_type)
        COMPONENT_DETAILS_OFFSETS["x"].encode(self, self.component.x)
        COMPONENT_DETAILS_OFFSETS["y"].encode(self, self.component.y)

        self._next_property_type = 0

        return self.pop_buffer()

    def encoded_property_7(self):
        property_index = self.bump_property()

        wtype, category, wformat, ctype = self.component.widget_type.get_int_properties()
        if wformat == Format.FORMAT_IMAGE.value:
            if self.component.pivot_x:
                self.set_buffer(0x20)
            else:
                self.set_buffer(0x10)
        else:
            self.set_buffer(0x14)

        WIDGET_CONFIGURATION_OFFSETS["widget_type"].encode(self, wtype)
        WIDGET_CONFIGURATION_OFFSETS["category"].encode(self, category)
        WIDGET_CONFIGURATION_OFFSETS["widget_format"].encode(self, wformat)
        WIDGET_CONFIGURATION_OFFSETS["ctype"].encode(self, ctype)
        WIDGET_CONFIGURATION_OFFSETS["property_index"].encode(self, property_index)
        WIDGET_CONFIGURATION_OFFSETS["next_property_type"].encode(self, self._next_property_type)

        if self._next_property_type == 0x3 and \
                self.component.static_image is not None:
            WIDGET_CONFIGURATION_OFFSETS["second_property_index"].encode(self, self.properties_counter[0x2] - 1)
            WIDGET_CONFIGURATION_OFFSETS["second_property_type"].encode(self, 0x2)

        if self.component.values_ranges:
            WIDGET_CONFIGURATION_OFFSETS["has_values_ranges"].encode(self, 0x2)
            WIDGET_CONFIGURATION_OFFSETS["values_ranges_start"].goto(self)
            for value in self.component.values_ranges:
                self.writele(value, 4)

        if self.component.pivot_x:
            WIDGET_CONFIGURATION_OFFSETS["pivot_x"].encode(self, self.component.pivot_x)
            WIDGET_CONFIGURATION_OFFSETS["pivot_y"].encode(self, self.component.pivot_y)
            WIDGET_CONFIGURATION_OFFSETS["max_value"].encode(self, self.component.max_value)
            WIDGET_CONFIGURATION_OFFSETS["max_degrees"].encode(self, self.component.max_degrees)

        if self._next_property_type == 0x2 and \
                self.component.masked_image is not None:
            WIDGET_CONFIGURATION_OFFSETS["property_index"].encode(self, self.properties_counter[0x2] - 2)
            WIDGET_CONFIGURATION_OFFSETS["next_property_type"].encode(self, 0x2)
            WIDGET_CONFIGURATION_OFFSETS["masked_image_property_index"].encode(self, self.properties_counter[0x2] - 1)
            WIDGET_CONFIGURATION_OFFSETS["masked_image_property_type"].encode(self, 0x2)

        if self.component.mask_max_value:
            WIDGET_CONFIGURATION_OFFSETS["mask_max_value"].encode(self, self.component.mask_max_value)
            WIDGET_CONFIGURATION_OFFSETS["mask_pivot_x"].encode(self, self.component.mask_pivot_x)
            WIDGET_CONFIGURATION_OFFSETS["mask_pivot_y"].encode(self, self.component.mask_pivot_y)
            WIDGET_CONFIGURATION_OFFSETS["mask_max_degrees"].encode(self, self.component.mask_max_degrees)
            WIDGET_CONFIGURATION_OFFSETS["mask_unk_1"].encode(self, self.component.mask_unk_1)
            WIDGET_CONFIGURATION_OFFSETS["mask_unk_2"].encode(self, self.component.mask_unk_2)

        self._next_property_type = 7

        return self.pop_buffer()

    def encoded_property_3(self):
        self.set_buffer()

        property_index = self.bump_property()

        IMAGE_COMPONENT_OFFSETS["color_profile"].encode(self, self.get_color_profile())
        IMAGE_COMPONENT_OFFSETS["width"].encode(self, self.component.width)
        IMAGE_COMPONENT_OFFSETS["height"].encode(self, self.component.height)
        IMAGE_COMPONENT_OFFSETS["frames_count"].encode(self, self.component.frames_count)
        IMAGE_COMPONENT_OFFSETS["mystery_number"].encode(self, self.component.width * self.component.height *
                                                         max(1, self.component.frames_count) * 3)
        IMAGE_COMPONENT_OFFSETS["pixel_array"].goto(self)
        for image in self.component.images:
            self.encode_image(image)
        # print(hex(self.f.getbuffer().nbytes))

        self._next_property_type = 3

        return self.pop_buffer()

    def encoded_property_2(self, is_mask):
        self.set_buffer()

        property_index = self.bump_property()

        IMAGE_COMPONENT_OFFSETS["color_profile"].encode(self, self.get_color_profile())
        IMAGE_COMPONENT_OFFSETS["width"].encode(self, self.component.swidth)
        IMAGE_COMPONENT_OFFSETS["height"].encode(self, self.component.sheight)
        IMAGE_COMPONENT_OFFSETS["mystery_number"].encode(self, self.component.swidth * self.component.sheight * 3)
        IMAGE_COMPONENT_OFFSETS["pixel_array"].goto(self)
        if not is_mask:
            self.encode_image(self.component.static_image)
        else:
            self.encode_image(self.component.masked_image)
        # print(hex(self.f.getbuffer().nbytes))

        self._next_property_type = 2

        return self.pop_buffer()

    def encode_image(self, image):
        image_bytes, mask_bytes = ImageEncoder.encode_from_image(image, self.component.spacing)
        self.write(image_bytes)
        self.write(mask_bytes)

    def bump_property(self):
        if self._next_property_type is None:
            return 0
        property_index = self.properties_counter[self._next_property_type]
        self.properties_counter[self._next_property_type] += 1
        return property_index

    @classmethod
    def get_color_profile(cls):
        return {
            "little": 0x4,
            "big": 0x7
        }[cls.color_endianness]
