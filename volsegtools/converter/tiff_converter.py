from pathlib import Path

import dask.array as da
import tifffile as tiff
import numpy as np

from volsegtools.abc import Converter
from volsegtools.core import LatticeKind, Vector3
from volsegtools.model import StoringParameters, TimeFrameMetadata
from volsegtools.model.opaque_data_handle import OpaqueDataHandle
from volsegtools.model.working_store import WorkingStore

class TIFFConverter(Converter):
    @staticmethod
    async def transform_volume(input_path: Path) -> OpaqueDataHandle:
        if not input_path.exists():
            raise RuntimeError(f"You have to provide a valid file, {input_path} does not exists")

        img_data = tiff.imread()
        # array = da.from_array(data_array)

        with TiffFile(input_path) as file:
            axes_str = file.series[0].axes
            axes = { axis:pos for pos, axis in enumerate(axes_str) }
            arr = file.asarray()
            if "C" in axes.keys():
                orig_axis_order = [axes["C"], axes["X"], axes["Y"], axes["Z"]]
                view = arr.moveaxis(arr, orig_axis_order, [0, 1, 2, 3])
            else:
                orig_axis_order = [axes["X"], axes["Y"], axes["Z"]]
                view = arr.moveaxis(arr, orig_axis_order, [0, 1, 2])


        internal_data = WorkingStore.instance
        internal_data.volume_dtype = array.dtype
        internal_data.is_volume_dtype_set = True
        volume_id: str = input_path.stem

        return internal_data.store_lattice_time_frame(
            StoringParameters(), array, volume_id
        )

    @staticmethod
    async def transform_segmentation(input_path: Path) -> OpaqueDataHandle:
        return None
