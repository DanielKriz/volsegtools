import abc


class PostConversionStep(abc.ABC):
    @abc.abstractmethod
    async def execute(
        self, volumes, segmentations, metadata, annotations
    ): ...

    async def __call__(
        self, volumes, segmentations, metadata, annotations
    ):
        return await self.execute(volumes, segmentations, metadata, annotations)
