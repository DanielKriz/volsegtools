import asyncio
from pathlib import Path
from typing import List, Optional
import itertools
import logging

import volsegtools as vst
from volsegtools._converter.converter_map import ConverterMap
from volsegtools._core.data_kind import DataKind
from volsegtools._core.timer import Timer
from volsegtools._core.vector import Vector3
from volsegtools._downsampler.null_downsampling_strategy import (
    NullDownsamplingStrategy,
)
from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import DataSet
from volsegtools._model.working_store import WorkingStore
from volsegtools.abc import (
    PostProcessingStep,
    PostConversionStep,
)
from volsegtools.abc.bundler import Bundler
from volsegtools.abc.serializer import Serializer

vst_logger = logging.getLogger("volsegtools")


def _flatten(list_of_lists: List[List]) -> List:
    # Source - https://stackoverflow.com/a/952952
    return [x for xs in list_of_lists for x in xs]


class ProcessingPipeline(vst.abc.ProcessingPipeline):

    def __init__(
        self,
        downsampling_strategy=NullDownsamplingStrategy(),
        volume_converter_map: Optional[ConverterMap] = None,
        segmentation_converter_map: Optional[ConverterMap] = None,
        volume_serializer: Optional[Serializer] = None,
        segmentation_mask_serializer: Optional[Serializer] = None,
        segmentation_volume_serializer: Optional[Serializer] = None,
        segmentation_mesh_serializer: Optional[Serializer] = None,
        post_processing_steps: List[PostProcessingStep] = [],
        post_conversion_steps: List[PostConversionStep] = [],
        bundler: Optional[Bundler] = None,
        work_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        self._downsampling_strategy = downsampling_strategy

        self._volume_converter_map = volume_converter_map
        self._segmentation_converter_map = segmentation_converter_map

        self._output_dir = output_dir if output_dir is not None else Path()
        self._data = WorkingStore.instance

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

        self._post_processing_steps = post_processing_steps
        self._post_conversion_steps = post_conversion_steps
        self._bundler = bundler

    def sync_process(
        self,
        volumes: List[Path] = [],
        segmentations: List[Path] = [],
        metadata: List[Path] = [],
        annotations: List[Path] = [],
    ) -> List[Path]:
        return asyncio.run(self.process(volumes, segmentations, metadata, annotations))

    async def process(
        self,
        volumes: List[Path] = [],
        segmentations: List[Path] = [],
        metadata: List[Path] = [],
        annotations: List[Path] = [],
    ) -> List[Path]:
        vst_logger.info("Converting Volumes")
        Timer.push_stage("Volume Conversion")
        converted_volumes = await self.convert_volumes(volumes)

        vst_logger.info("Converting Segmentations")
        Timer.push_stage("Segmentation Conversion")
        converted_segmentations = await self.convert_segmentations(segmentations)

        Timer.push_stage("Metadata Collection")
        collected_metadata = await self.collect_metadata(metadata)

        Timer.push_stage("Annotation Collection")
        collected_annotations = await self.collect_annotation(annotations)

        vst_logger.info("Applying post conversion steps")
        Timer.push_stage("Post Conversion Steps")
        if self._post_conversion_steps != []:
            await self.apply_post_conversion_steps(
                converted_volumes,
                converted_segmentations,
                collected_metadata,
                collected_annotations,
            )

        vst_logger.info("Downsampling Volumes and Segmentations")
        Timer.push_stage("Downsampling")
        downsampled_data = await asyncio.gather(
            *[
                self.downsample(handle)
                for handle in itertools.chain(
                    converted_volumes, converted_segmentations
                )
            ]
        )
        downsampled_data = _flatten(downsampled_data)
        vst_logger.info("Downsampling Volumes and Segmentations - DONE")

        vst_logger.info("Applying Post Processing Steps")
        Timer.push_stage("Post Processing")
        if self._post_processing_steps != []:
            downsampled_data = await self.apply_post_processing_steps(downsampled_data)
        vst_logger.info("Applying Post Processing Steps - DONE")

        vst_logger.info("Serializing Volumes and Segmentations")
        Timer.push_stage("Serialization")
        serialized_files = await asyncio.gather(
            *[self.serialize(handle) for handle in downsampled_data]
        )
        serialized_files = _flatten(serialized_files)
        vst_logger.info("Serializing Volumes and Segmentations - DONE")

        if self._bundler is not None:
            Timer.push_stage("Bundling")
            serialized_files = await self.bundle(serialized_files)

        return serialized_files

    async def convert_volumes(self, paths: List[Path]) -> List[DataSet]:
        volumes = []

        if self._volume_converter_map is None:
            raise RuntimeError("No volume converter map was set!")

        if self._volume_converter_map.is_empty():
            raise RuntimeError("There are no valid volume conveters!")

        for path in paths:
            converter = self._volume_converter_map["".join(path.suffixes)]
            volumes += await converter.convert_volume(path)
            Timer.push_event(f"Finished converting {path}")

        return volumes

    async def convert_segmentations(self, paths: List[Path]) -> List[DataSet]:
        segmentations = []

        if self._segmentation_converter_map is None:
            raise RuntimeError("No volume converter map was set!")

        if self._segmentation_converter_map.is_empty():
            raise RuntimeError("There are no valid volume conveters!")

        for path in paths:
            converter = self._segmentation_converter_map["".join(path.suffixes)]
            segmentations += await converter.convert_segmentation(path)

        return segmentations

    async def collect_metadata(self, paths: List[Path]):
        return []

    async def collect_annotation(self, paths: List[Path]):
        return []

    async def apply_post_conversion_steps(
        self, volumes, segmentations, metadata, annotations
    ):
        for step in self._post_conversion_steps:
            step(volumes, segmentations, metadata, annotations)

    async def downsample(self, data_set: DataSet) -> List[DataSet]:
        resulting_data_sets: dict[int, DataSet] = {}

        if True:
            resulting_data_sets[0] = data_set

        msg = "Finished downsampling '{}' of ch{} with r{}"

        for channel in data_set.flat_channel_iter():
            frame = channel.parent.metadata.id
            for resolution, downsampled_data in enumerate(
                self._downsampling_strategy.execute(channel),
                start=1,  # 0 is reserved for the original data resolution
            ):
                if resolution not in resulting_data_sets.keys():
                    resulting_data_sets[resolution] = DataSet(
                        WorkingStore.instance.data_store
                    )
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
                Timer.push_event(
                    msg.format(data_set.metadata.id, channel.metadata.id, resolution)
                )
        return list(resulting_data_sets.values())

    async def apply_post_processing_steps(self, data_set) -> List[DataSet]:
        processed_data = data_set
        for step in self._post_processing_steps:
            processed_data = await step.execute(processed_data)
        return processed_data

    async def serialize(self, data_set) -> List[Path]:
        kind = data_set.metadata.kind

        serializer = self._serializer_map[kind]
        if serializer is None:
            raise RuntimeError(f"Could not find serializer for '{kind}'")

        return await serializer.serialize(data_set, self._work_dir)
    async def bundle(self, files: List[Path]):
        if self._bundler is None:
            raise RuntimeError("Cannot bundle without any bundler!")
        return self._bundler.bundle(files, self._output_dir)

