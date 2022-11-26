from pathlib import Path

from PIL import Image

from image import ImageDecoder
from widget_type import WidgetType


class Component:
    WIDGET = 0
    PREVIEW = 1

    def __init__(self, component_type):
        self.comp_type = component_type

        self.unknowns = []
        self.images = []
        self.static_image = None
        self.x = None
        self.y = None
        self.width = None
        self.swidth = None
        self.sheight = None
        self.height = None
        self.values_ranges = []
        self.frames_count = None
        self.widget_type = None

        # Only in rotating widgets (ex clock)
        self.max_degrees = None
        self.pivot_y = None
        self.pivot_x = None
        self.max_value = None

    def show(self):
        images = []
        if self.images:
            images.extend(self.images)
        if self.static_image:
            images.append(self.static_image)
        if images:
            ImageDecoder.pil_grid(images).show(title=str((self.x, self.y)))

    def dump(self, path, suffix):
        rel_path = Path(f"images_{suffix}")
        path = Path(path) / rel_path
        paths_list = []
        if self.images or self.static_image:
            path.mkdir()
        for j, image in enumerate(self.images):
            img_path = path / f"image_{j}.png"
            image.save(img_path)
            paths_list.append(str(rel_path / f"image_{j}.png"))
        if self.static_image:
            self.static_image.save(path / "static.png")

        dump = {}
        if self.comp_type == Component.WIDGET:
            dump["x"] = self.x
            dump["y"] = self.y

        if self.widget_type is not None:
            dump["type"] = self.widget_type.dump()

        if self.max_degrees:
            dump["max_degrees"] = self.max_degrees
        if self.max_value:
            dump["max_value"] = self.max_value
        if self.pivot_x:
            dump["pivot_x"] = self.pivot_x
        if self.pivot_y:
            dump["pivot_y"] = self.pivot_y

        if self.values_ranges:
            dump["values_ranges"] = self.values_ranges

        if paths_list:
            dump["dynamic"] = paths_list
        if self.static_image:
            dump["static"] = str(rel_path / "static.png")
        return dump

    def load_from_dump(self, path, dump):
        self.x = dump.get("x")
        self.y = dump.get("y")
        self.max_degrees = dump.get("max_degrees")
        self.max_value = dump.get("max_value")
        self.pivot_x = dump.get("pivot_x")
        self.pivot_y = dump.get("pivot_y")
        self.values_ranges = dump.get("values_ranges") or []

        widget_type_dump = dump.get("type")
        if widget_type_dump:
            self.widget_type = WidgetType.load_from_dump(widget_type_dump)

        static_path = dump.get("static")
        if static_path:
            self.static_image = Image.open(path / static_path).convert("RGBA")
            self.swidth = self.static_image.size[0]
            self.sheight = self.static_image.size[1]

        dynamic_paths = dump.get("dynamic")
        if dynamic_paths:
            self.frames_count = len(dynamic_paths)
            for dynamic_path in dynamic_paths:
                image = Image.open(path / dynamic_path).convert("RGBA")
                self.images.append(image)
                if self.width is None:
                    self.width = image.size[0]
                if self.height is None:
                    self.height = image.size[1]
        else:
            self.frames_count = 0

    def resolve(self):
        if self.frames_count is None:
            self.frames_count = len(self.images) if self.images else 0
        if self.images and (self.width is None or self.height is None):
            self.width = self.images[0].size[0]
            self.height = self.images[0].size[1]
        if self.static_image and (self.swidth is None or self.sheight is None):
            self.swidth = self.static_image.size[0]
            self.sheight = self.static_image.size[1]
