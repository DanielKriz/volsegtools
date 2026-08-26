from pathlib import Path
from typing import Self

from volsegtools._conversion.converter_map import ConverterMap
from volsegtools._core import Bytes, DataKind
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
        self._downsampling_strategy: DownsamplingStrategy = Null()
        self._post_processing_steps: list[PostProcessingStep] = []
        self._post_conversion_steps: list[PostConversionStep] = []
        self._serializer_map: dict[DataKind, Serializer] = {}
        self._volume_converter_map = ConverterMap()
        self._segmentation_converter_map = ConverterMap()
        self._bundler = None
        self._keep_original = False
        self._threshold = ProcessingPipeline.DEFAULT_SIZE_THRESHOLD

    def _mend_suffixes(
        self,
        converter: Converter,
        suffixes: list[str] | None = None,
        preserve_builtin: bool = False,
    ):
        """Mends suffixes to a single group for lookup.

        Converters are usually bound to a single file suffix, with this we
        can mend those groups together.

        Parameters
        ----------
        converter: Converter
            The converter for which we want to med the suffixes.
        suffixes: list[str]
            The list of additional suffixes.
        preserve_builtin: bool, optional
            Whether we want to use the converter's default suffixes.
        """
        if suffixes is None:
            suffixes = converter.supported_suffixes
        elif preserve_builtin:
            suffixes = suffixes + converter.supported_suffixes

        return suffixes

    def add_segmentation_converter(
        self,
        converter: Converter,
        suffixes: list[str] | None = None,
        preserve_builtin: bool = False,
    ) -> Self:
        """Add additional segmentation converter to the pipeline.

        There has to be atleast one volume or segmentation converter for a
        pipeline to be valid (for segmentation see
        :meth:`~volsegtools.ProcessingPipelineBuilder.add_volume_converter).

        Parameters
        ----------
        converter: Converter
            The converter which we want to add.
        suffixes: list[str]
            The list of suffixes for which we should use this converter.
        preserve_builtin: bool, optional
            Whether we want to use the converter's default suffixes.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        suffixes = self._mend_suffixes(converter, suffixes, preserve_builtin)
        self._segmentation_converter_map.set_converter(converter, suffixes)
        return self

    def add_volume_converter(
        self,
        converter: Converter,
        suffixes: list[str] | None = None,
        preserve_builtin: bool = False,
    ) -> Self:
        """Add additional volume converter to the pipeline.

        There has to be atleast one volume or segmentation converter for a
        pipeline to be valid (for segmentation see
        :meth:`~volsegtools.ProcessingPipelineBuilder.add_segmentation_converter).

        Parameters
        ----------
        converter: Converter
            The converter which we want to add.
        suffixes: list[str]
            The list of suffixes for which we should use this converter.
        preserve_builtin: bool, optional
            Whether we want to use the converter's default suffixes.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        suffixes = self._mend_suffixes(converter, suffixes, preserve_builtin)
        self._volume_converter_map.set_converter(converter, suffixes)
        return self

    def set_downsampling_strategy(self, strategy: DownsamplingStrategy) -> Self:
        """Sets a downsampler that is going to be used by the resulting
        preprocessor.

        If this method is going to be called multimple times, it is going
        to override the previously set downsampler.

        This stage is optional.

        Parameters
        ----------
        strategy: DownsamplingStrategy
            Strategy which should be used by this pipeline.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        self._downsampling_strategy = strategy
        return self

    def add_post_conversion_step(self, step: PostConversionStep) -> Self:
        """Adds Post-Conversion step to the pipeline.

        There is not checking for duplication, if it is going to be called
        several times with the same instance, then it is going to be used by
        the pipeline several times.

        This stage is optional.

        Parameters
        ----------
        step: PostConversionStep
            The post-conversion step that we want to add to the pipeline.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        self._post_conversion_steps.append(step)
        return self

    def add_post_process_step(self, step: PostProcessingStep) -> Self:
        """Adds Post-Processing step to the pipeline.

        There is not checking for duplication, if it is going to be called
        several times with the same instance, then it is going to be used by
        the pipeline several times.

        This stage is optional.

        Parameters
        ----------
        step: PostProcessingStep
            The post-processing step that we want to add to the pipeline.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        self._post_processing_steps.append(step)
        return self

    def set_bundler(self, bundler: Bundler) -> Self:
        """Set the bundler that should be used by the pipeline.

        This stage is optional.

        Parameters
        ----------
        bundler: Bundler
            The builder that should be used by the pipeline.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        self._bundler = bundler
        return self

    def set_serializer(self, kind: DataKind, serializer: Serializer) -> Self:
        """Set the serializer for a data kind that should be used by the
        pipeline.

        This stage is required. Atleast for a single data kind the serializer
        have to be set.

        Calling this method again for the same data kind is going to override
        the previous one.

        Parameters
        ----------
        kind: DataKind
            The kind of the data for which we are setting the serializer.
        serializer: serializer
            The serializer that the pipeline should used for give data kind.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        self._serializer_map[kind] = serializer
        return self

    def set_work_dir(self, file_path: Path) -> Self:
        """Sets the working directory of the processor.

        This directory is going to be used for storing intermediate file,
        namely zarr archive.

        Parameters
        ----------
        file_path: Path
            Path to the working directory.

        Raises
        ------
        RuntimeError:
            If the provide file path is not a directory.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        if not file_path.is_dir:
            raise RuntimeError("Output directory has to be a directory!")

        self._work_dir = file_path
        return self

    def keep_original(self, value: bool) -> Self:
        """Set that the original resolution should be part of the output.

        Parameters
        ----------
        value: bool
            Flag denoting whether we should keep the original original.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        self._keep_original = value
        return self

    def set_output_dir(self, file_path: Path) -> Self:
        """Sets the directory into which the pipeline is going to write output.

        Output is in this case all outputs of the serializer and bundler
        stages.

        Parameters
        ----------
        file_path: Path
            Path to the output directory.

        Raises
        ------
        RuntimeError:
            If the provide file path is not a directory.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        if not file_path.is_dir:
            raise RuntimeError("Output directory has to be a directory!")

        self._output_dir = file_path
        return self

    def set_downsampling_size_threshold(self, threshold: Bytes) -> Self:
        """Sets the size threshold for accepting downsampled resolutions.

        Parameters
        ----------
        threshold: Bytes
            Positive threshold for the resolution size.

        Raises
        ------
        RuntimeError:
            If the threshold is smaller than 0.

        Returns
        -------
        Self:
            Reference to this builder.
        """
        if threshold <= 0:
            raise RuntimeError("Size threshold has be bigger than 0!")

        self._threshold = threshold
        return self

    def build(self) -> ProcessingPipeline:
        """Builds the resulting processing pipeline.

        Raises
        ------
        RuntimeError:
            If volume nor segmentation converter is set.
            If no serializer is set.

        Returns
        -------
        ProcessingPipepline:
            Instance of the processing pipeline.
        """

        if (
            self._segmentation_converter_map.is_empty()
            and self._volume_converter_map.is_empty()
        ):
            raise RuntimeError("segmentation or volume converter has to be set!")

        if all(x is None for x in self._serializer_map.values()):
            raise RuntimeError("Atleast one serializer must set")

        return ProcessingPipeline(
            downsampling_strategy=self._downsampling_strategy,
            volume_converter_map=self._volume_converter_map,
            segmentation_converter_map=self._segmentation_converter_map,
            post_processing_steps=self._post_processing_steps,
            post_conversion_steps=self._post_conversion_steps,
            volume_serializer=self._serializer_map.get(DataKind.VOLUME),
            segmentation_mask_serializer=self._serializer_map.get(
                DataKind.SEGMENTATION_MASK
            ),
            segmentation_volume_serializer=self._serializer_map.get(
                DataKind.SEGMENTATION_VOLUME
            ),
            segmentation_mesh_serializer=self._serializer_map.get(
                DataKind.SEGMENTATION_MESH
            ),
            bundler=self._bundler,
            work_dir=self._work_dir,
            output_dir=self._output_dir,
            keep_original=self._keep_original,
            size_threshold=self._threshold,
        )


def create_builder() -> ProcessingPipelineBuilder:
    """Creates a processing pipeline builder.

    It is just a convenience function.

    Returns
    -------
    Self:
        Reference to this builder.
    """
    return ProcessingPipelineBuilder()
