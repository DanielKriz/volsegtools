import collections
import molviewspec as mvs
from typing import List
from pathlib import Path
import itertools
import logging

from molviewspec.mvsx_converter import tempfile

from volsegtools._model.data_set import info_from_file_path
from volsegtools.abc.bundler import Bundler


class MVSXBundler(Bundler):
    def bundle(self, data_paths: List[Path], output_path: Path) -> List[Path]:
        parsed_paths = [info_from_file_path(x) for x in data_paths]

        data_per_resolution = collections.defaultdict(list)
        for key, group in itertools.groupby(parsed_paths, lambda x: x.resolution):
            data_per_resolution[key] += list(group)

        output_file_paths = []

        for resolution in data_per_resolution.keys():
            builder = mvs.create_builder()

            data_set_id = data_per_resolution[resolution][0].data_set
            logging.info(
                f"Bundling Data set {data_set_id} with resolution {resolution}"
            )

            for info in data_per_resolution[resolution]:
                logging.info(f"... Adding {info.file_path.name}")
                volume = (
                    builder.download(url=str(info.file_path))
                    .parse(format="map")
                    .volume()
                )
                volume.representation(
                    type="isosurface", relative_isovalue=2, show_wireframe=False
                ).color(color="red")

            with tempfile.NamedTemporaryFile(mode="w", delete=True) as tmp_file:
                state = mvs.MVSJ(data=builder.get_state()).dumps()
                tmp_file.write(state)
                # We have to make sure that the file is written before using it.
                tmp_file.flush()

                output_file_paths.append(
                    mvs.mvsj_to_mvsx(
                        tmp_file.name,
                        output_path / Path(f"{data_set_id}_r{resolution}.mvsx"),
                        download_external=True,
                    )
                )

        return output_file_paths
