import abc
from pathlib import Path
from typing import List


class Serializer(abc.ABC):
    """Serializes the provided array-like data into some data format."""

    @abc.abstractmethod
    async def serialize(self, data_set, output_path: Path) -> List[Path]: ...
