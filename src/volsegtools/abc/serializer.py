import abc
from pathlib import Path

from volsegtools.abc.data_handle import DataHandle


class Serializer(abc.ABC):
    """Serializes the provided array-like data into some data format."""

    @staticmethod
    @abc.abstractmethod
    async def serialize(data: DataHandle, output_path: Path) -> None: ...
