import asyncio
from pathlib import Path
from typing import List, Optional

from volsegtools.abc import Converter, Downsampler
from volsegtools._core.lattice_kind import LatticeKind
from volsegtools._model.working_store import WorkingStore
from volsegtools._serialization import BCIFSerializer


class Preprocessor:
    state = {"downsampling_status": 0.0}

    def __init__(
        self,
        downsampler: Downsampler,
        converter: Converter,
        volume_input_files: List[Path],
        segmentation_input_files: List[Path],
        metadata_input_files: Optional[List[Path]] = None,
        annotations_input_files: Optional[List[Path]] = None,
        work_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        self.converter: Converter = converter
        self._output_dir = output_dir if output_dir is not None else Path()
        self._data = WorkingStore.instance
        self.downsampler = downsampler
        self._volume_input_files = volume_input_files
        self._segmentation_input_files = segmentation_input_files
        self._metadata_input_files = metadata_input_files
        self._annotations_input_files = annotations_input_files
        self._work_dir = work_dir

    async def transform_volume(self):
        raise NotImplementedError()

    async def collect_metadata(self):
        raise NotImplementedError()

    def create_converter_from_format(self):
        raise NotImplementedError()

    async def transform_segmentation(self):
        raise NotImplementedError()

    async def preprocess(self):
        raise NotImplementedError()

    def sync_preprocess(self):
        data = []

        # 1. Data conversion phase
        for path in self._volume_input_files:
            data.append(asyncio.run(self.converter.transform_volume(path)))
            data[-1].metadata = asyncio.run(self.converter.collect_metadata(path))
            # FIX: This should be automatic!
            data[-1].metadata.kind = LatticeKind.VOLUME
        for path in self._segmentation_input_files:
            data.append(asyncio.run(self.converter.transform_segmentation(path)))
            data[-1].metadata = asyncio.run(self.converter.collect_metadata(path))
            # FIX: This should be automatic!
            data[-1].metadata.kind = LatticeKind.SEGMENTATION

        downsampled_data = []
        for ref in data:
            # TODO: it has to be flattened!
            downsampled_data += asyncio.run(self.downsampler.downsample_lattice(ref))
        print("Downsampled Data:", downsampled_data)
        # 4. Serialization Phase
        for ref in downsampled_data:
            asyncio.run(BCIFSerializer.serialize(ref, self._output_dir))

    def downsample(self):
        pass
