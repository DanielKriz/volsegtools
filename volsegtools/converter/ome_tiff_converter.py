from pathlib import Path

import dask.array as da
import pyometiff as ome_tiff
import numpy as np

from volsegtools.abc import Converter
from volsegtools.core import LatticeKind, Vector3
from volsegtools.model import StoringParameters, TimeFrameMetadata
from volsegtools.model.opaque_data_handle import OpaqueDataHandle
from volsegtools.model.working_store import WorkingStore

class OMETiFFConverter(Converter):
    @staticmethod
    async def transform_volume(input_path: Path) -> OpaqueDataHandle:
        if not input_path.exists():
            raise RuntimeError(f"You have to provide a valid file, {input_path} does not exists")

        reader = ome_tiff.OMETIFFReader(fpath=input_path)
        data_array, metadata, xml_metadata = reader.read()
        array = da.from_array(data_array)

        print(metadata)
        print(xml_metadata)
        print(array.shape)

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
