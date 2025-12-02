import abc
import dask.array as da
from typing import Any


class Downsampler(abc.ABC):

    @property
    def parameters(self) -> Any:
        ...

    @abc.abstractmethod
    # TODO: this needs a bit of refactoring, it seems that there is some kind
    # of information leakage
    async def downsample_lattice(self, name, lattice: da.Array, kind) -> da.Array:
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

    @abc.abstractmethod
    def downsample(self, data: Any) -> Any:
        """Downsamples the provided data.

        The downsampling is applied both to the volumetric and segmentation
        data.

        Parameters
        ----------
        data: volseg.Data

        Returns
        -------
        data: volseg.Data
            Reference to the input data, but at this point it is downsampled.
        """
        ...
