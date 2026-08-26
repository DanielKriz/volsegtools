from pathlib import Path
from typing import Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage.data_set import DataSet


class Converter(Protocol):
    """Converts the contents of some file format into the internal data
    structure that is then going to be used further in the processing.
    """

    @property
    def supported_suffixes(self) -> list[str]:
        """Returns the list of supported file suffixes.

        Some converters might support multiple formats, or the formats commonly
        has several different suffixes (e.g., MRC can be found as .map, .mrc
        or .ccp4).

        Returns
        -------
        list[str]:
            List of supported file suffixes.
        """
        ...

    @property
    def supports_compression(self) -> bool:
        """Returns the list of supported file suffixes.

        Some converters might support multiple formats, or the formats commonly
        has several different suffixes (e.g., MRC can be found as .map, .mrc
        or .ccp4).

        Returns
        -------
        list[str]:
            List of supported file suffixes.
        """
        ...

    def is_suffix_supported(self, suffix: str) -> bool:
        """Checks whether given file suffix is supported by this converter.

        Attributes
        ----------
        suffix: str
            Suffix of a file that we want to know if it is supported by this
            converter.

        Returns
        -------
        bool:
            Whether the provided suffix is supported or not.
        """
        return suffix in self.supported_suffixes

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        """Transforms volumetric data into a zarr array.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.

        Returns
        -------
        list[DataSet]:
            List of datasets in internal format.
        """
        ...

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        """Transforms the segmentation data into a zarr array.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.

        Returns
        -------
        list[DataSet]:
            List of datasets in internal format.
        """
        ...

    async def collect_metadata(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        """Collects metadata from a file.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        internal_data: Data
            Reference to the internal representation of the output. It is
            going to be changed by this method.

        Returns
        -------
        list[DataSet]:
            List of datasets in internal format.
        """
        ...

    async def collect_annotations(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        """Collects annotations from a file.

        Parameters
        ----------
        input_path: Path
            Path to the transformation target.
        internal_data: Data
            Reference to the internal representation of the output. It is
            going to be changed by this method.

        Returns
        -------
        list[DataSet]:
            List of datasets in internal format.
        """
        ...
