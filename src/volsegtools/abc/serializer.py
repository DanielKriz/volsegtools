from pathlib import Path
from typing import List, Protocol


class Serializer(Protocol):
    """Serializes the provided array-like data into some data format."""

    async def serialize(self, data_set, output_path: Path) -> List[Path]: ...
