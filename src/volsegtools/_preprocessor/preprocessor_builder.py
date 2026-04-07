from pathlib import Path
from typing import List

from typing_extensions import Self

from volsegtools.abc import Converter, Downsampler
from volsegtools._preprocessor import Preprocessor


class PreprocessorBuilder:
    """Allows fine-grained specification of the preprocessor."""

    def __init__(self) -> None:
        self._work_dir: Path | None = None
        self._output_dir: Path | None = None
        self._volume_sources: List[Path] = []
        self._segmentation_sources: List[Path] = []
        self._annotations_sources: List[Path] = []
        self._metadata_sources: List[Path] = []
        self._converter: Converter | None = None
        self._downsampler: Downsampler | None = None
        # Currently, we only support a single preprocessor, after that we
        # could add support for generic preprocessor
        # self._preprocessor_type: Optional[Preprocessor] = None

    def set_converter(self, converter: Converter) -> Self:
        """Sets a converter that is going to be used by the resulting
        preprocessor.

        If this method is going to be called multimple times, it is going
        to override the previously set converter.
        """
        self._converter = converter
        return self

    def set_downsampler(self, downsampler: Downsampler) -> Self:
        """Sets a downsampler that is going to be used by the resulting
        preprocessor.

        If this method is going to be called multimple times, it is going
        to override the previously set downsampler.
        """
        self._downsampler = downsampler
        return self

    def add_volume_src_file(self, file_path: Path) -> Self:
        """Adds the source file for volumetric data.

        It should be used in cases where there are multiple files and
        set_input_file cannot be used.
        """
        self._volume_sources.append(file_path)
        return self

    def add_segmentation_src_file(self, file_path: Path) -> Self:
        """Sets the source file for annotations.

        It should be used in cases where there are multiple files and
        set_input_file cannot be used.
        """
        self._segmentation_sources.append(file_path)
        return self

    def add_metadata_src_file(self, file_path: Path) -> Self:
        """Adds the source file for metadata.

        It should be used in cases where there are multiple files and
        set_input_file cannot be used.
        """
        return self

    def add_annotations_src_file(self, file_path: Path) -> Self:
        """Adds the source file for annotations.

        It should be used in cases where there are multiple files and
        set_input_file cannot be used.
        """
        return self

    def set_work_dir(self, file_path: Path) -> Self:
        """Sets the working directory of the processor.

        It is going to be added to the search path for source files of the
        preprocessor. Also, the output of the preprocessor is going to be
        saved at this location.
        """
        return self

    def set_output_dir(self, file_path: Path) -> Self:
        self._output_dir = file_path
        return self

    def build(self) -> Preprocessor:
        """Builds the resulting preprocessor."""
        if self._downsampler is None:
            raise RuntimeError("Downsampler was not set")

        if self._converter is None:
            raise RuntimeError("Converter was not set")

        return Preprocessor(
            self._downsampler,
            self._converter,
            self._volume_sources,
            self._segmentation_sources,
            self._metadata_sources,
            self._annotations_sources,
            self._work_dir,
            self._output_dir,
        )
