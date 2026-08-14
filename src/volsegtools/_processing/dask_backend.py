from typing import Any

import dask.array as da
import zarr

from volsegtools._model.metadata import DescriptiveStatistics
from volsegtools.abc import ComputationBackend
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

        if hasattr(target_zarr, "shards") and target_zarr.shards is not None:
            target_chunks = target_zarr.shards
        else:
            target_chunks = target_zarr.chunks

        aligned_dask = array.rechunk(target_chunks)

        da.store(
            aligned_dask,
            target_zarr,
            overwrite=True,
            lock=False,
            compute=True,
        )
