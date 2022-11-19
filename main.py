from decoder.watch_face_decoder import WatchFaceDecoder
from encoder.watch_face_encoder import WatchFaceEncoder
from memory.loader import Loader
from memory.saver import Saver


from argparse import ArgumentParser


def execute_tests():
    pass


if __name__ == '__main__':
    parser = ArgumentParser(
        description='decode / encode Redmi Watch 2 Lite watch faces',
        epilog='//// coded by Amin Guermazi'
               ' - https://github.com/Mino260806')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--decode", type=str)
    group.add_argument("-e", "--encode", type=str)
    parser.add_argument("-o", "--output", type=str, default="watchface")

    args = parser.parse_args()
    if args.encode:
        input_file = args.encode
        output_file = args.output

        watchface = Loader(input_file).get()
        encoder = WatchFaceEncoder(watchface)
        encoder.encode(output_file)

    if args.decode:
        input_file = args.decode
        output_file = args.output

        decoder = WatchFaceDecoder(input_file)
        watchface = decoder.get()

        Saver(watchface).save(output_file)
