from typing import Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage import Dataset


class PostProcessingStep(Protocol):
    async def execute(
        self,
        data_sets: list[Dataset],
        context: PipelineContext,
    ) -> list[Dataset]: ...

    async def __call__(
        self,
        data_sets: list[Dataset],
        context: PipelineContext,
    ) -> list[Dataset]:
        return await self.execute(data_sets, context)
