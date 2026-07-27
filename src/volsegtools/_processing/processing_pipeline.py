from pathlib import Path

import asyncio
import itertools
import logging

from volsegtools._conversion.converter_map import ConverterMap
from volsegtools._core import Bytes, DataKind, Timer, Vector3, WorkingStore
from volsegtools._downsampling.null import Null
from volsegtools._model import (
    PipelineStageKind,
    PipelineState,
    PipelineStateManager,
)
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import DataSet
from volsegtools.abc import (
    Bundler,
    PostConversionStep,
    PostProcessingStep,
    ProcessingPipeline,
    Serializer,
)

vst_logger = logging.getLogger("volsegtools")


def _flatten(list_of_lists: list[list]) -> list:
    # Source - https://stackoverflow.com/a/952952
    return [x for xs in list_of_lists for x in xs]


class ProcessingPipeline(ProcessingPipeline):
    DEFAULT_WORK_DIR = Path(".vst_work_dir")
    DEFAULT_SIZE_THRESHOLD = Bytes("5MiB")

    # It is safe to ignore the B008 error here, because the Null downsampling
    # strategy does not contain any state. Thus, it is safe to share it between
    # instances.
    def __init__(
        self,
        downsampling_strategy=Null(),  # noqa: B008
        volume_converter_map: ConverterMap | None = None,
        segmentation_converter_map: ConverterMap | None = None,
        volume_serializer: Serializer | None = None,
        segmentation_mask_serializer: Serializer | None = None,
        segmentation_volume_serializer: Serializer | None = None,
        segmentation_mesh_serializer: Serializer | None = None,
        post_processing_steps: list[PostProcessingStep] | None = None,
        post_conversion_steps: list[PostConversionStep] | None = None,
        bundler: Bundler | None = None,
        work_dir: Path | None = None,
        output_dir: Path | None = None,
        keep_original: bool = False,
        size_threshold: int = DEFAULT_SIZE_THRESHOLD,
    ):
        # The conversion and bundling are required stages
        if post_conversion_steps is None:
            post_conversion_steps = []
        if post_processing_steps is None:
            post_processing_steps = []
        self._downsampling_strategy = downsampling_strategy

        self._volume_converter_map = volume_converter_map
        self._segmentation_converter_map = segmentation_converter_map

        self._output_dir = output_dir if output_dir is not None else Path()

        self._serializer_map = {
            DataKind.VOLUME: volume_serializer,
            DataKind.SEGMENTATION_MASK: segmentation_mask_serializer,
            DataKind.SEGMENTATION_VOLUME: segmentation_volume_serializer,
            DataKind.SEGMENTATION_MESH: segmentation_mesh_serializer,
        }

        if work_dir is None:
            self._work_dir = ProcessingPipeline.DEFAULT_WORK_DIR
        else:
            self._work_dir = work_dir
        self.working_store = WorkingStore(work_dir)

        self._post_processing_steps = post_processing_steps
        self._post_conversion_steps = post_conversion_steps
        self._bundler = bundler

        self._keep_original = keep_original

        self._callbacks = []

        self._state = PipelineState(
            current_stage=PipelineStageKind.NOT_STARTED,
            msg="The pipeline has not yet started",
        )

        self.state__ = PipelineStateManager(
            self,
            PipelineState(
                current_stage=PipelineStageKind.NOT_STARTED,
                msg="The pipeline has not yet started",
            ),
        )

        self.context = PipelineContext(
            timer=Timer(),
            working_store=self.working_store,
            output_dir=self._output_dir,
            state=self.state__,
            size_threshold=size_threshold,
        )

    @property
    def keep_original(self) -> bool:
        return self._keep_original

    @staticmethod
    def pipeline_stage(kind: PipelineStageKind | str):
        def inner(func):
            def wrapper(self, *args, **kwargs):
                vst_logger.info(kind)
                self.context.timer.push_stage(str(kind))
                self._state.current_stage = PipelineStageKind(kind)

                for cb in self._callbacks:
                    cb(self._state)

                return func(self, *args, **kwargs)

            return wrapper

        return inner

    @property
    def state(self):
        return self._state

    def add_state_change_callback(self, cb):
        self._callbacks.append(cb)

    @property
    def started(self):
        return self._state.current_stage != PipelineStageKind.NOT_STARTED

    @property
    def done(self):
        return self._state.current_stage == PipelineStageKind.FINISHED

    def sync_process(
        self,
        volumes: list[Path] | None = None,
        segmentations: list[Path] | None = None,
        metadata: list[Path] | None = None,
        annotations: list[Path] | None = None,
    ) -> list[Path]:
        if annotations is None:
            annotations = []
        if metadata is None:
            metadata = []
        if segmentations is None:
            segmentations = []
        if volumes is None:
            volumes = []
        return asyncio.run(self.process(volumes, segmentations, metadata, annotations))

    async def process(
        self,
        volumes: list[Path] | None = None,
        segmentations: list[Path] | None = None,
        metadata: list[Path] | None = None,
        annotations: list[Path] | None = None,
    ) -> list[Path]:
        if annotations is None:
            annotations = []
        if metadata is None:
            metadata = []
        if segmentations is None:
            segmentations = []
        if volumes is None:
            volumes = []
        converted_volumes = await self.convert_volumes(volumes)
        converted_segmentations = await self.convert_segmentations(segmentations)
        collected_metadata = await self.collect_metadata(metadata)
        collected_annotations = await self.collect_annotation(annotations)

        if self._post_conversion_steps != []:
            await self.apply_post_conversion_steps(
                converted_volumes,
                converted_segmentations,
                collected_metadata,
                collected_annotations,
            )

        downsampled_data = await asyncio.gather(
            *[
                self.downsample(handle)
                for handle in itertools.chain(converted_volumes, converted_segmentations)
            ]
        )

        downsampled_data = _flatten(downsampled_data)
        if not self.keep_original:
            downsampled_data = list(
                filter(
                    lambda x: x.metadata.resolution != 0,
                    downsampled_data,
                )
            )

        if self._post_processing_steps != []:
            downsampled_data = await self.apply_post_processing_steps(downsampled_data)

        serialized_files = await asyncio.gather(
            *[self.serialize(handle) for handle in downsampled_data]
        )
        serialized_files = _flatten(serialized_files)

        if self._bundler is not None:
            serialized_files = await self.bundle(serialized_files)

        return serialized_files

    @pipeline_stage("Volume Conversion")
    async def convert_volumes(self, paths: list[Path]) -> list[DataSet]:
        volumes = []

        if self._volume_converter_map is None:
            raise RuntimeError("No volume converter map was set!")

        if self._volume_converter_map.is_empty():
            raise RuntimeError("There are no valid volume conveters!")

        for path in paths:
            converter = self._volume_converter_map["".join(path.suffixes)]
            self._state.msg = f"Converting '{path}'"
            volumes += await converter.convert_volume(path, self.context)
            self.context.timer.push_event(f"Finished converting {path}")

        return volumes

    @pipeline_stage("Segmentation Conversion")
    async def convert_segmentations(self, paths: list[Path]) -> list[DataSet]:
        segmentations = []

        if self._segmentation_converter_map is None:
            raise RuntimeError("No volume converter map was set!")

        if self._segmentation_converter_map.is_empty():
            raise RuntimeError("There are no valid volume conveters!")

        for path in paths:
            converter = self._segmentation_converter_map["".join(path.suffixes)]
            self._state.msg = f"Converting '{path}'"
            segmentations += await converter.convert_segmentation(path, self.context)

        return segmentations

    @pipeline_stage("Metadata Collection")
    async def collect_metadata(self, paths: list[Path]):
        return []

    @pipeline_stage("Annotation Collection")
    async def collect_annotation(self, paths: list[Path]):
        return []

    @pipeline_stage("Post-Conversion Steps")
    async def apply_post_conversion_steps(
        self, volumes, segmentations, metadata, annotations
    ):
        for step in self._post_conversion_steps:
            await step(volumes, segmentations, metadata, annotations, self.context)

    @pipeline_stage("Downsampling")
    async def downsample(self, data_set: DataSet) -> list[DataSet]:
        resulting_data_sets: dict[int, DataSet] = {}

        self._state.msg = f"Downsampling '{data_set.metadata.id}'"

        if True:
            resulting_data_sets[0] = data_set

        msg = "Finished downsampling '{}' of ch{} with r{}"

        for channel in data_set.flat_channel_iter():
            frame = channel.parent.metadata.id
            for resolution, downsampled_data in enumerate(
                self._downsampling_strategy.execute(channel, self.context),
                start=1,  # 0 is reserved for the original data resolution
            ):
                if resolution not in resulting_data_sets:
                    resulting_data_sets[resolution] = DataSet(self.context.working_store)
                    resulting_data_sets[resolution].update_metadata(data_set)
                    resulting_data_sets[resolution].metadata.resolution = resolution
                    resulting_data_sets[resolution].metadata.lattice_shape = Vector3(
                        downsampled_data.shape[0],
                        downsampled_data.shape[1],
                        downsampled_data.shape[2],
                    )
                resulting_data_sets[resolution].add_time_frame(frame)
                channel = (
                    resulting_data_sets[resolution]
                    .time_frames[frame]
                    .add_channel(channel.metadata.id)
                )
                channel.set_data(downsampled_data, DaskBackend)
                self.context.timer.push_event(
                    msg.format(data_set.metadata.id, channel.metadata.id, resolution)
                )
        return list(resulting_data_sets.values())

    @pipeline_stage("Post-Processing Steps")
    async def apply_post_processing_steps(self, data_set) -> list[DataSet]:
        processed_data = data_set
        for step in self._post_processing_steps:
            processed_data = await step.execute(processed_data, self.context)
        return processed_data

    @pipeline_stage("Serialization")
    async def serialize(self, data_set) -> list[Path]:
        kind = data_set.metadata.kind

        serializer = self._serializer_map[kind]
        if serializer is None:
            raise RuntimeError(f"Could not find serializer for '{kind}'")

        return await serializer.serialize(
            data_set,
            self._output_dir,
            self.context,
        )

    @pipeline_stage("Bundling")
    async def bundle(self, files: list[Path]):
        if self._bundler is None:
            raise RuntimeError("Cannot bundle without any bundler!")
        return self._bundler.bundle(files, self._output_dir, self.context)
