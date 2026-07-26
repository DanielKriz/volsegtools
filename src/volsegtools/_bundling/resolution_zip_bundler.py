from pathlib import Path

import collections
import itertools
import logging
import zipfile

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._storage.data_set import info_from_file_path
from volsegtools.abc.bundler import Bundler

vst_logger = logging.getLogger("volsegtools")


class ResolutionZipBundler(Bundler):
    def bundle(
        self,
        data_paths: list[Path],
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]:
        parsed_paths = [info_from_file_path(x) for x in data_paths]

        data_per_resolution = collections.defaultdict(list)
        for key, group in itertools.groupby(parsed_paths, lambda x: x.resolution):
            data_per_resolution[key] += list(group)

        output_file_paths = []

        for resolution in data_per_resolution:
            data_set_id = data_per_resolution[resolution][0].data_set

            archive_path = output_path / Path(f"{data_set_id}_r{resolution}.zip")
            with zipfile.ZipFile(archive_path, "w") as archive:
                for info in data_per_resolution[resolution]:
                    vst_logger.info(f"... Adding {info.file_path.name}")
                    archive.write(info.file_path, info.file_path.name)
            output_file_paths.append(archive_path)
            vst_logger.info(f"Created ZIP archive at: {archive_path}")

        return output_file_paths
