from typing import Any, Protocol

from volsegtools._model import PipelineContext


class PostProcessingStep(Protocol):
    async def execute(
        self,
        data_sets: list[Any],
        context: PipelineContext,
    ) -> list[Any]: ...

    async def __call__(
        self,
        data_sets: list[Any],
        context: PipelineContext,
    ) -> list[Any]:
        return await self.execute(data_sets, context)
