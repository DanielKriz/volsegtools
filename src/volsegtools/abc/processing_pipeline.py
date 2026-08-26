from pathlib import Path
from typing import Any, Protocol

from volsegtools._storage import DataSet


class ProcessingPipeline(Protocol):
    """Processes given dataset."""

    async def convert_volumes(self, paths: list[Path]) -> list[DataSet]:
        """Converts list of volume files into a list of datasets.

        Parameters
        ----------
        paths: list[Path]
            List of paths to files containing volumetric data.

        Returns
        -------
        list[DataSet]:
            List of datasets containing volumetric data.
        """
        ...

    async def convert_segmentations(self, paths: list[Path]) -> list[DataSet]:
        """Converts list of segmentation files into a list of datasets.

        Parameters
        ----------
        paths: list[Path]
            List of paths to files containing segmentations.

        Returns
        -------
        list[DataSet]:
            List of datasets containing segmentation data.
        """
        ...

    async def collect_metadata(self, paths: list[Path]) -> list[Any]:
        """Collects metadata from a list of files.

        It is expected that the metadata is then going to be incorporated to
        datasets gotten from other files in the post-conversion step.

        Parameters
        ----------
        paths: list[Path]
            List of paths to files containing metadata.

        Returns
        -------
        list[Any]:
            List of any data that should be passed to post-conversion step.
        """
        ...

    async def collect_annotation(self, paths: list[Path]) -> list[Any]:
        """Collects annotations from collection of files.

        It is expected that the annotations are then going to be incorporated
        to datasets gotten from other files in the post-conversion step.

        Parameters
        ----------
        paths: list[Path]
            List of paths to files containing annotations.

        Returns
        -------
        list[Any]:
            List of any data that should be passed to post-conversion step.

        """
        ...

    async def apply_post_conversion_steps(
        self,
        volumes: list[DataSet],
        segmentations: list[DataSet],
        metadata: list[Any],
        annotations: list[Any],
    ) -> None:
        """Does some processing of the converted data.

        Some downsampling algorithms might need some additional processing or
        data collection. There also could be some formats that store metadata
        externally in some other data or serialization format.

        For these cases it is possible to do additional processing steps.

        Parameters
        ----------
        volumes: list[DataSet]
            List of datasets containing volumetric data.
        segmentations: list[DataSet]
            List of datasets containing segmentations.
        metadata: list[Any]
            List of arbitrary data containing metadata.
        annotations: list[Any]
            List of arbitrary data containing annotations.
        """
        ...

    async def downsample(self, data_set: DataSet) -> list[DataSet]:
        """Downsamples given data.

        This basically creates the so-called resolution pyramid of the data.

        Parameters
        ----------
        data_set: DataSet
            Dataset in the original resolution.

        Returns
        -------
        list[DataSet]
            List of datasets, each in different resolution.
        """
        ...

    async def apply_post_processing_steps(
        self,
        data_set: list[DataSet],
    ) -> list[DataSet]:
        """Applies post processing steps on the downsampled data.

        Some downsampling methods are known to produce some artifacts that can
        be mitigated by additional processing steps. For these cases it is
        possible to use this method.

        Parameters
        ----------
        data_set: list[DataSet]
            List of original datasets.

        Returns
        -------
        list[Any]:
            List of processed datasets.
        """
        ...

    # TODO: Path is not enough, we need some additional information further in
    # the pipeline. Attach some metadata to the path.
    async def serialize(self, data_set: DataSet) -> list[Path]:
        """Serializes given data into files.

        There should be a serializer for each data kind that should be used for
        serialization of said kind.

        Parameters
        ----------
        data_set: DataSet
            Dataset that should be serialized.

        Returns
        -------
        list[Path]:
            List of paths to the serialized files.
        """
        ...

    async def bundle(self, files: list[Path]) -> list[Path]:
        """Bundles serialized files into some kind of archive.

        Parameters
        ----------
        files: list[Path]
            List of paths to serialized files.

        Returns
        -------
        list[Path]:
            List of bundled files.

        """
        ...

    async def process(
        self,
        volumes: list[Path],
        segmentations: list[Path],
        metadata: list[Path],
        annotations: list[Path],
    ) -> list[Path]:
        """Processes given data using this processing pipeline.

        Parameters
        ----------
        volumes: list[Path]
            List of paths to files containing volumetric data.
        segmentations: list[Path]
            List of paths to files containing segmentations.
        metadata: list[Path]
            List of paths to files containing metadata.
        annotations: list[Path]
            List of paths to files containing annotations.

        Returns
        -------
        list[Path]:
            List of resulting files, both serialized and bundled into some
            archive.
        """
        ...

    def sync_process(
        self,
        volumes: list[Path],
        segmentations: list[Path] | None = None,
        metadata: list[Path] | None = None,
        annotations: list[Path] | None = None,
    ) -> list[Path]:
        """Processes given data in synchronous manner.

        Not everything has to be asynchronnous, so this is a convenience
        wrapper.

        For description of parameters see:
        :meth:`~volsegtools.abc.ProcessingPipeline.process`.

        """
        ...
