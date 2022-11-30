from dataclasses import dataclass

from encoder.component_encoder import ComponentEncoder


@dataclass
class Config:
    color_endianness: str

    def propagate(self):
        ComponentEncoder.color_endianness = self.color_endianness
