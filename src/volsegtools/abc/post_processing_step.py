import abc

from typing import List, Any


class PostProcessingStep(abc.ABC):
    @abc.abstractmethod
    async def execute(self, data_sets: List[Any]) -> List[Any]: ...

    async def __call__(self, data_sets: List[Any]) -> List[Any]:
        return await self.execute(data_sets)
