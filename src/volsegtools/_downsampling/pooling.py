from collections.abc import Iterator

import logging

import dask.array as da
import numpy as np

from volsegtools._downsampling.common import calculate_steps
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.channel import Channel
from volsegtools.abc.downsampling_strategy import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class PoolingDownsamplingStrategy(DownsamplingStrategy[Channel]):
    DEFAULT_BLOCK_SIZE = 2
    DEFAULT_PADDING_MODE = "reflect"

    def __init__(
        self,
        operation,
        block_size: int = DEFAULT_BLOCK_SIZE,
        padding_mode: str = DEFAULT_PADDING_MODE,
    ):
        """
        'edge' padding mode is good for masks
        'reflect' padding mode is good for continuous volumes
        """
        self.operation = operation
        self.block_size = block_size
        self.padding_mode = padding_mode

    def execute(self, data: Channel, context: PipelineContext) -> Iterator[Channel]:
        match self.operation:
            case np.mean:
                vst_logger.info("Using the 'Mean' downsampling strategy")
            case np.min:
                vst_logger.info("Using the 'Min' downsampling strategy")
            case np.max:
                vst_logger.info("Using the 'Max' downsampling strategy")

        lattice = data.handle.get_lattice(DaskBackend)

        original_dtype = lattice.dtype

        axes_block_sizes = {
            0: self.block_size,
            1: self.block_size,
            2: self.block_size,
        }

        resolution = 1
        for _ in range(calculate_steps(data, context.size_threshold, self.block_size)):
            log_msg = "... downsampling '{}' for resolution number {}"
            vst_logger.info(log_msg.format(data.data_set.metadata.id, resolution))

            paddings = []
            for dim in lattice.shape:
                remainder = dim % self.block_size
                pad = self.block_size - remainder if remainder != 0 else 0
                paddings.append((0, pad))

            lattice = da.pad(lattice, pad_width=paddings, mode=self.padding_mode)
            lattice = da.coarsen(self.operation, lattice, axes_block_sizes)
            lattice = lattice.astype(original_dtype)
            lattice = lattice.rechunk("auto")
            resolution += 1
            yield lattice


class AveragePooling(PoolingDownsamplingStrategy):
    def __init__(
        self,
        block_size: int = PoolingDownsamplingStrategy.DEFAULT_BLOCK_SIZE,
        padding_mode: str = PoolingDownsamplingStrategy.DEFAULT_PADDING_MODE,
    ):
        super().__init__(np.mean, block_size, padding_mode)


class MinPooling(PoolingDownsamplingStrategy):
    def __init__(
        self,
        block_size: int = PoolingDownsamplingStrategy.DEFAULT_BLOCK_SIZE,
        padding_mode: str = PoolingDownsamplingStrategy.DEFAULT_PADDING_MODE,
    ):
        super().__init__(np.min, block_size, padding_mode)


class MaxPooling(PoolingDownsamplingStrategy):
    def __init__(
        self,
        block_size: int = PoolingDownsamplingStrategy.DEFAULT_BLOCK_SIZE,
        padding_mode: str = PoolingDownsamplingStrategy.DEFAULT_PADDING_MODE,
    ):
        super().__init__(np.max, block_size, padding_mode)
