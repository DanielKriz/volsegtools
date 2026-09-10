from typing import Any, Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage import Dataset


class PostConversionStep(Protocol):
    async def execute(
        self,
        volumes: list[Dataset],
        segmentations: list[Dataset],
        metadata: list[Any],
        annotations: list[Any],
        context: PipelineContext,
    ) -> list[Dataset]: ...

    async def __call__(
        self,
        volumes: list[Dataset],
        segmentations: list[Dataset],
        metadata: list[Any],
        annotations: list[Any],
        context: PipelineContext,
    ) -> list[Dataset]:
        return await self.execute(volumes, segmentations, metadata, annotations, context)
