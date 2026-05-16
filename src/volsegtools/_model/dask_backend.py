import zarr
import dask
import dask.config
import math
import dask.array as da

from volsegtools._model.computation_backend import ComputationBackend
from volsegtools._model.data_set import DescriptiveStatistics


class DaskBackend(ComputationBackend):
    DEFAULT_CHUNKS = (256, 256, 256)


    @staticmethod
    def get_name() -> str:
        return "dask"


    @staticmethod
    def load_from_zarr(zarr_array: zarr.Array) -> da.Array:
        return da.from_zarr(
            url=zarr_array,
            chunks=DaskBackend.DEFAULT_CHUNKS,
        )


    @staticmethod
    def calculate_statistics(array: da.Array) -> DescriptiveStatistics:
        stats = da.compute(
            da.mean(array),
            da.std(array),
            da.max(array),
            da.min(array),
        )

        return DescriptiveStatistics(*stats)

    @staticmethod
    def store_to_zarr(array: da.Array, target_zarr: zarr.Array) -> None:
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
