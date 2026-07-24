import zarr
import numpy as np
from typing import Any

from volsegtools.abc import ComputationBackend
from volsegtools._model.data_set import DescriptiveStatistics
from volsegtools.typing import ZarrObject


class NumPyBackend(ComputationBackend):
    DEFAULT_CHUNKS = (256, 256, 256)

    @staticmethod
    def get_name() -> str:
        return "numpy"

    @staticmethod
    def load_from_zarr(zarr_object: ZarrObject) -> Any:
        if isinstance(zarr_object, zarr.Group):
            raise RuntimeError("Cannot load dask array from group")
        return zarr_object[...]

    @staticmethod
    def calculate_statistics(array) -> DescriptiveStatistics:
        return DescriptiveStatistics(
            mean=np.mean(array),
            std=np.std(array),
            max=np.max(array),
            min=np.min(array),
        )

    @staticmethod
    def store_to_zarr(array, target_zarr: ZarrObject) -> None:
        if isinstance(target_zarr, zarr.Group):
            raise RuntimeError("Cannot store dask array to group")
        target_zarr[:] = array[:]
