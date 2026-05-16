from pathlib import Path
from typing import List

import dask.array as da
import mrcfile
import numpy as np
import logging

from volsegtools._model.dask_backend import DaskBackend
from volsegtools.abc import Converter
from volsegtools._core import DataKind, Vector3
from volsegtools._model.working_store import WorkingStore

from volsegtools._model import (
    DataSet,
    DataSetInfo,
)

vst_logger = logging.getLogger("volsegtools")


# TODO: Make this a template method, where most of the logging is going to be
# handled by the base class.

class MRCConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["mrc", "map", "cpp4"]

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")
        with mrcfile.mmap(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError("Failed to read data from MAP file")

            array = da.from_array(mrc.data)
            array = MRCConverter._normalize_axis_order(array, mrc.header)

            data_set_info = MRCConverter._collect_data_set_metadata(
                input_path,
                mrc.header,
                DataKind.VOLUME,
            )

            data_set = DataSet(WorkingStore.instance.data_store, data_set_info)
            frame = data_set.add_time_frame()

            channel = frame.add_channel(0)
            channel.set_data(array, DaskBackend)

            return [data_set]

    async def convert_segmentation(self, input_path: Path) -> List[DataSet]:
        raise NotImplementedError()

    async def collect_annotations(self, input_path) -> None:
        pass

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError

    @staticmethod
    def _collect_data_set_metadata(file, mrc_header, kind) -> DataSetInfo:
        lattice_shape = Vector3(
            int(mrc_header.nx),
            int(mrc_header.ny),
            int(mrc_header.nz),
        )

        axis_order_map = {
            mrc_header.mapc - 1: 0,
            mrc_header.mapr - 1: 1,
            mrc_header.maps - 1: 2,
        }

        start = (mrc_header.nxstart, mrc_header.nystart, mrc_header.nzstart)
        start = Vector3(
            start[axis_order_map[0]],
            start[axis_order_map[1]],
            start[axis_order_map[2]],
        )

        original_voxel_size = Vector3(
            float(mrc_header.cella.x),
            float(mrc_header.cella.y),
            float(mrc_header.cella.z),
        )

        origin = Vector3(
            float(start.x * original_voxel_size.x),
            float(start.y * original_voxel_size.y),
            float(start.z * original_voxel_size.z),
        )

        return DataSetInfo(
            filename=file.stem,
            resolution=0,
            axis_order=Vector3(0, 1, 2),  # data should have normalized order
            voxel_size=original_voxel_size,
            origin=origin,
            id=file.stem,
            kind=kind,
            lattice_shape=lattice_shape,
        )

    @staticmethod
    def _normalize_axis_order(data: da.Array, header: np.recarray) -> da.Array:
        """Normalizes the order of axes in the data to (x, y, z).

        Due to the fact that we use column order we have to transpose
        the array in the end.

        Parameters
        ----------
        data: da.Array
            MCR file data with any order of axes.
        header: np.recarray
            The of the file from which comes the data.

        Returns
        -------
        da.Array
            Array with normalized order of axes. It is the view to the input
            array.
        """
        CORRECT_ORDER = (0, 1, 2)

        current_order = tuple(
            int(axis) - 1 for axis in [header.mapc, header.mapr, header.maps]
        )

        if tuple(current_order) != CORRECT_ORDER:
            da.moveaxis(data, current_order, CORRECT_ORDER)

        data.transpose()

        return data
