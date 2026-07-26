from typing import List
from pathlib import Path
import zipfile
import logging

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools.abc.bundler import Bundler
from volsegtools._storage.data_set import info_from_file_path

vst_logger = logging.getLogger("volsegtools")


class ZipBundler(Bundler):
    def bundle(
        self,
        data_paths: List[Path],
        output_path: Path,
        context: PipelineContext,
    ) -> List[Path]:
        parsed_paths = [info_from_file_path(x) for x in data_paths]

        archive_path = output_path / "vst_output.zip"
        with zipfile.ZipFile(archive_path, "w") as zip:
            for file_info in parsed_paths:
                vst_logger.info(f"... Adding {file_info.file_path.name}")
                zip.write(file_info.file_path, file_info.file_path.name)

        vst_logger.info(f"Created ZIP archive at: {archive_path}")

        return [archive_path]
