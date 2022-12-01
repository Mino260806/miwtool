from dataclasses import dataclass

from encoder.component_encoder import ComponentEncoder
from image import ImageEncoder, ImageDecoder


@dataclass
class Config:
    color_endianness: str

    def propagate(self):
        ComponentEncoder.color_endianness = self.color_endianness
        ImageEncoder.color_endianness = self.color_endianness
