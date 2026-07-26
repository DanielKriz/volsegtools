from pathlib import Path

import logging

import dask.array as da
import mrcfile
import numpy as np

from volsegtools._core import DataKind, Vector3
from volsegtools._model import DataSetInfo, PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


# TODO: Make this a template method, where most of the logging is going to be
# handled by the base class.


class MRCConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["mrc", "map", "cpp4"]

    @property
    def supports_compression(self) -> bool:
        return True

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        mrc = mrcfile.mmap(input_path, "r")
        if mrc.data is None or mrc.header is None:
            raise RuntimeError("Failed to read data from MAP file")

        array = da.from_array(mrc.data, chunks=(256, 256, 256))
        array = MRCConverter._normalize_axis_order(array, mrc.header)

        data_set_info = MRCConverter._collect_data_set_metadata(
            input_path,
            mrc.header,
            DataKind.VOLUME,
        )
        mrc.close()

        data_set = DataSet(context.working_store, data_set_info)
        frame = data_set.add_time_frame()

        channel = frame.add_channel(0)
        channel.set_data(array, DaskBackend)
        return [data_set]

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        data_sets = await self.convert_volume(input_path, context)
        for ds in data_sets:
            ds.metadata.kind = DataKind.SEGMENTATION_VOLUME
        return data_sets

    async def collect_annotations(self, input_path, context) -> None:
        pass

    async def collect_metadata(self, input_path, context) -> None:
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

        # We have to completely remove the suffixes to get the id.
        filename = Path(str(file).strip("".join(file.suffixes))).stem

        return DataSetInfo(
            filename=str(file),
            resolution=0,
            axis_order=Vector3(0, 1, 2),  # data should have normalized order
            voxel_size=original_voxel_size,
            origin=origin,
            id=filename,
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
        correct_order = (0, 1, 2)

        current_order = tuple(
            int(axis) - 1 for axis in [header.mapc, header.mapr, header.maps]
        )

        if tuple(current_order) != correct_order:
            da.moveaxis(data, current_order, correct_order)

        data.transpose()

        return data
