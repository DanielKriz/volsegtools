import logging
import numpy as np
import dask.array as da

from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
from volsegtools.abc.downsampling_strategy import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class PoolingDownsamplingStrategy(DownsamplingStrategy):
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

    def execute(self, channel: Channel):
        match self.operation:
            case np.mean:
                vst_logger.info("Using the 'Mean' downsampling strategy")
            case np.min:
                vst_logger.info("Using the 'Min' downsampling strategy")
            case np.max:
                vst_logger.info("Using the 'Max' downsampling strategy")

        data = channel.handle.get_lattice(DaskBackend)

        original_dtype = data.dtype

        axes_block_sizes = {
            0: self.block_size,
            1: self.block_size,
            2: self.block_size,
        }

        resolution = 1
        while data.nbytes > super().MIN_SIZE_THRESHOLD:
            log_msg = "... downsampling '{}' for resolution number {}"
            vst_logger.info(log_msg.format(channel.data_set.metadata.id, resolution))

            paddings = []
            for dim in data.shape:
                remainder = dim % self.block_size
                pad = self.block_size - remainder if remainder != 0 else 0
                paddings.append((0, pad))

            data = da.pad(data, pad_width=paddings, mode=self.padding_mode)
            data = da.coarsen(self.operation, data, axes_block_sizes)
            data = data.astype(original_dtype)
            data = data.rechunk("auto")
            resolution += 1
            yield data


class AveragePoolingStrategy(PoolingDownsamplingStrategy):
    def __init__(
        self,
        block_size: int = PoolingDownsamplingStrategy.DEFAULT_BLOCK_SIZE,
        padding_mode: str = PoolingDownsamplingStrategy.DEFAULT_PADDING_MODE,
    ):
        super().__init__(np.mean, block_size, padding_mode)


class MinPoolingStrategy(PoolingDownsamplingStrategy):
    def __init__(
        self,
        block_size: int = PoolingDownsamplingStrategy.DEFAULT_BLOCK_SIZE,
        padding_mode: str = PoolingDownsamplingStrategy.DEFAULT_PADDING_MODE,
    ):
        super().__init__(np.min, block_size, padding_mode)


class MaxPoolingStrategy(PoolingDownsamplingStrategy):
    def __init__(
        self,
        block_size: int = PoolingDownsamplingStrategy.DEFAULT_BLOCK_SIZE,
        padding_mode: str = PoolingDownsamplingStrategy.DEFAULT_PADDING_MODE,
    ):
        super().__init__(np.max, block_size, padding_mode)
