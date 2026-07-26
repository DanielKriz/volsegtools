from typing import Union

import dask.array as da
import numpy as np
import zarr

ZarrObject = Union[zarr.Array, zarr.Group]

ArrayType = Union[np.array, np.ndarray, da.Array]

StorableType = Union[ArrayType]

StorableDType = Union[
    np.uint8,
    np.uint16,
    np.uint32,
    np.int8,
    np.int16,
    np.int32,
]
