import abc
from pathlib import Path
from typing import Any

from volsegtools.abc import DataHandle


class Converter(abc.ABC):
    """Converts the contents of some file format into the internal data 
    structure that is then going to be used further in the processing.
    """

    @staticmethod
    @abc.abstractmethod
    async def transform_volume(input_path: Path) -> DataHandle:
        """Transforms volumetric data into a zarr array.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.

        Returns
        -------
        Lazy reference to the binary blob data.
        """
        ...

    @staticmethod
    @abc.abstractmethod
    async def transform_segmentation(input_path: Path) -> DataHandle:
        """Transforms the segmentation data into a zarr array.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        """
        ...


    @staticmethod
    @abc.abstractmethod
    async def collect_metadata(input_path) -> Any:
        """Collects metadata from a file.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        internal_data: Data
            Reference to the internal representation of the output. It is
            going to be changed by this method.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    async def collect_annotations(input_path) -> Any:
        """Collects annotations from a file.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        internal_data: Data
            Reference to the internal representation of the output. It is
            going to be changed by this method.
        """
        pass
