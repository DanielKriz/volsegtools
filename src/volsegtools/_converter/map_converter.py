from pathlib import Path
from typing import List

import dask.array as da
import mrcfile
import numpy as np

from volsegtools.abc import Converter
from volsegtools._core import LatticeKind, Vector3
from volsegtools._model import StoringParameters, TimeFrameMetadata
from volsegtools._model.opaque_data_handle import OpaqueDataHandle
from volsegtools._model.working_store import WorkingStore

from volsegtools._model import (
    DataSet,
    DataSetInfo,
)


class MapConverter(Converter):
    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        with mrcfile.mmap(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError("Failed to read data from MAP file")

            array = da.from_array(mrc.data)
            array = MapConverter._normalize_axis_order(array, mrc.header)

            data_set_info = MapConverter._collect_data_set_metadata(
                input_path,
                mrc.header,
                LatticeKind.VOLUME,
            )

            data_set = DataSet(data_set_info)
            data_set.add_time_frame()

            WorkingStore.instance.store_lattice_time_frame(
                StoringParameters(
                    lattice_kind=LatticeKind.VOLUME, storage_dtype=mrc.data.dtype
                ),
                array,
                data_set.metadata.id,
            )

            frame = data_set.time_frames[0]
            frame.add_channel(array, 0)

            return [data_set]

            # internal_data = WorkingStore.instance
            # internal_data.volume_dtype = mrc.data.dtype
            # internal_data.is_volume_dtype_set = True
            # volume_id: str = input_path.stem
            # return [internal_data.store_lattice_time_frame(
            #     StoringParameters(), array, volume_id
            # )]

    async def convert_segmentation(self, input_path: Path) -> List[OpaqueDataHandle]:
        with mrcfile.open(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError("Failed to read data from MAP file")

            data = da.from_array(mrc.data)
            data = MapConverter._normalize_axis_order(data, mrc.header)

            if isinstance(data.dtype, np.floating):
                data = data.astype(np.byte)

            internal_data = WorkingStore.instance

            internal_data.volume_dtype = data.dtype
            internal_data.is_volume_dtype_set = True

            segmentation_id: str = input_path.stem

            storing_params = StoringParameters()
            storing_params.storage_dtype = data.dtype
            storing_params.lattice_kind = LatticeKind.SEGMENTATION
            return [
                internal_data.store_lattice_time_frame(
                    storing_params, data, segmentation_id
                )
            ]

    async def collect_annotations(self, input_path) -> None:
        pass

    async def collect_metadata(self, input_path) -> TimeFrameMetadata:
        with mrcfile.open(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError("Failed to read data from MAP file")
            lattice_shape = Vector3(
                int(mrc.header.nx),
                int(mrc.header.ny),
                int(mrc.header.nz),
            )
            header = mrc.header

        axis_order_map = {
            header.mapc - 1: 0,
            header.mapr - 1: 1,
            header.maps - 1: 2,
        }

        axis_order = Vector3(0, 1, 2)

        start = (header.nxstart, header.nystart, header.nzstart)
        start = Vector3(
            start[axis_order_map[0]],
            start[axis_order_map[1]],
            start[axis_order_map[2]],
        )

        original_voxel_size = Vector3(
            header.cella.x,
            header.cella.y,
            header.cella.z,
        )

        origin = Vector3(
            start.x * original_voxel_size.x,
            start.y * original_voxel_size.y,
            start.z * original_voxel_size.z,
        )

        original_time_frame_metadata = TimeFrameMetadata(
            axis_order=axis_order,
            lattice_id=input_path.stem,
            id=0,
            resolution=0,
            origin=origin,
            lattice_dimensions=lattice_shape,
            voxel_size=original_voxel_size,
            # As we are not converting the first resolution to BCIF, this can
            # be left empty.
            channels=[],
        )

        print("Original Metadata:", original_time_frame_metadata)

        return original_time_frame_metadata

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
