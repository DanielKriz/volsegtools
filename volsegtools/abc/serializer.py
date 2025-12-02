import abc
from pathlib import Path

class Serializer(abc.ABC):
    """Serializes the provided array-like data into some data format."""

    @staticmethod
    @abc.abstractmethod
    async def serialize(data, output_path: Path) -> None:
        ...
