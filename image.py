from io import BytesIO

import numpy as np
from color import Color
from PIL import Image


class ImageDecoder:
    def __init__(self, mode="RGB", endianness="big", dtype=">u2"):
        self.mode = mode
        self.endianness = endianness
        self.dtype = dtype

    def decode(self, stream, width, height):
        if self.mode == "RGB":
            shape = (height, width, 3)
        elif self.mode == "L":
            shape = (height, width)
        else:
            raise RuntimeError("unsupported mode")

        nbytes = 2 if self.dtype.endswith("u2") else 1
        img_bytes = np.frombuffer(stream.read(width * height * nbytes), dtype=self.dtype)
        img_bytes = np.reshape(img_bytes, (height, width))
        img_array = np.full(shape, fill_value=0x00, dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                value = img_bytes[y, x]
                self.decode_color(img_array, value, x, y)
        return img_array

    # https://stackoverflow.com/a/46877433/10231266
    @staticmethod
    def pil_grid(images, max_horiz=np.iinfo(int).max):
        n_images = len(images)
        n_horiz = min(n_images, max_horiz)
        h_sizes, v_sizes = [0] * n_horiz, [0] * (n_images // n_horiz)
        for i, im in enumerate(images):
            h, v = i % n_horiz, i // n_horiz
            h_sizes[h] = max(h_sizes[h], im.size[0])
            v_sizes[v] = max(v_sizes[v], im.size[1])
        h_sizes, v_sizes = np.cumsum([0] + h_sizes), np.cumsum([0] + v_sizes)
        im_grid = Image.new('RGBA', (h_sizes[-1], v_sizes[-1]), color='black')
        for i, im in enumerate(images):
            im_grid.paste(im, (h_sizes[i % n_horiz], v_sizes[i // n_horiz]))
        return im_grid

    def decode_color(self, img_rgb, value, x, y):
        if self.mode == "RGB":
            color = Color.fromRGB565(value, self.endianness).toRGB888()
            img_rgb[y, x, 0] = color.r
            img_rgb[y, x, 1] = color.g
            img_rgb[y, x, 2] = color.b
        elif self.mode == "L" or self.mode == "1":
            img_rgb[y, x] = value

    def merge(self, img_rgb, img_alpha):
        width = img_rgb.shape[1]
        height = img_rgb.shape[0]
        img = np.ndarray((height, width, 4), dtype=">u1")
        img[:, :, :3] = img_rgb
        img[:, :, 3] = img_alpha
        return Image.fromarray(img, mode="RGBA")


class ImageEncoder:
    color_endianness = "big"

    @classmethod
    def encode_from_path(cls, path):
        return ImageEncoder.encode_from_image(Image.open(path).convert("RGBA"))

    @classmethod
    def encode_from_image(cls, image, spacing=0):
        img_array = np.asarray(image.convert("RGBA"))
        width = img_array.shape[1]
        height = img_array.shape[0]
        new_img_array = np.ndarray((height, width), dtype=">u2")
        mask_array = np.ndarray((height, width), dtype=np.byte)
        for y in range(height):
            for x in range(width):
                pixel = img_array[y, x]
                color = Color(pixel[0], pixel[1], pixel[2], Color.RGB888)
                doublebyte_color = color.toRGB565().value(cls.color_endianness)
                new_img_array[y, x] = doublebyte_color
                mask_array[y, x] = pixel[3]
        if spacing > 0:
            new_img_array = np.hstack((new_img_array, np.zeros((height, spacing)))).astype(">u2")
            mask_array = np.hstack((mask_array, np.zeros((height, spacing), dtype=np.byte)))
        elif spacing < 0:
            assert width > -spacing
            new_img_array = new_img_array[:, :width+spacing].copy(order="C")
            mask_array = mask_array[:, :width+spacing].copy(order="C")

        return new_img_array, mask_array
