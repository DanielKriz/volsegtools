from pathlib import Path
from typing import List

from typing_extensions import Self

from volsegtools._downsampler.hierarchy_downsampling_strategy import (
    NullDownsamplingStrategy,
)
from volsegtools._model.working_store import WorkingStore
from volsegtools.abc import Converter, Downsampler
from volsegtools._preprocessor.processing_pipeline import ProcessingPipeline
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
        # self._downsampler: Downsampler | None = None
        self._downsampling_strategy: DownsamplingStrategy = NullDownsamplingStrategy
        self._post_processing_steps: List[PostProcessingStep] = []
        self._post_conversion_steps: List[PostConversionStep] = []
        self._serializer = None

    def set_segmentation_converter(self, converter: Converter) -> Self:
        self._segmentation_converter = converter
        return self

    def set_volume_converter(self, converter: Converter) -> Self:
        """Sets a converter that is going to be used by the resulting
        preprocessor.

        If this method is going to be called multimple times, it is going
        to override the previously set converter.
        """
        self._volume_converter = converter
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
        # if self._downsampler is None:
        #     raise RuntimeError("Downsampler was not set")

        if self._volume_converter is None and self._segmentation_converter is None:
            raise RuntimeError("Atleast one convertor has to be set")

        if self._serializer is None:
            raise RuntimeError("Serializer must be provided!")

        return ProcessingPipeline(
            downsampling_strategy=self._downsampling_strategy,
            volume_converter=self._volume_converter,
            segmentation_converter=self._segmentation_converter,
            post_processing_steps=self._post_processing_steps,
            post_conversion_steps=self._post_conversion_steps,
            serializer=self._serializer,
            work_dir=self._work_dir,
            output_dir=self._output_dir,
        )


def create_builder() -> ProcessingPipelineBuilder:
    return ProcessingPipelineBuilder()
