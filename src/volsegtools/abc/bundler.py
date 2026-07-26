from typing import List, Protocol
from pathlib import Path

from volsegtools._model import PipelineContext

class Bundler(Protocol):
    """Bundles a collection of data sets into an another artifact.

    For some formats and workflows it might be beneficial to return mutliple
    artifacts, not just one.
    """

    def bundle(
        self,
        data_paths: List[Path],
        output_path: Path,
        context: PipelineContext,
    ) -> List[Path]:
        """Bundles provided files into an another artifact.

        Parameters
        ----------
        data_paths : List[Path]
            List of files that should be bundled together.
        output_path: Path
            Path to which should the result be stored.

        Returns
        -------
        List[Path]
            List of resulting artifacts.
        """
        ...
