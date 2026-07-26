from pathlib import Path
from typing import Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage import DataSet


class Serializer(Protocol):
    """Serializes the provided array-like data into some data format."""

    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]: ...
