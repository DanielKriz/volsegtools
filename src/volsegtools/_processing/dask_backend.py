import zarr
import dask
import dask.config
import math
import dask.array as da

from typing import Any

from volsegtools.abc import ComputationBackend
from volsegtools._model.metadata import DescriptiveStatistics
from volsegtools.typing import ZarrObject


class DaskBackend(ComputationBackend):
    DEFAULT_CHUNKS = (256, 256, 256)

    @staticmethod
    def get_name() -> str:
        return "dask"

    @staticmethod
    def load_from_zarr(zarr_object: ZarrObject) -> Any:
        if isinstance(zarr_object, zarr.Group):
            raise RuntimeError("Cannot load dask array from group")
        return da.from_zarr(
            url=zarr_object,
            chunks=DaskBackend.DEFAULT_CHUNKS,
        )

    @staticmethod
    def calculate_statistics(array: da.Array) -> DescriptiveStatistics:
        array = da.from_zarr(array)
        stats = da.compute(
            da.mean(array),
            da.std(array),
            da.max(array),
            da.min(array),
        )

        return DescriptiveStatistics(*stats)

    @staticmethod
    def store_to_zarr(array: da.Array, target_zarr: ZarrObject) -> None:
        if isinstance(target_zarr, zarr.Group):
            raise RuntimeError("Cannot store dask array to group")
        target_chunks = target_zarr.chunks
        aligned_dask = array.rechunk(target_chunks)
        chunk_bytes = math.prod(target_chunks) * array.dtype.itemsize
        with dask.config.set({"array.chunk-size": chunk_bytes}):
            da.to_zarr(
                arr=aligned_dask,
                url=target_zarr,
                overwrite=True,
                compute=True,
            )
