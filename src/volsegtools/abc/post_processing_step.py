from typing import List, Any, Protocol

from volsegtools._model import PipelineContext

class PostProcessingStep(Protocol):
    async def execute(
        self,
        data_sets: List[Any],
        context: PipelineContext,
    ) -> List[Any]: ...

    async def __call__(
        self,
        data_sets: List[Any],
        context: PipelineContext,
    ) -> List[Any]:
        return await self.execute(data_sets, context)
