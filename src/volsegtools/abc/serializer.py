import abc
from pathlib import Path
from typing import List

from volsegtools.abc.data_handle import DataHandle


class Serializer(abc.ABC):
    """Serializes the provided array-like data into some data format."""

    @staticmethod
    @abc.abstractmethod
    async def serialize(data_set, output_path: Path) -> List[Path]: ...


class SerializerOld(abc.ABC):
    """Serializes the provided array-like data into some data format."""

    @staticmethod
    @abc.abstractmethod
    async def serialize(data: DataHandle, output_path: Path) -> List[Path]: ...
