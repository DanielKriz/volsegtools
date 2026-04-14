import molviewspec as mvs
from typing import List
from pathlib import Path

from volsegtools.abc.bundler import Bundler


class MVSXBundler(Bundler):
    def bundle(self, data: List[Path], output_path: Path) -> List[Path]:
        builder = mvs.create_builder()

        for path in data:
            volume = builder.download(url=path).parse("bcif").volume()
            volume.representation(
                type="isosurface", relative_isovalue=1, show_wireframe=True
            ).opacity(0.25)
            # file_info = info_from_file_path(path)
