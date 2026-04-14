import dataclasses

import numpy as np
import dask.array as da
import dask
from numpy.typing import ArrayLike
from zarr.core.array import Array as ZarrArray

from volsegtools.abc.data_handle import DataHandle
from volsegtools._model.metadata import TimeFrameMetadata, DescriptiveStatistics

# cuPy is an optional import to the volseg-tools (as CUDA may not be available
# everywhere)
# try:
#     import cupy as cp
# except ImportError:
#     # Define the array type as something inacessible
#     ...


class TimeFrameIterator: ...


class ResolutionIterator: ...


class ChannelIterator: ...


@dataclasses.dataclass
class ChannelInfo:
    resolution: str
    time: str
    channel: str
    data: ZarrArray


class FlatChannelIterator:
    def __init__(self, group):
        self.group = group
        self._iter = self._group_iter()

    def _group_iter(self):
        for resolution, resolution_group in self.group.groups():
            for time, time_group in resolution_group.groups():
                for channel, channel_arr in time_group.arrays():
                    yield ChannelInfo(resolution, time, channel, channel_arr)

    def __iter__(self):
        return self

    def __next__(self) -> ChannelInfo:
        return next(self._iter)


class OpaqueDataHandle(DataHandle):
    """Wrapper around basic volseg-tools data model.

    The data held by the data model can potentially be very large and have to
    be storred in files in the files system (usually by leveraging Zarr store).

    This is a wrapper around this file that is passed between the different
    stages and holds the reference to the data stored in the file system. If
    unwrapped then it is directly loaded to the memory as an array.
    """

    def __init__(self, reference):
        if type(reference) is np.ndarray:
            if reference.base is None:
                raise RuntimeError("Data reference can be made only from a view")
        self._metadata = TimeFrameMetadata()
        self._internal_repr = reference

    @property
    def metadata(self) -> TimeFrameMetadata:
        return self._metadata

    @metadata.setter
    def metadata(self, new_metadata) -> None:
        self._metadata = new_metadata

    def access(self) -> ArrayLike:
        return self._internal_repr

    def unwrap(self, target="numpy") -> ArrayLike:
        """
        Supported unwrapping targets are: numpy, dask, and optionally cupy
        """
        match target:
            case "numpy":
                return self._repr_to_numpy_arr()
            case "dask":
                return self._repr_to_dask_arr()
            case "cupy":
                return self._repr_to_cupy_arr()
            case _:
                raise RuntimeError("Unknown unwrapping kind")

    def _repr_to_numpy_arr(self):
        if type(self._internal_repr) is np.ndarray:
            return self._internal_repr.copy()
        elif type(self._internal_repr) is ZarrArray:
            return self._internal_repr[:]

        raise RuntimeError(
            f"Unknown internal representation {type(self._internal_repr)}"
        )

    def _repr_to_dask_arr(self):
        return None

    def _repr_to_cupy_arr(self):
        return None

    def calculate_statistics(self):
        data = da.from_zarr(
            url=self._internal_repr,
            chunks=self._internal_repr.chunks,
        )

        stats = dask.compute(
            da.mean(data),
            da.std(data),
            data.max(),
            data.min(),
        )
        return DescriptiveStatistics(*stats)
