import json
import shutil
import tempfile
from pathlib import Path


class Saver:
    def __init__(self, watch_face):
        self.watch_face = watch_face

    def save(self, filename):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            dumped_info = self.watch_face.dump(tmp_dir)
            with open(tmp_dir / "config.json", "w") as f:
                json.dump(dumped_info,
                          f,
                          indent=4,
                          separators=(',', ': '))

            shutil.make_archive(filename, 'zip', tmp_dir)
            # shutil.move(f"{filename}.{zip}", f"{filename}.")
