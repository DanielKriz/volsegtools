from pathlib import Path
from typing import List

from typing_extensions import Self

from volsegtools._converter.converter_map import ConverterMap
from volsegtools._downsampler.hierarchy_downsampling_strategy import (
    NullDownsamplingStrategy,
)
from volsegtools._model.working_store import WorkingStore
from volsegtools._processing.processing_pipeline import ProcessingPipeline

from volsegtools.abc import Converter, Downsampler
from volsegtools.abc.bundler import Bundler
from volsegtools.abc.downsampling_strategy import DownsamplingStrategy
from volsegtools.abc.post_conversion_step import PostConversionStep
from volsegtools.abc.post_processing_step import PostProcessingStep
from volsegtools.abc.serializer import Serializer


class ProcessingPipelineBuilder:
    """Allows fine-grained specification of the preprocessor."""

    def __init__(self) -> None:
        self._work_dir: Path | None = None
        self._output_dir: Path | None = None
        self._volume_converter: Converter | None = None
        self._segmentation_converter: Converter | None = None
        self._downsampling_strategy: DownsamplingStrategy = NullDownsamplingStrategy
        self._post_processing_steps: List[PostProcessingStep] = []
        self._post_conversion_steps: List[PostConversionStep] = []
        self._serializer = None
        self._volume_converter_map = ConverterMap()
        self._segmentation_converter_map = ConverterMap()
        self._bundler = None

    def _mend_suffixes(self, converter, suffixes=None, preserve_builtin=False):
        if preserve_builtin:
            suffixes = suffixes + converter.supported_suffixes

        if suffixes is None:
            suffixes = converter.supported_suffixes
        return suffixes


    def add_segmentation_converter(
        self,
        converter: Converter, 
        suffixes=None, 
        preserve_builtin=False
    ) -> Self:
        suffixes = self._mend_suffixes(converter, suffixes, preserve_builtin)
        self._segmentation_converter_map.set_converter(converter, suffixes)
        return self


    def add_volume_converter(
        self,
        converter: Converter, 
        suffixes=None, 
        preserve_builtin=False
    ) -> Self:
        suffixes = self._mend_suffixes(converter, suffixes, preserve_builtin)
        self._volume_converter_map.set_converter(converter, suffixes)
        return self


    def set_downsampling_strategy(self, strategy: DownsamplingStrategy) -> Self:
        """Sets a downsampler that is going to be used by the resulting
        preprocessor.

        If this method is going to be called multimple times, it is going
        to override the previously set downsampler.
        """
        self._downsampling_strategy = strategy
        return self


    def set_downsampler(self, downsampler: Downsampler) -> Self:
        """Sets a downsampler that is going to be used by the resulting
        preprocessor.

        If this method is going to be called multimple times, it is going
        to override the previously set downsampler.
        """
        self._downsampler = downsampler
        return self


    def set_add_post_conversion_step(self, step: PostConversionStep) -> Self:
        self._post_conversion_steps.append(step)
        return self


    def set_add_post_process_step(self, step: PostProcessingStep) -> Self:
        self._post_processing_steps.append(step)
        return self

    def set_bundler(self, bundler: Bundler) -> Self:
        self._bundler = bundler
        return self

    def set_serializer(self, serializer: Serializer) -> Self:
        self._serializer = serializer
        return self


    def set_work_dir(self, file_path: Path) -> Self:
        """Sets the working directory of the processor.

        It is going to be added to the search path for source files of the
        preprocessor. Also, the output of the preprocessor is going to be
        saved at this location.
        """
        # FIXME: this shouldn't be necessary
        WorkingStore(file_path)
        self._work_dir = file_path
        return self


    def set_output_dir(self, file_path: Path) -> Self:
        self._output_dir = file_path
        return self


    def build(self) -> ProcessingPipeline:
        """Builds the resulting preprocessor."""

        if self._volume_converter is None and self._segmentation_converter is None:
            raise RuntimeError("Atleast one convertor has to be set")

        if self._serializer is None:
            raise RuntimeError("Serializer must be provided!")

        return ProcessingPipeline(
            downsampling_strategy=self._downsampling_strategy,
            volume_converter_map=self._volume_converter_map,
            segmentation_converter_map=self._segmentation_converter_map,
            post_processing_steps=self._post_processing_steps,
            post_conversion_steps=self._post_conversion_steps,
            serializer=self._serializer,
            bundler=self._bundler,
            work_dir=self._work_dir,
            output_dir=self._output_dir,
        )


def create_builder() -> ProcessingPipelineBuilder:
    return ProcessingPipelineBuilder()
