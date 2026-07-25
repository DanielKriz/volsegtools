from pathlib import Path
from typing import Any, Protocol


class Converter(Protocol):
    """Converts the contents of some file format into the internal data
    structure that is then going to be used further in the processing.
    """

    async def convert_volume(self, input_path: Path) -> Any:
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

    async def convert_segmentation(self, input_path: Path) -> Any:
        """Transforms the segmentation data into a zarr array.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        """
        ...

    async def collect_metadata(self, input_path) -> Any:
        """Collects metadata from a file.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        internal_data: Data
            Reference to the internal representation of the output. It is
            going to be changed by this method.
        """
        ...

    async def collect_annotations(self, input_path) -> Any:
        """Collects annotations from a file.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        internal_data: Data
            Reference to the internal representation of the output. It is
            going to be changed by this method.
        """
        ...
