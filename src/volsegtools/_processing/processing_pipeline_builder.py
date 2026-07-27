from pathlib import Path
from typing import Self

import collections

import zarr.errors

from volsegtools._conversion.converter_map import ConverterMap
from volsegtools._core import Bytes, DataKind, WorkingStore
from volsegtools._downsampling.null import Null
from volsegtools._processing.processing_pipeline import ProcessingPipeline
from volsegtools.abc import (
    Bundler,
    Converter,
    DownsamplingStrategy,
    PostConversionStep,
    PostProcessingStep,
    Serializer,
)


class ProcessingPipelineBuilder:
    """Allows fine-grained specification of the preprocessor."""

    def __init__(self) -> None:
        self._work_dir: Path | None = None
        self._output_dir: Path | None = None
        self._volume_converter: Converter | None = None
        self._segmentation_converter: Converter | None = None
        self._downsampling_strategy: DownsamplingStrategy = Null()
        self._post_processing_steps: list[PostProcessingStep] = []
        self._post_conversion_steps: list[PostConversionStep] = []
        self._serializer_map = collections.defaultdict(None)
        self._volume_converter_map = ConverterMap()
        self._segmentation_converter_map = ConverterMap()
        self._bundler = None
        self._keep_original = False
        self._threshold = ProcessingPipeline.DEFAULT_SIZE_THRESHOLD

    def _mend_suffixes(self, converter, suffixes=None, preserve_builtin=False):
        if preserve_builtin:
            suffixes = suffixes + converter.supported_suffixes

        if suffixes is None:
            suffixes = converter.supported_suffixes
        return suffixes

    def add_segmentation_converter(
        self, converter: Converter, suffixes=None, preserve_builtin=False
    ) -> Self:
        suffixes = self._mend_suffixes(converter, suffixes, preserve_builtin)
        self._segmentation_converter_map.set_converter(converter, suffixes)
        return self

    def add_volume_converter(
        self, converter: Converter, suffixes=None, preserve_builtin=False
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

    def add_post_conversion_step(self, step: PostConversionStep) -> Self:
        self._post_conversion_steps.append(step)
        return self

    def add_post_process_step(self, step: PostProcessingStep) -> Self:
        self._post_processing_steps.append(step)
        return self

    def set_bundler(self, bundler: Bundler) -> Self:
        self._bundler = bundler
        return self

    def set_serializer(self, kind: DataKind, serializer: Serializer) -> Self:
        self._serializer_map[kind] = serializer
        return self

    def set_work_dir(self, file_path: Path) -> Self:
        """Sets the working directory of the processor.

        It is going to be added to the search path for source files of the
        preprocessor. Also, the output of the preprocessor is going to be
        saved at this location.
        """
        # NOTE: Currently a work-around should be removed together with
        # working store.
        try:
            WorkingStore(file_path)
        except zarr.errors.ContainsGroupError:
            print("Working store already data from previous processing")
            print("You might want to add '--overwrite-tmp' to overwrite them")
            raise RuntimeError("Working store already initialized") from None

        self._work_dir = file_path
        return self

    def keep_original(self, value: bool) -> Self:
        self._keep_original = value
        return self

    def set_output_dir(self, file_path: Path) -> Self:
        self._output_dir = file_path
        return self

    def set_downsampling_size_threshold(self, threshold: Bytes) -> Self:
        self._threshold = threshold
        return self

    def build(self) -> ProcessingPipeline:
        """Builds the resulting preprocessor."""

        if all(x is None for x in self._serializer_map.values()):
            raise RuntimeError("Atleast one serializer must set")

        return ProcessingPipeline(
            downsampling_strategy=self._downsampling_strategy,
            volume_converter_map=self._volume_converter_map,
            segmentation_converter_map=self._segmentation_converter_map,
            post_processing_steps=self._post_processing_steps,
            post_conversion_steps=self._post_conversion_steps,
            volume_serializer=self._serializer_map[DataKind.VOLUME],
            segmentation_mask_serializer=self._serializer_map[DataKind.SEGMENTATION_MASK],
            segmentation_volume_serializer=self._serializer_map[
                DataKind.SEGMENTATION_VOLUME
            ],
            segmentation_mesh_serializer=self._serializer_map[DataKind.SEGMENTATION_MESH],
            bundler=self._bundler,
            work_dir=self._work_dir,
            output_dir=self._output_dir,
            keep_original=self._keep_original,
            size_threshold=self._threshold,
        )


def create_builder() -> ProcessingPipelineBuilder:
    return ProcessingPipelineBuilder()
