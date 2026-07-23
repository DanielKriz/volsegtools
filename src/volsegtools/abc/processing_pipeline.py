import abc
from typing import Any, List, Sequence
from pathlib import Path


class ProcessingPipeline(abc.ABC):
    """Processes given data set."""

    class Progress:
        percent_done: int
        current_file: Path

    @abc.abstractmethod
    async def convert_volumes(self, paths: List[Path]) -> Any:
        """Converts collection of volumes into standardized data handles."""
        ...

    @abc.abstractmethod
    async def convert_segmentations(self, paths: List[Path]) -> Any:
        """Converts collection of segmentations into a standardized data
        handles."""
        ...

    @abc.abstractmethod
    async def collect_metadata(self, paths: List[Path]) -> Any:
        """Collects metadata from collection of files."""
        ...

    @abc.abstractmethod
    async def collect_annotation(self, paths: List[Path]) -> Any:
        """Collects annotations from collection of files."""
        ...

    @abc.abstractmethod
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

    @abc.abstractmethod
    async def downsample(self, data_set: Any) -> List[Any]:
        """Downsamples given data."""
        ...

    @abc.abstractmethod
    async def apply_post_processing_steps(
        self, data_set: Any,
    ) -> Sequence[Any]:
        """Applies post processing steps on the downsampled data.

        Some downsampling methods are known to produce some artifacts that can
        be mitigated by additional processing steps. For these cases it is
        possible to use this method.
        """
        ...

    @abc.abstractmethod
    async def serialize(self, data_set) -> List[Path]:
        """Serializes given data into files."""
        ...

    @abc.abstractmethod
    async def process(
        self,
        volumes: List[Path],
        segmentations: List[Path],
        metadata: List[Path],
        annotations: List[Path],
    ) -> List[Path]:
        """Processes given data using this processing pipeline."""
        ...

    @abc.abstractmethod
    def sync_process(
        self,
        volumes: List[Path],
        segmentations: List[Path] = [],
        metadata: List[Path] = [],
        annotations: List[Path] = [],
    ) -> List[Path]:
        """Processes given data in synchronous manner."""
        ...
