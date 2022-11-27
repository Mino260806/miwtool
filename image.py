import numpy as np
from color import Color
from PIL import Image


class ImageDecoder:
    def __init__(self, mode="RGBA"):
        self.mode = mode

    def decode(self, stream, width, height, dtype=">i2"):
        if self.mode == "RGBA":
            shape = (height, width, 4)
        else:
            shape = (height, width)

        nbytes = 2 if dtype == ">i2" else 1
        img_bytes = np.frombuffer(stream.read(width * height * nbytes), dtype=dtype)
        img_bytes = np.reshape(img_bytes, (height, width))
        img_rgb = np.full(shape, fill_value=0xff, dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                value = img_bytes[y, x]
                self.decode_color(img_rgb, value, x, y)
        image = Image.fromarray(img_rgb, self.mode)
        return image

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
        if self.mode == "RGBA":
            color = Color.fromRGB565(value).toRGB888()
            img_rgb[y, x, 0] = color.r
            img_rgb[y, x, 1] = color.g
            img_rgb[y, x, 2] = color.b
        elif self.mode == "L" or self.mode == "1":
            img_rgb[y, x] = value


class ImageEncoder:
    @staticmethod
    def encode_from_path(path):
        return ImageEncoder.encode_from_image(Image.open(path))

    @staticmethod
    def encode_from_image(image):
        image = image.convert(mode="RGBA")
        img_array = np.asarray(image)
        width = img_array.shape[1]
        height = img_array.shape[0]
        new_img_array = np.ndarray((height, width), dtype=">i2")
        mask_array = np.ndarray((height, width), dtype=np.byte)
        for y in range(height):
            for x in range(width):
                pixel = img_array[y, x]
                color = Color(pixel[0], pixel[1], pixel[2], Color.RGB888)
                doublebyte_color = color.toRGB565().value
                new_img_array[y, x] = doublebyte_color
                mask_array[y, x] = pixel[3]
        return new_img_array, mask_array
