from pathlib import Path
from typing import List

import dask.array as da
import pyometiff as ome_tiff
import logging

from volsegtools._processing.dask_backend import DaskBackend
from volsegtools.abc import Converter
from volsegtools._core import DataKind, Vector3, WorkingStore

from volsegtools._model import (
    DataSet,
    DataSetInfo,
)

vst_logger = logging.getLogger("volsegtools")


class TIFFConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["ome.tiff", "tiff", "tif", "ome.tif"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        reader = ome_tiff.OMETIFFReader(fpath=input_path)
        # the last one are XML metadata in which we are not interested here
        data_array, metadata, _ = reader.read()
        array = da.from_array(data_array)

        axis_order_map = {}
        for idx, axis in enumerate(
            filter(lambda x: x in ["X", "Y", "Z"], metadata["DimOrder BF Array"])
        ):
            axis_order_map[idx] = axis

        current_order = "{}{}{}".format(
            axis_order_map[0],
            axis_order_map[1],
            axis_order_map[2],
        )

        target_order = "XYZ"
        permutation = tuple(current_order.find(axis) for axis in target_order)

        data_set_info = DataSetInfo(
            filename=input_path.stem,
            resolution=0,
            axis_order=Vector3(0, 1, 2),
            voxel_size=Vector3(
                metadata["PhysicalSizeX"] * 100,
                metadata["PhysicalSizeY"] * 100,
                metadata["PhysicalSizeZ"] * 100,
            ),
            origin=Vector3(0, 0, 0),
            id=input_path.stem,
            kind=DataKind.VOLUME,
            lattice_shape=Vector3(
                metadata["SizeX"],
                metadata["SizeY"],
                metadata["SizeZ"],
            ),
        )

        data_set = DataSet(WorkingStore.instance.data_store, data_set_info)
        if data_array.ndim == 5:
            # There are multiple frames
            raise NotImplementedError()
        elif data_array.ndim == 4:
            frame = data_set.add_time_frame()
            for idx, channel_data in enumerate(array):
                transposed = channel_data.transpose(permutation)
                channel = frame.add_channel(idx)
                channel.set_data(transposed, DaskBackend)
        else:
            frame = data_set.add_time_frame()
            transposed = array.transpose(permutation)
            channel = frame.add_channel(0)
            channel.set_data(transposed, DaskBackend)

        return [data_set]

    async def convert_segmentation(self, input_path: Path) -> List[DataSet]:
        raise NotImplementedError()

    async def collect_annotations(self, input_path) -> None:
        raise NotImplementedError()

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError()
