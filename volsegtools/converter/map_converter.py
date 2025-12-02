from collections import defaultdict
import dask.array as da
import mrcfile
import numpy as np

from pathlib import Path

from volsegtools.abc import Converter
from volsegtools.core import Vector3
from volsegtools.model import (
    Data,
    OriginalTimeFrameMetadata,
    Metadata,
    StoringParameters,
    LatticeKind,
)

class MapConverter(Converter):

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

    
    @staticmethod
    async def transform_volume(input_path: Path, internal_data: Data) -> None:
        with mrcfile.mmap(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError('Failed to read data from MAP file')

            array = da.from_array(mrc.data)
            array = MapConverter._normalize_axis_order(array, mrc.header)
            internal_data.volume_dtype = mrc.data.dtype
            internal_data.is_volume_dtype_set = True
            # TODO: Do not store the data as ints here! It wouldn't make sense!
            volume_id: str = input_path.stem
            internal_data.store_lattice_time_frame(StoringParameters(), array, volume_id)


    @staticmethod
    async def transform_segmentation(input_path, internal_data: Data) -> None:
        with mrcfile.open(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError('Failed to read data from MAP file')

            data = da.from_array(mrc.data)
            data = MapConverter._normalize_axis_order(data, mrc.header)

            if isinstance(data.dtype, np.floating):
                data = data.astype(np.byte)

            internal_data.volume_dtype = data.dtype
            internal_data.is_volume_dtype_set = True

            segmentation_id: str = input_path.stem
            internal_data.segmentation_lattices[segmentation_id] = set(
                da.unique(data).flatten().compute()
            )

            storing_params = StoringParameters()
            storing_params.storage_dtype = data.dtype
            storing_params.lattice_kind = LatticeKind.SEGMENTATION
            # storing_params.is_compression_enabled = True

            # internal_data.store_lattice_for_segmentation(
            #     storing_params,
            #     data,
            #     segmentation_id,
            # )
            internal_data.store_lattice_time_frame(storing_params, data, segmentation_id)


    @staticmethod
    async def collect_annotations(input_path, internal_data: Data) -> None:
        pass

    @staticmethod
    async def collect_metadata(input_path, internal_data: Data) -> None:
        with mrcfile.open(input_path, "r+") as mrc:
            if mrc.data is None or mrc.header is None:
                raise RuntimeError('Failed to read data from MAP file')
            # lattice_shape = Vector3(
            #     mrc.data.shape[0],
            #     mrc.data.shape[1],
            #     mrc.data.shape[2],
            # )
            lattice_shape = Vector3(
                int(mrc.header.nx),
                int(mrc.header.ny),
                int(mrc.header.nz),
            )
            header = mrc.header
        current_axis_order = tuple(
            int(axis) - 1 for axis in [header.mapc, header.mapr, header.maps]
        )

        print("CURRENT AXIS ORDER:", current_axis_order)
        print("CURRENT AXIS UNMOD:", [header.mapc, header.mapr, header.maps])
        print("Dimensions of Thingy:", lattice_shape)

        axis_order_map = {
            header.mapc - 1 : 0,
            header.mapr - 1 : 1,
            header.maps - 1 : 2,
        }

        # Rework!
        # axes = (header.nx, header.ny, header.nz)
        # axes = (
        #     axes[axis_order_map[0]],
        #     axes[axis_order_map[1]],
        #     axes[axis_order_map[2]],
        # )
        # axis_order = Vector3(
        #     axes[axis_order_map[0]],
        #     axes[axis_order_map[1]],
        #     axes[axis_order_map[2]],
        # )
        axes = [0, 1, 2]
        axis_order = Vector3(0, 1, 2)

        start = (header.nxstart, header.nystart, header.nzstart)
        print("START:", start)
        start = Vector3(
            start[axis_order_map[0]],
            start[axis_order_map[1]],
            start[axis_order_map[2]],
        )

        print("CELLA:", (header.cella.x, header.cella.y, header.cella.z))
        print("N-XYZ:", (header.nx, header.ny, header.nz))
        print("SHAPE:", lattice_shape)
        # original_voxel_size = Vector3(
        #     header.cella.x / lattice_shape.x,
        #     header.cella.y / lattice_shape.y,
        #     header.cella.z / lattice_shape.z,
        # )
        print("ANGSTROM VOXEL SIZE:", header.cella)
        original_voxel_size = Vector3(
            header.cella.x / header.nx,
            header.cella.y / header.ny,
            header.cella.z / header.nz,
        )
        original_voxel_size = Vector3(
            header.cella.x,
            header.cella.y,
            header.cella.z,
        )
        print("ORIGINAL VOXEL SIZE:", original_voxel_size)

        origin = Vector3(
            start.x * original_voxel_size.x,
            start.y * original_voxel_size.y,
            start.z * original_voxel_size.z,
        )
        print("ORIGIN:", start)

        original_time_frame_metadata = OriginalTimeFrameMetadata(
            id=0,
            resolution=0,
            origin=origin,
            lattice_dimensions=lattice_shape,
            voxel_size=original_voxel_size,
            # As we are not converting the first resolution to BCIF, this can
            # be left empty.
            channels=[],
            axis_order=axis_order
        )

        internal_data.metadata = Metadata(original_time_frame_metadata, [])

