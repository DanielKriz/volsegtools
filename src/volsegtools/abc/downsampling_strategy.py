from typing import Any, Protocol

class DownsamplingStrategy(Protocol):
    """Downsamples given data."""
    MIN_SIZE_THRESHOLD = 5_000_000  # 5 MB

    def execute(self, data) -> Any:
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
