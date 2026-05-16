import zarr
from typing import Any, Protocol

class ComputationBackend(Protocol):
    """Provides access to the computation behind arrays."""

    @staticmethod
    def get_name() -> str:
        """Returns name of the backend.
        Returns
        -------
        str:
            Name of the backend.
        """
        ...

    @staticmethod
    def load_from_zarr(zarr_array: zarr.Array) -> Any:
        """Returns the backend's compatible representation of zarr array.

        Parameters
        ----------
        zarr_array: zarr.Array
            An array that we should represent in the backend's compatible
            manner.

        Returns
        -------
        Any:
            An array that is compatible with current backend. Because we do not
            know before-hand how is it going to be used and how is it going to
            look like we do not have any deeper requirements about its type.
        """
        ...

    @staticmethod
    def calculate_statistics(array: Any) -> Any:
        """Calculates statistics of the provided data.

        Parameters
        ----------
        array: Any
            An array that has to be compatible with current backend. We do not
            know before-hand which type is going to be. For more information
            look into `load_from_zarr`.

        Returns
        -------
        Any:
            Statistics of the provided data. Generally, it should adhere to the
            `DescriptiveStatistics` data class.
        """
        ...

    @staticmethod
    def store_to_zarr(array: Any, target_zarr: zarr.Array) -> None: 
        """Stores given data into target zarr array.
        
        Parameters
        ----------
        array: Any
            An array that has to be compatible with current backend. We do not
            know before-hand which type is going to be. For more information
            look into `load_from_zarr`.
        target_zarr: zarr.Array
            An array into which we are going to store the given data.
        """
        ...
