from dataclasses import dataclass

from encoder.component_encoder import ComponentEncoder
from image import ImageEncoder, ImageDecoder


@dataclass
class Config:
    color_endianness: str

    def __post_init__(self):
        if self.color_endianness == "l": self.color_endianness = "little"
        if self.color_endianness == "b": self.color_endianness = "big"

    def propagate(self):
        ComponentEncoder.color_endianness = self.color_endianness
        ImageEncoder.color_endianness = self.color_endianness
