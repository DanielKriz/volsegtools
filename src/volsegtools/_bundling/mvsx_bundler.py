import collections
import itertools
import logging
from pathlib import Path
from typing import List

import molviewspec as mvs
from molviewspec.mvsx_converter import tempfile

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._storage.data_set import info_from_file_path
from volsegtools.abc.bundler import Bundler

vst_logger = logging.getLogger("volsegtools")

# It is better to distinguish between the individual primitives with colors.
X11_COLOR_NAMES = [
    "silver",
    "red",
    "aqua",
    "green",
    "wheat",
    "orange",
    "palegreen",
    "violet",
    "sienna",
    "olive",
    "pink",
    "ivory",
    "purple",
    "coral",
    "blue",
    "yellow",
    "brown",
]


class MVSXBundler(Bundler):
    """Bundler for the MVSX format."""

    def bundle(
        self,
        data_paths: List[Path],
        output_path: Path,
        context: PipelineContext,
    ) -> List[Path]:
        parsed_paths = [info_from_file_path(x) for x in data_paths]

        data_per_resolution = collections.defaultdict(list)
        for key, group in itertools.groupby(parsed_paths, lambda x: x.resolution):
            data_per_resolution[key] += list(group)

        output_file_paths = []

        for resolution in data_per_resolution.keys():
            builder = mvs.create_builder()

            data_set_id = data_per_resolution[resolution][0].data_set
            vst_logger.info(
                f"Bundling Data set '{data_set_id}' with resolution {resolution}"
            )

            for idx, info in enumerate(data_per_resolution[resolution]):
                vst_logger.info(f"... Adding {info.file_path.name}")

                match info.suffix:
                    case "mrc":
                        format = "map"
                    case "bcif":
                        format = "bcif"
                    case _:
                        raise RuntimeError("Unsuported volume format")

                volume = (
                    builder.download(url=str(info.file_path))
                    .parse(format=format)
                    .volume()
                )
                volume.representation(
                    type="isosurface", relative_isovalue=2, show_wireframe=False
                ).color(color=X11_COLOR_NAMES[idx % len(X11_COLOR_NAMES)])

            archive_path = output_path / Path(f"{data_set_id}_r{resolution}.mvsx")

            # At the moment we have to create a temporary file to use the mvs
            # API for creation of MVSX
            with tempfile.NamedTemporaryFile(mode="w", delete=True) as tmp_file:
                state = mvs.MVSJ(data=builder.get_state()).dumps()
                tmp_file.write(state)
                # We have to make sure that the file is written before using it.
                tmp_file.flush()

                mvs.mvsj_to_mvsx(
                    tmp_file.name,
                    archive_path,
                    download_external=True,
                )
                output_file_paths.append(archive_path)
                vst_logger.info(f"Created MVSX archive at: {archive_path}")

        return output_file_paths
