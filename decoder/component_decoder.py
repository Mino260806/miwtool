import numpy as np
from PIL import Image

from constants import COMPONENT_DETAILS_OFFSETS, IMAGE_COMPONENT_OFFSETS, WIDGET_CONFIGURATION_OFFSETS
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

        if 0x0 in self.offsets_info:
            self.seek(self.offsets_info[0].value)
            self.pin_offset()

            component.x = COMPONENT_DETAILS_OFFSETS["x"].extract(self)
            component.y = COMPONENT_DETAILS_OFFSETS["y"].extract(self)

        if 0x2 in self.offsets_info:
            self.offset = 0
            self.seek(self.offsets_info[0x2].value)
            self.pin_offset()
            self.parse_image(static=True)

        if 0x3 in self.offsets_info:
            self.offset = 0
            self.seek(self.offsets_info[0x3].value)
            self.pin_offset()
            self.parse_image(static=False)

        if 0x7 in self.offsets_info:
            self.unpin_offset()
            self.seek(self.offsets_info[0x7].value)
            self.pin_offset()
            wtype = WIDGET_CONFIGURATION_OFFSETS["widget_type"].extract(self)
            category = WIDGET_CONFIGURATION_OFFSETS["category"].extract(self)
            wformat = WIDGET_CONFIGURATION_OFFSETS["widget_format"].extract(self)
            coordinate_types = WIDGET_CONFIGURATION_OFFSETS["coordinate_types"].extract(self)
            if coordinate_types == 0x30: # clock
                assert self.offsets_info[0x7].size >= 0x20
                component.max_value = WIDGET_CONFIGURATION_OFFSETS["max_value"].extract(self)
                component.pivot_x = WIDGET_CONFIGURATION_OFFSETS["pivot_x"].extract(self)
                component.pivot_y = WIDGET_CONFIGURATION_OFFSETS["pivot_y"].extract(self)
                component.max_degrees = WIDGET_CONFIGURATION_OFFSETS["max_degrees"].extract(self)
            has_values_ranges = WIDGET_CONFIGURATION_OFFSETS["has_values_ranges"].extract(self)
            if has_values_ranges == 0x2:
                assert wformat == WidgetType.Format.FORMAT_IMAGE.value
                WIDGET_CONFIGURATION_OFFSETS["values_ranges_start"].goto(self)
                doffset = WIDGET_CONFIGURATION_OFFSETS["values_ranges_start"].value
                for i in range(0, self.offsets_info[0x7].size - doffset, 0x4):
                    r = self.read_ile(0x4)
                    component.values_ranges.append(r)

            component.widget_type = WidgetType(wtype, category, wformat, coordinate_types)

    def parse_image(self, static=True):
        component = self.component

        component.frames_count = IMAGE_COMPONENT_OFFSETS["frames_count"].extract(self)
        if not static:
            component.width = IMAGE_COMPONENT_OFFSETS["width"].extract(self)
            component.height = IMAGE_COMPONENT_OFFSETS["height"].extract(self)
        else:
            component.swidth = IMAGE_COMPONENT_OFFSETS["width"].extract(self)
            component.sheight = IMAGE_COMPONENT_OFFSETS["height"].extract(self)
        self.seek(0x8)
        component.unknowns.append(self.read_ile(4))
        offset = IMAGE_COMPONENT_OFFSETS["pixel_array"].value

        if static:
            image = self.extract_image(offset, component.swidth, component.sheight)
            component.static_image = image

        else:
            for i in range(component.frames_count):
                image = self.extract_image(offset, component.width, component.height)
                component.images.append(image)
                offset += int((component.height * 3 / 2) * component.width * 2)

    def extract_image(self, offset,  w, h):
        self.seek(offset)
        base_image = ImageDecoder().decode(self.f, w, h)
        # component.images.append(base_image)
        # offset += int((component.height * 3 / 2) * component.width * 2)

        # component.images.append(ImageDecoder().decode(self.f, w, component.height))
        offset += h * w * 2
        self.seek(offset)
        mask = ImageDecoder("L").decode(self.f, w, h, dtype=np.byte)
        # masks = np.asarray(masks_raw)
        # mask1_raw = Image.fromarray(masks[:, :floor(w / 2)])
        # mask2_raw = Image.fromarray(masks[:floor(h / 2), ceil(w / 2):])
        # mask1 = mask1_raw \
        #     .resize((w, h), Image.NORMAL) \
        #     .convert("L")
        # mask2 = mask2_raw \
        #     .resize((w, h), Image.NORMAL) \
        #     .convert("L")
        # # mask1.show()
        # # exit()
        # mask1_raw_new = np.asarray(mask1)
        # mask2_raw_new = np.asarray(mask2)
        # masks_combined_raw = mask1_raw_new // 2 + mask2_raw_new // 2
        # masks_combined = Image.fromarray(masks_combined_raw)
        # masks_combined = Image.new(mode="L", size=(w, component.height))
        # masks_combined.paste(mask1, mask=mask_mask)
        # masks_combined.paste(mask2, mask=mask_mask)
        # exit()

        # mask1.resize((w * 8, component.height * 8)).show()
        # mask2.resize((w * 8, component.height * 8)).show()
        # masks_combined.resize((w * 8, component.height * 8)).show()
        # print(masks_combined.getpixel((5,5)))
        # exit()

        background = Image.new("RGBA", (w, h), color=(0, 0, 0, 0))
        image = Image.composite(base_image, background, mask)

        # if self.unknowns[0] == 1:
        #     pass
        #     # image.show()
        #     # base_image.save("base.png")
        #     # masks_raw.save("masks.png")
        #     # masks_raw.convert("L").save("masks_gray.png")
        #     # mask1_raw.save("mask1.png")
        #     # image.save("result.png")
        #     # exit()
        return image

    def get(self):
        return self.component
