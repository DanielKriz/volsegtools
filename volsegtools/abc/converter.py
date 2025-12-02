import abc
from pathlib import Path
from typing import Any

class Converter(abc.ABC):
    """Converts the contents of some file format into the internal data 
    structure that is then going to be used further in the processing.
    """

    @staticmethod
    @abc.abstractmethod
    async def transform_volume(input_path: Path, internal_data: Any) -> None:
        """Transforms the volumetric data into a zarr array.

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
    async def transform_segmentation(input_path, internal_data: Any) -> None:
        """Transforms the segmentation data into a zarr array.

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
    async def collect_metadata(input_path, internal_data: Any) -> None:
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
    async def collect_annotations(input_path, internal_data: Any) -> None:
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
