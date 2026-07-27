from typing import Any, Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage import DataSet


class PostConversionStep(Protocol):
    async def execute(
        self,
        volumes: list[DataSet],
        segmentations: list[DataSet],
        metadata: list[Any],
        annotations: list[Any],
        context: PipelineContext,
    ) -> list[DataSet]: ...

    async def __call__(
        self,
        volumes: list[DataSet],
        segmentations: list[DataSet],
        metadata: list[Any],
        annotations: list[Any],
        context: PipelineContext,
    ) -> list[DataSet]:
        return await self.execute(volumes, segmentations, metadata, annotations, context)
