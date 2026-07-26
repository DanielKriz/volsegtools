from typing import Any

from numpy.typing import NDArray

import dask.array as da
import numpy as np
import zarr

ZarrObject = zarr.Array | zarr.Group

ArrayType = NDArray[Any] | da.Array

StorableType = ArrayType

StorableDType = np.uint8 | np.uint16 | np.uint32 | np.int8 | np.int16 | np.int32

__all__ = [
    "ArrayType",
    "StorableDType",
    "StorableType",
    "ZarrObject",
]
