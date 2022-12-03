from component import Component
from decoder.component_decoder import ComponentDecoder
from constants import HEADER, HEADER_OFFSETS
from decoder.base_decoder import Decoder
from decoder.offsets_decoder import ComponentOffset, ComponentOffsetDecoder
from decoder.watch_face import WatchFace


class WatchFaceDecoder(Decoder):
    def __init__(self, path):
        file = open(path, "rb")

        super().__init__(file)

        self.watch_face = WatchFace()

        self.offsets_decoder = None
        self.components_offsets = None
        self.parse_file()

        file.close()

    def parse_file(self):
        wf = self.watch_face

        f = self.f
        header = self.read(4)
        if header != HEADER:
            raise RuntimeError("Unkown header")

        preview_offset = HEADER_OFFSETS["preview_offset"].extract(self)
        wf.preview = ComponentDecoder(
            f,
            offsets=ComponentOffset([(0x2, ComponentOffset.OffsetInfo(preview_offset))]),
            component_type=Component.PREVIEW).get()
        wf.face_id = HEADER_OFFSETS["face_id"].extract(self)
        wf.name = HEADER_OFFSETS["name"].extract(self)

        components_offsets_end = HEADER_OFFSETS["components_offsets_end"].extract(self)
        self.offsets_decoder = ComponentOffsetDecoder(f, components_offsets_end)
        self.components_offsets = self.offsets_decoder.component_offsets
        for component_offset in self.components_offsets:
            wf.components.append(ComponentDecoder(f, offsets=component_offset).get())

    def get(self):
        return self.watch_face
