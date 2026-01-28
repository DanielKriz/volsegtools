import abc
from typing import Any, List

from volsegtools.abc import DataHandle


class Downsampler(abc.ABC):
    @property
    def parameters(self) -> Any: ...

    @abc.abstractmethod
    async def downsample_lattice(self, data: DataHandle) -> List[DataHandle]:
        """Downsamples the provided lattice.

        The lattice is changed in place and only a reference to the same data
        array is returned.

        Parameters
        ----------
        name: str
            Name of the lattice that should be previously stored in the lattice

        Returns
        -------
        """
        ...
