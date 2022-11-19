import json
import shutil
import tempfile
from pathlib import Path

from decoder.watch_face import WatchFace


class Loader:
    def __init__(self, path):
        self.watch_face = WatchFace()

        path = Path(path)
        if path.is_dir():
            self.load_path_folder(path)
        else:
            self.load_path_file(path)

    def load_path_file(self, filename):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            shutil.unpack_archive(filename, tmp_dir)
            self.load_path_folder(tmp_dir)

    def load_path_folder(self, folder):
        with open(folder / "config.json", "r") as f:
            dumped_info = json.load(f)

        self.watch_face.load_from_dump(folder, dumped_info)

    def get(self):
        return self.watch_face
