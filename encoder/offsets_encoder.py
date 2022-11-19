from encoder.base_encoder import Encoder


class OffsetsEncoder(Encoder):
    def __init__(self, counter):
        super().__init__()
        self.counter = counter
        self.offsets_table = []

    def add_offset(self, property_type, property_index, offset, data_size):
        self.offsets_table.append((property_type, property_index, offset, data_size))

    def __len__(self):
        return sum(self.counter.values())

    @property
    def nbytes(self):
        return len(self) * 0x10

    def get_bytes_table(self):
        self.offsets_table.sort()

        self.set_buffer()

        for offset_details in self.offsets_table:
            self.writele(offset_details[1], 0x2)
            self.writele(0, 0x1)
            self.writele(offset_details[0], 0x2)
            self.writele(0, 0x3)
            self.writele(offset_details[2], 0x4)
            self.writele(offset_details[3], 0x4)

        return self.pop_buffer()

    def get_bytes_description(self):
        self.set_buffer(0x50)

        offset = 0x100

        self.writele(self.counter[0], 0x2)
        self.writele(0, 0x2)
        self.writele(offset, 0x2)
        self.writele(0, 0x2)

        offset += self.counter[0] * 0x10
        self.writele(0, 0x4)
        self.writele(offset, 0x2)
        self.writele(0, 0x2)

        self.writele(self.counter[2], 0x2)
        self.writele(0, 0x2)
        self.writele(offset, 0x2)
        self.writele(0, 0x2)

        offset += self.counter[2] * 0x10
        self.writele(self.counter[3], 0x2)
        self.writele(0, 0x2)
        self.writele(offset, 0x2)
        self.writele(0, 0x2)

        offset += self.counter[3] * 0x10
        for i in range(3):
            self.writele(0, 0x4)
            self.writele(offset, 0x2)
            self.writele(0, 0x2)

        self.writele(self.counter[7], 0x2)
        self.writele(0, 0x2)
        self.writele(offset, 0x2)
        self.writele(0, 0x2)

        offset += self.counter[7] * 0x10
        for i in range(2):
            self.writele(0, 0x4)
            self.writele(offset, 0x2)
            self.writele(0, 0x2)

        return self.pop_buffer()
