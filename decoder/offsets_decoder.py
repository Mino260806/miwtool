from constants import HEADER_OFFSETS, OFFSETS_DETAILS_OFFSETS, WIDGET_CONFIGURATION_OFFSETS, INVERSE_COORDINATES_TABLE
from decoder.base_decoder import Decoder


class ComponentOffset:
    class OffsetInfo:
        def __init__(self, value, size=-1):
            self.value = value
            self.size = size

    def __init__(self, offsets=None):
        if offsets is None:
            offsets = []
        self.offsets = offsets

    def add_offset(self, offset, block_size, otype):
        self.offsets.append((otype, ComponentOffset.OffsetInfo(offset, block_size)))

    def __iter__(self):
        return self.offsets.__iter__()


class ComponentOffsetDecoder(Decoder):
    def __init__(self, file, end_offset):
        super().__init__(file)

        self.components_count = None
        self.end_offset = end_offset
        self.component_offsets = []
        self.raw_offsets = {}

        self.parse_file()

    def parse_file(self):
        self.components_count = HEADER_OFFSETS["components_count"].extract(self)

        HEADER_OFFSETS["components_offsets"].goto(self)
        self.pin_offset()

        doffset = 0x0
        while self.offset + doffset < self.end_offset:
            component_index = OFFSETS_DETAILS_OFFSETS["component_index"].extract(self, doffset)
            offset_type = OFFSETS_DETAILS_OFFSETS["offset_type"].extract(self, doffset)
            component_offset = OFFSETS_DETAILS_OFFSETS["component_offset"].extract(self, doffset)
            block_size = OFFSETS_DETAILS_OFFSETS["block_size"].extract(self, doffset)

            if offset_type not in self.raw_offsets:
                self.raw_offsets[offset_type] = []

            if component_index != len(self.raw_offsets[offset_type]):
                raise RuntimeError("component_index > len(offsets[offset_type])")

            self.raw_offsets[offset_type].append((component_offset, block_size))

            doffset += 0x10

        self.unpin_offset()

        for i in range(self.components_count):
            start_offset, start_offset_size = self.raw_offsets[0x0][i]
            self.component_offsets.append(ComponentOffset())
            self.process_offset(i, 0x0, start_offset, start_offset_size)

    def process_offset(self, component_index, source_offset_type, source_offset, source_offset_size):
        print(component_index, source_offset_type, hex(source_offset), hex(source_offset_size))
        self.component_offsets[component_index].add_offset(source_offset, source_offset_size, source_offset_type)

        for doffset in self.get_doffsets(source_offset, source_offset_type, source_offset_size):
            self.seek(source_offset + doffset)
            next_offset_index = self.read_ile(1)
            self.read_ile(2)
            next_offset_type = self.read_ile(1)

            if next_offset_type == 0x0:
                continue

            next_offset, next_offset_size = self.raw_offsets[next_offset_type][next_offset_index]
            self.process_offset(component_index, next_offset_type, next_offset, next_offset_size)

    def get_doffsets(self, offset, offset_type, offset_size):
        # useful_info_offset = {
        #     0x0: (0x0,),
        #     0x2: (),
        #     0x3: (),
        #     0x7: None
        # }
        # if offset_type in useful_info_offset:
        #     doffsets = useful_info_offset[offset_type]
        #     if offset_type == 0x7:
        #         if offset_size == 0x14:
        #             doffsets = (0x8, 0x10)
        #         elif offset_size == 0x28: # masked rotation
        #             doffsets = (0x8, 0xc)
        #         else:
        #             doffsets = (0x8,)
        #     return doffsets
        # return ()
        if offset_type == 0x0:
            return (0x0,)
        elif offset_type == 0x7:
            ctypes = WIDGET_CONFIGURATION_OFFSETS["coordinate_types"].extract(self, offset)
            if ctypes == INVERSE_COORDINATES_TABLE["RMSS"]:
                return (0x8, 0xc)
            elif ctypes <= 0x16 and offset_size == 0x14: # decimal
                return (0x8, 0x10)
            return (0x8,)
        else:
            return ()
