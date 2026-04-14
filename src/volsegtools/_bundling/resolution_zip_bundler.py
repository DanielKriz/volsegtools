from typing import List
from pathlib import Path

from volsegtools.abc.bundler import Bundler


class ResolutionZipBundler(Bundler):
    def bundle(self, data: List[Path], output_path: Path) -> List[Path]:
        # 1. sort data into lists per resolution
        # 2. bundle each into a zip file separately
        return [Path()]
