from pathlib import Path
from typing import Any, Protocol

from volsegtools._storage import DataSet


class ProcessingPipeline(Protocol):
    """Processes given data set."""

    class Progress:
        percent_done: int
        current_file: Path

    async def convert_volumes(self, paths: list[Path]) -> list[DataSet]:
        """Converts collection of volumes into standardized data handles."""
        ...

    async def convert_segmentations(self, paths: list[Path]) -> list[DataSet]:
        """Converts collection of segmentations into a standardized data
        handles."""
        ...

    async def collect_metadata(self, paths: list[Path]) -> list[Any]:
        """Collects metadata from collection of files."""
        ...

    async def collect_annotation(self, paths: list[Path]) -> list[Any]:
        """Collects annotations from collection of files."""
        ...

    async def apply_post_conversion_steps(
        self, volumes, segmentations, metadata, annotations
    ):
        """Does some processing of the converted data.

        Some downsampling algorithms might need some additional processing or
        data collection. There also could be some formats that store metadata
        externally in some other data or serialization format.

        For these cases it is possible to do additional processing steps.
        """
        ...

    async def downsample(self, data_set: DataSet) -> list[Any]:
        """Downsamples given data."""
        ...

    async def apply_post_processing_steps(
        self,
        data_set: DataSet,
    ) -> list[Any]:
        """Applies post processing steps on the downsampled data.

        Some downsampling methods are known to produce some artifacts that can
        be mitigated by additional processing steps. For these cases it is
        possible to use this method.
        """
        ...

    async def serialize(self, data_set: DataSet) -> list[Path]:
        """Serializes given data into files."""
        ...

    async def process(
        self,
        volumes: list[Path],
        segmentations: list[Path],
        metadata: list[Path],
        annotations: list[Path],
    ) -> list[Path]:
        """Processes given data using this processing pipeline."""
        ...

    def sync_process(
        self,
        volumes: list[Path],
        segmentations: list[Path] | None = None,
        metadata: list[Path] | None = None,
        annotations: list[Path] | None = None,
    ) -> list[Path]:
        """Processes given data in synchronous manner."""
        ...
