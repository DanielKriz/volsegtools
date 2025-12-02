from typing import Any

import abc

class Preprocessor(abc.ABC):
    """Processes"""
    @abc.abstractmethod
    async def transform_volume(self):
        pass

    @abc.abstractmethod
    async def transform_segmentation(self):
        pass

    @abc.abstractmethod
    async def collect_metadata(self):
        pass

    @abc.abstractmethod
    async def collect_annotation(self):
        pass

    @abc.abstractmethod
    async def downsample(self):
        pass

    @abc.abstractmethod
    async def get_results(self) -> Any:
        pass

    @abc.abstractmethod
    def preprocess(self):
        pass

