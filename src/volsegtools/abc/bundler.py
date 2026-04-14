import abc
from typing import List
from pathlib import Path


class Bundler(abc.ABC):
    """Bundles a collection of data sets into a single artifact"""

    @abc.abstractmethod
    def bundle(self, data_paths: List[Path], output_path: Path) -> List[Path]: ...
