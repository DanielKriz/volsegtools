import dask.array as da
import numpy as np
import zarr

ZarrObject = zarr.Array | zarr.Group

ArrayType = np.array | np.ndarray | da.Array

StorableType = ArrayType

StorableDType = np.uint8 | np.uint16 | np.uint32 | np.int8 | np.int16 | np.int32
