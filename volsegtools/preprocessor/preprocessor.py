from typing import List, Optional
from pathlib import Path
import asyncio
import logging

from volsegtools.abc import Converter, Downsampler, ConvolutionKernel
from volsegtools.model import (
    Data,
)
from volsegtools.serialization import BCIFSerializer

class Preprocessor:

    state = {
        "downsampling_status" : 0.0
    }

    def __init__(
        self,
        downsampler: Downsampler,
        converter: Converter,
        volume_input_files: List[Path],
        segmentation_input_files: List[Path],
        metadata_input_files: Optional[List[Path]] = None,
        annotations_input_files: Optional[List[Path]] = None,
        work_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        self.converter: Converter = converter
        self._output_dir = output_dir if output_dir is not None else Path()
        self._data = Data(self._output_dir)
        self.downsampler = downsampler
        # This has to be reflected in the design of Downsampler class
        self.downsampler.data = self._data
        self._volume_input_files = volume_input_files
        self._segmentation_input_files = segmentation_input_files
        self._metadata_input_files = metadata_input_files
        self._annotations_input_files = annotations_input_files
        self._work_dir = work_dir

    async def transform_volume(self):
        # TODO: enumerate the volumes and store them separately
        for volume_src_path in self._volume_input_files:
            logging.info(f"Transforming volume {volume_src_path}")
            # TODO: create tasks and then use gather!
            await self.converter.transform_volume(
                volume_src_path,
                self._data,
            )

    async def collect_metadata(self):
        for volume_src_path in self._volume_input_files:
            await self.converter.collect_metadata(
                volume_src_path,
                self._data,
            )

    def create_converter_from_format(self):
        return Converter
        pass

    def set_mode(self, mode):
        return self

    def add_input(self, path, kind):
        return self

    def set_workdir(self, path):
        return self

    async def transform_segmentation(self):
        logging.info("Transforming segmentation")
        # TODO: enumerate the volumes and store them separately
        for segmentation_src_path in self._segmentation_input_files:
            logging.info(f"Processing file {segmentation_src_path}")
            # TODO: create tasks and then use gather!
            await self.converter.transform_segmentation(
                segmentation_src_path,
                self._data,
            )

    async def preprocess(self):
        logging.info("Starting the preprocessor")
        converter = self.create_converter_from_format()
    
        tasks = [
            asyncio.create_task(callable) for callable in [
                self.transform_volume(),
                self.transform_segmentation(),
                self.collect_metadata(),
            ]
        ]
    
        results = await asyncio.gather(*tasks)
    
        # TODO: rework this without the intermediate results
        results_nametags = [
            'volume',
            'segmentation',
            'metadata',
        ]
    
        results = dict(zip(results_nametags, results))
        return results
    
    
    def sync_preprocess(self):
        result = asyncio.run(self.preprocess())
        self.downsampler.downsample(self._data)
        return result


    async def serialize_data(self):
        await BCIFSerializer.serialize(self._data, self._output_dir)

    def serialize(self):
        print("Start serialization")
        result = asyncio.run(self.serialize_data())
        return result

    def downsample(self):
        pass
