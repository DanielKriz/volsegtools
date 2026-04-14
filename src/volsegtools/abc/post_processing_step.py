import abc

from volsegtools.abc import DataHandle


class PostProcessingStep(abc.ABC):
    @abc.abstractmethod
    async def execute(self, DataHandle) -> DataHandle: ...

    async def __call__(self, DataHandle) -> DataHandle:
        return await self.execute(DataHandle)
