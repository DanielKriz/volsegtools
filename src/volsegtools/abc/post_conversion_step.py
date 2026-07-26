from typing import Protocol

from volsegtools._model import PipelineContext


class PostConversionStep(Protocol):
    async def execute(
        self,
        volumes,
        segmentations,
        metadata,
        annotations,
        context: PipelineContext,
    ): ...

    async def __call__(
        self,
        volumes,
        segmentations,
        metadata,
        annotations,
        context: PipelineContext,
    ):
        return await self.execute(
            volumes, segmentations, metadata, annotations, context
        )
