from pathlib import Path

import logging

import dask.array as da
import pyometiff as ome_tiff

from volsegtools._core import AxisValues, DataKind
from volsegtools._model import DatasetMetadata, PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import Dataset
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")

# this library does not have idiomatic support for python loggers, so it is
# poluting our logs.
logging.getLogger("pyometiff").disabled = True


class TIFFConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["ome.tiff", "tiff", "tif", "ome.tif"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[Dataset]:
        vst_logger.info(f"... converting '{input_path}'")

        logging.disable(logging.CRITICAL)
        try:
            reader = ome_tiff.OMETIFFReader(fpath=input_path)
            # the last one are XML metadata in which we are not interested here
            raw_data, metadata, _ = reader.read()
        finally:
            logging.disable(logging.NOTSET)
        data = da.from_array(raw_data)

        # The data might contain time frames and channels; however, it is not
        # a rule and it might happen that either T or C is missing. Thus, we
        # have to add missing dimensions to preserve the same creation logic
        # of the dataset.
        for _ in range(5 - data.ndim):
            data = data[None, ...]

        data = data.transpose(tuple("TCXYZ".index(ax) for ax in metadata["DimOrder"]))

        axes = filter(lambda x: x in ["X", "Y", "Z"], metadata["DimOrder BF Array"])
        axis_order = tuple("XYZ".index(ax) for ax in axes)

        data_set_info = DatasetMetadata(
            filename=input_path.stem,
            resolution=0,
            axis_order=AxisValues(*axis_order),
            cell_size=AxisValues(
                metadata["PhysicalSizeX"] * metadata["SizeX"],
                metadata["PhysicalSizeY"] * metadata["SizeY"],
                metadata["PhysicalSizeZ"] * metadata["SizeZ"],
            ),
            origin=AxisValues(0, 0, 0),
            id=input_path.stem,
            kind=DataKind.VOLUME,
            lattice_shape=AxisValues(
                metadata["SizeX"],
                metadata["SizeY"],
                metadata["SizeZ"],
            ),
        )

        data_set = Dataset(context.working_store, data_set_info)
        for time_frame_data in data:
            frame = data_set.add_time_frame()
            for idx, channel_data in enumerate(time_frame_data):
                channel = frame.add_channel(idx)
                channel.set_data(channel_data, DaskBackend)

        return [data_set]

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[Dataset]:
        raise NotImplementedError()

    async def collect_annotations(self, input_path, context) -> None:
        raise NotImplementedError()

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError()
