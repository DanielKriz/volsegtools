import asyncio
from pathlib import Path
from typing import List, Optional, DefaultDict
import itertools
import collections
import logging

import volsegtools as vst
from volsegtools._core.vector import Vector3
from volsegtools._downsampler.hierarchy_downsampling_strategy import (
    NullDownsamplingStrategy,
)
from volsegtools._model.data_set import DataSet
from volsegtools._model.opaque_data_handle import OpaqueDataHandle
from volsegtools.abc import Converter
from volsegtools._model.working_store import WorkingStore
from volsegtools.abc import (
    PostProcessingStep,
    PostConversionStep,
)
from volsegtools.abc.serializer import Serializer


def _flatten(list_of_lists: List[List]) -> List:
    # Source - https://stackoverflow.com/a/952952
    return [x for xs in list_of_lists for x in xs]


class ProcessingPipeline(vst.abc.ProcessingPipeline):
    state = {"downsampling_status": 0.0}

    def __init__(
        self,
        downsampling_strategy=NullDownsamplingStrategy(),
        volume_converter: Optional[Converter] = None,
        segmentation_converter: Optional[Converter] = None,
        serializer: Optional[Serializer] = None,
        post_processing_steps: List[PostProcessingStep] = [],
        post_conversion_steps: List[PostConversionStep] = [],
        work_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        if volume_converter is None and segmentation_converter is None:
            raise RuntimeError("Atleast one converter has to be set")

        self._downsampling_strategy = downsampling_strategy

        self._volume_converter = volume_converter
        self._segmentation_converter = segmentation_converter

        self._output_dir = output_dir if output_dir is not None else Path()
        self._data = WorkingStore.instance
        # self._downsampler = downsampler
        self._serializer = serializer
        self._work_dir = work_dir

        self._post_processing_steps = post_processing_steps
        self._post_conversion_steps = post_conversion_steps

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
        logging.info("Converting Volumes")
        converted_volumes = await self.convert_volumes(volumes)

        logging.info("Converting Segmentations")
        converted_segmentations = await self.convert_segmentations(segmentations)

        collected_metadata = await self.collect_metadata(metadata)
        collected_annotations = await self.collect_annotation(annotations)

        logging.info("Applying post conversion steps")
        if self._post_conversion_steps != []:
            await self.apply_post_conversion_steps(
                converted_volumes,
                converted_segmentations,
                collected_metadata,
                collected_annotations,
            )

        logging.info("Downsampling Volumes and Segmentations")
        downsampled_data = await asyncio.gather(
            *[
                self.downsample(handle)
                for handle in itertools.chain(
                    converted_volumes, converted_segmentations
                )
            ]
        )
        downsampled_data = _flatten(downsampled_data)
        logging.info("Downsampling Volumes and Segmentations - DONE")

        logging.info("Applying Post Processing Steps")
        if self._post_processing_steps != []:
            downsampled_data = await asyncio.gather(
                *[
                    self.apply_post_processing_steps(handle)
                    for handle in downsampled_data
                ]
            )
            downsampled_data = _flatten(downsampled_data)
        logging.info("Applying Post Processing Steps - DONE")

        logging.info("Serializing Volumes and Segmentations")
        serialized_files = await asyncio.gather(
            *[self.serialize(handle) for handle in downsampled_data]
        )
        serialized_files = _flatten(serialized_files)
        logging.info("Serializing Volumes and Segmentations - DONE")

        return serialized_files

    async def convert_volumes(self, paths: List[Path]) -> List[DataSet]:
        volumes = []

        if self._volume_converter is None:
            return volumes

        for volume_path in paths:
            volumes += await self._volume_converter.convert_volume(volume_path)
        return volumes

    async def convert_segmentations(self, paths: List[Path]) -> List[DataSet]:
        segmentations = []

        if self._segmentation_converter is None:
            return segmentations

        for segmentation_path in paths:
            segmentations += await self._segmentation_converter.convert_segmentation(
                segmentation_path
            )
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
        resulting_data_sets: DefaultDict[int, DataSet] = collections.defaultdict(
            DataSet
        )

        # TODO: add check if we should include the original resolution
        if True:
            resulting_data_sets[0] = data_set

        for channel in data_set.flat_channel_iter():
            frame = channel.parent.metadata.id
            for resolution, downsampled_data in enumerate(
                self._downsampling_strategy.execute(channel),
                start=1,  # 0 is reserved for the original data resolution
            ):
                resulting_data_sets[resolution].update_metadata(data_set)
                resulting_data_sets[resolution].metadata.resolution = resolution
                resulting_data_sets[resolution].metadata.lattice_shape = Vector3(
                    downsampled_data.shape[0],
                    downsampled_data.shape[1],
                    downsampled_data.shape[2],
                )

                resulting_data_sets[resolution].add_time_frame(frame)
                resulting_data_sets[resolution].time_frames[frame].add_channel(
                    downsampled_data, channel.metadata.id
                )
        return list(resulting_data_sets.values())

    async def serialize(self, data_set) -> List[Path]:
        if self._serializer is None:
            return []

        return await self._serializer.serialize(data_set, self._output_dir)

    async def apply_post_processing_steps(
        self, data_handle: OpaqueDataHandle
    ) -> List[OpaqueDataHandle]:
        data = [data_handle]
        for step in self._post_processing_steps:
            data = step(data)

        return data

    async def get_progress(self):
        pass
