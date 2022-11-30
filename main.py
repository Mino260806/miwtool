from config import Config
from decoder.watch_face_decoder import WatchFaceDecoder
from encoder.watch_face_encoder import WatchFaceEncoder
from memory.loader import Loader
from memory.saver import Saver
from wfeditor.parser import WFEditorParser

from argparse import ArgumentParser
import os


def execute_tests():
    try:
        from tests import test
        test()
    except ModuleNotFoundError:
        print("No tests")


if "TEST" in os.environ:
    execute_tests()

elif __name__ == '__main__':
    parser = ArgumentParser(
        description='decode / encode Redmi Watch 2 Lite watch faces',
        epilog='//// coded by Amin Guermazi'
               ' - https://github.com/Mino260806')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--decode", type=str)
    group.add_argument("-e", "--encode", type=str)
    group.add_argument("-dw", "--decode_wfeditor", type=str)
    group.add_argument("-ew", "--encode_wfeditor", type=str)
    parser.add_argument("-o", "--output", type=str, default="watchface")

    parser.add_argument("-ce", "--colorendianness", type=str, choices=["little", "big"], default="big")

    args = parser.parse_args()
    config = Config(args.colorendianness)
    config.propagate()
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

    if args.decode_wfeditor:
        input_file = args.decode_wfeditor
        output_file = args.output

        parser = WFEditorParser(input_file)
        watchface = parser.watchface

        Saver(watchface).save(output_file)

    if args.encode_wfeditor:
        input_file = args.encode_wfeditor
        output_file = args.output

        parser = WFEditorParser(input_file)
        watchface = parser.watchface

        encoder = WatchFaceEncoder(watchface)
        encoder.encode(output_file)
