from typing import List
from pathlib import Path
import zipfile

from volsegtools.abc.bundler import Bundler


class ZipBundler(Bundler):
    def bundle(self, data: List[Path], output_path: Path) -> List[Path]:
        zip_file = output_path / "vst_output.zip"
        with zipfile.ZipFile(zip_file, "w") as zip:
            for path in data:
                zip.write(path)

        return [zip_file]
