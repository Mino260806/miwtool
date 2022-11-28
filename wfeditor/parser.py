import json
from pathlib import Path
from random import randint
from PIL import Image

from component import Component
from decoder.watch_face import WatchFace
from widget_type import WidgetType

PARENT_FOLDER = Path(__file__).parent.resolve()


def index_images(folder):
    indexes = {}
    for image in Path(folder).iterdir():
        if image.suffix == ".png" and image.stem.isnumeric():
            indexes[int(image.stem)] = str(image)
    return indexes


class WFEditorParser:
    default_images_indexes = index_images(PARENT_FOLDER / "defaultimages")
    misc_images_indexes = {}

    def __init__(self, src):
        self.images_indexes = index_images(src)
        self.watchface = None
        self.folder = Path(src)

        with open(self.folder / "watchface.json", "r") as f:
            self.data = json.loads(f.read())

        self.parse()

    def parse(self):
        t = WidgetType.from_string_attrs

        self.watchface = WatchFace()
        preview_data = self.data.get("Preview")
        self.add_component(preview_data, is_preview=True)

        background = self.data.get("Background")
        if background is not None:
            self.add_component(background["Image"])

        metadata = self.data.get("MetaData")
        if metadata is not None:
            name = self._get(metadata, "Name", str)
            face_id = self._get(metadata, "Id", str)

            self.watchface.name = name
            self.watchface.face_id = face_id

        self.watchface.name = "Unnamed" if self.watchface.name is None else self.watchface.name
        self.watchface.face_id = str(randint(1, 65130061)) if self.watchface.face_id is None else self.watchface.face_id

        time_data = self.data.get("Time")
        if time_data is not None:
            hours = time_data.get("Hours")
            minutes = time_data.get("Minutes")
            seconds = time_data.get("Seconds")

            self.add_component(hours, t("HOUR", "TIME", "FORMAT_DECIMAL_2_DIGITS", "NSS0"))
            self.add_component(minutes, t("MINUTE", "TIME", "FORMAT_DECIMAL_2_DIGITS", "NSS0"))
            self.add_component(seconds, t("SECOND", "TIME", "FORMAT_DECIMAL_2_DIGITS", "NSS0"))

        date_data = self.data.get("Date")
        if date_data is not None:
            weekday = date_data.get("WeekDay")
            self.add_component(weekday, t("DAY_OF_WEEK", "DAY", "FORMAT_IMAGE", "SS"))

            monthandday_data = date_data.get("MonthAndDay")
            if monthandday_data is not None:
                if "OneLine" in monthandday_data:
                    raise RuntimeError("OneLine MonthAndDay is not supported!")
                separate_data = monthandday_data.get("Separate")
                if separate_data is not None:
                    day = separate_data.get("Day")
                    month = separate_data.get("Month")

                    self.add_component(day, t("DAY_OF_MONTH", "DAY", "FORMAT_DECIMAL_2_DIGITS", "NSS0"))
                    self.add_component(month, t("MONTH", "DAY", "FORMAT_DECIMAL_2_DIGITS", "NSS0"))

        activity_data = self.data.get("Activity")
        if activity_data is not None:
            steps = activity_data.get("Steps")
            pulse = activity_data.get("Pulse")
            calories = activity_data.get("Calories")

            self.add_component(steps, t("NORMAL", "STEPS", "FORMAT_DECIMAL_5_DIGITS", "NSS"))
            self.add_component(pulse, t("NORMAL", "HEART_RATE", "FORMAT_DECIMAL_3_DIGITS", "NSS"))
            self.add_component(calories, t("NORMAL", "CALORIES", "FORMAT_DECIMAL_5_DIGITS", "NSS"))

        battery_data = self.data.get("Battery")
        if battery_data is not None:
            battery = battery_data.get("Text")

            self.add_component(battery, t("NORMAL", "BATTERY", "FORMAT_DECIMAL_3_DIGITS", "NSS"))

        weather_data = self.data.get("Weather")
        if weather_data is not None:
            weathericon_data = weather_data.get("Icon")
            if weathericon_data is not None:
                customicon = weathericon_data.get("CustomIcon")
                if customicon is not None:
                    self.ensure(customicon["ImagesCount"] == 19, "Weather images count must exactly equal 19")
                    self.add_component(customicon, t("TYPE", "WEATHER", "FORMAT_IMAGE", "SS"),
                                       values_ranges=[0,1,2,3,4,5,6,8,10,13,15,16,17,18,20,33,53,99,301])

                coordinates = weathericon_data.get("Coordinates")
                if coordinates is not None:
                    self.index_misc()
                    coordinates["ImageIndex"] = 100000
                    coordinates["ImagesCount"] = 19
                    self.add_component(coordinates, t("TYPE", "WEATHER", "FORMAT_IMAGE", "SS"),
                                       values_ranges=[0, 1, 2, 3, 4, 5, 6, 8, 10, 13, 15, 16, 17, 18, 20, 33, 53, 99, 301])

            temperature_data = weather_data.get("Temperature")
            if temperature_data is not None:
                current_temperature_data = temperature_data.get("Current")
                if current_temperature_data is not None:
                    number = current_temperature_data.get("Number")
                    component = self.add_component(number, t("TEMPERATURE", "WEATHER", "FORMAT_DECIMAL_2_DIGITS", "NSS"))

                    minusSignImageIndex = current_temperature_data.get("MinusSignImageIndex")
                    degreesImageIndex = current_temperature_data.get("DegreesImageIndex")

                    component.images.append(self.load_image(minusSignImageIndex))
                    component.static_image = self.load_image(degreesImageIndex)
                    component.resolve()

    def add_component(self, component_data, widget_type=None, is_preview=False, **attrs):
        if component_data is not None:
            component = self.parse_component(component_data, widget_type)
            for attr, value in attrs.items():
                component.__setattr__(attr, value)
            if not is_preview:
                self.watchface.components.append(component)
            else:
                component.comp_type = Component.PREVIEW
                self.watchface.preview = component
            return component

    def parse_component(self, component_image, widget_type=None):
        if "Tens" in component_image:
            return self.parse_component(component_image["Tens"], widget_type)

        component = Component(Component.WIDGET)
        component.widget_type = widget_type
        image_index = int(component_image["ImageIndex"])
        if widget_type is None:
            component.static_image = self.load_image(image_index)
        else:
            images_count = int(component_image["ImagesCount"])
            component.images = []
            for i in range(images_count):
                component.images.append(self.load_image(image_index + i))

        alignment = self._get(component_image, "Alignment", str)
        if alignment is not None and alignment != "TopLeft":
            raise RuntimeError("only TopLeft alignment is supported")
        x = self._get(component_image, "X", int)
        if x is None: x = self._get(component_image, "TopLeftX", int)
        y = self._get(component_image, "Y", int)
        if y is None: y = self._get(component_image, "TopLeftY", int)
        component.x = x
        component.y = y
        spacing = self._get(component_image, "Spacing", int) or 0
        component.spacing = spacing
        component.resolve()

        return component

    def load_image(self, index):
        if index in self.images_indexes:
            return Image.open(self.folder / self.images_indexes[index])
        elif index in self.default_images_indexes:
            return Image.open(PARENT_FOLDER / "defaultimages" / self.default_images_indexes[index])
        elif index in self.misc_images_indexes:
            return Image.open(PARENT_FOLDER / "../assets" / self.misc_images_indexes[index])

    def ensure(self, boolean, message):
        if not boolean:
            raise RuntimeError(message)
        
    def _get(self, data, key, valuetype):
        value = data.get(key)
        if value is not None:
            self.ensure(isinstance(value, valuetype), f"\"{key}\" must be a {valuetype}")
        return value

    def index_misc(self):
        if not self.misc_images_indexes:
            index = index_images(PARENT_FOLDER / "../assets")
            self.misc_images_indexes.update(index)
