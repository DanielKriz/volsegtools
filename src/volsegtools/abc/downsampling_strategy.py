from collections.abc import Iterator
from typing import Protocol, TypeVar

import trimesh

from volsegtools._model import PipelineContext
from volsegtools._storage import Channel

DataType = Channel | trimesh.Trimesh
TData = TypeVar("TData", bound=DataType)

class DownsamplingStrategy(Protocol[TData]):
    """Downsamples given data."""

    MIN_SIZE_THRESHOLD = 5_000_000  # 5 MB

    def execute(
        self,
        data: TData,
        context: PipelineContext,
    ) -> Iterator[TData]:
        """Executes give downsampling strategy on given data.

        It shall be implemented as a generator, where each yield represents
        one smaller resolution of the given data.

        Parameters
        ----------
        data: Union[trimesh.Trimesh, Channel]
            Data that shall be downsampled by the algorithm implemented by
            the strategy. Some strategies might work with meshes and not
            channels.

        Raises
        ------
        TypeError
            If the given data is not of supported type.

        Yields
        ------
        Union[trimesh.Trimesh, Channel]
            Downsampled version of the data.
        """
        ...
