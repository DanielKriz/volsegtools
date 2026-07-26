from pathlib import Path
from typing import Protocol

from volsegtools._model import PipelineContext


class Serializer(Protocol):
    """Serializes the provided array-like data into some data format."""

    async def serialize(
        self,
        data_set,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]: ...
