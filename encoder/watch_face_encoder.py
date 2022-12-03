from constants import HEADER, HEADER_OFFSETS
from decoder.watch_face import WatchFace
from encoder.base_encoder import Encoder
from encoder.component_encoder import ComponentEncoder
from encoder.offsets_encoder import OffsetsEncoder


class WatchFaceEncoder(Encoder):
    def __init__(self, watch_face: WatchFace):
        super().__init__()

        self.watch_face = watch_face

        self.component_encoders = []
        self.preview_encoder = None
        self.offsets_encoder = None

    def encode(self, filename):
        wf = self.watch_face

        self.set_buffer()

        HEADER_OFFSETS["header_constant"].encode(self, HEADER)
        HEADER_OFFSETS["face_id"].encode(self, wf.face_id)
        HEADER_OFFSETS["name"].encode(self, wf.name)
        HEADER_OFFSETS["mysterious_metadata"].encode(self,
             b"\x01\x07\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00")

        self.encode_preview()
        counter = self.encode_components()
        self.offsets_encoder = OffsetsEncoder(counter)

        HEADER_OFFSETS["components_details"].encode(self, self.offsets_encoder.get_bytes_description())

        data_offset = HEADER_OFFSETS["components_offsets"].value + self.offsets_encoder.nbytes
        self.seek(data_offset)

        for component_encoder in self.component_encoders:
            for property_type, property_index, property_data in component_encoder.iter_properties():
                self.offsets_encoder.add_offset(
                    property_type, property_index,
                    self.f.tell(), len(property_data)
                )
                self.write(property_data)
        preview_offset = self.whereami()
        self.write(self.preview_encoder.encoded_data[0][2])

        bytes_table = self.offsets_encoder.get_bytes_table()
        HEADER_OFFSETS["components_offsets"].encode(self, bytes_table)
        HEADER_OFFSETS["preview_offset"].encode(self, preview_offset)
        HEADER_OFFSETS["preview_offset2"].encode(self, preview_offset)

        with open(filename, "wb") as f:
            f.write(self.f.getbuffer())

    def encode_components(self):
        counter = {0x0: 0, 0x2: 0, 0x3: 0, 0x7: 0}
        for component in self.watch_face.components:
            self.component_encoders.append(ComponentEncoder(component))
            self.component_encoders[-1].encode(counter)
            print(counter)
        return counter

    def encode_preview(self):
        self.preview_encoder = ComponentEncoder(self.watch_face.preview, is_preview=True)
        self.preview_encoder.encode()
