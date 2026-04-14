import abc

from volsegtools.abc import DataHandle


class PostConversionStep(abc.ABC):
    @abc.abstractmethod
    async def execute(
        self, volumes, segmentations, metadata, annotations
    ) -> DataHandle: ...

    async def __call__(
        self, volumes, segmentations, metadata, annotations
    ) -> DataHandle:
        return await self.execute(volumes, segmentations, metadata, annotations)
