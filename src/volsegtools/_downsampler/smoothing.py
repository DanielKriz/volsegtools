import numpy as np
import scipy
from typing import List
import logging

from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
import volsegtools as vst

vst_logger = logging.getLogger("volsegtools")

class Smoothing(vst.abc.DownsamplingStrategy):
    def __init__(self, size: int, sigma: float):
        self.radius = int(size * sigma + 0.5)
        self.sigma = sigma

    CHUNKS = (256, 256, 256)

    def calculate_approx_downsampled_sizes(self, channel: Channel) -> List[float]:
        bytes_count = channel.handle.nbytes
        sizes = []
        while bytes_count > super().MIN_SIZE_THRESHOLD:
            bytes_count /= 8
            if bytes_count < super().MIN_SIZE_THRESHOLD:
                break
            sizes.append(bytes_count)
        return sizes

    def calculate_steps(self, channel: Channel) -> int:
        return len(self.calculate_approx_downsampled_sizes(channel))

    def calculate_convolution_kernel(self):
        x = np.arange(-self.radius, self.radius + 1)
        kernel = np.exp(-(x**2) / (2 * self.sigma**2))
        kernel = kernel / kernel.sum()
        return kernel

    def execute(self, data: Channel):
        kernel = self.calculate_convolution_kernel()

        def conv_block(block, axis):
            return scipy.ndimage.convolve1d(
                block,
                weights=kernel,
                axis=axis,
                mode='mirror'
            )

        current_data = data.handle.get_lattice(DaskBackend)

        steps = self.calculate_steps(data)
        vst_logger.info(f"Calculated downsampling steps: {steps}")
        for step in range(steps):
            downsampled_data = current_data
            for axis in [0, 1, 2]:
                depth = {x : self.radius if x == axis else 0 for x in range(3) }
                downsampled_data = downsampled_data.map_overlap(
                    conv_block,
                    axis=axis,
                    depth=depth,
                    boundary='reflect',
                    dtype=current_data.dtype,
                )
            downsampled_data = downsampled_data[::2, ::2, ::2]
            downsampled_data = downsampled_data.rechunk((256, 256, 256))
            current_data = downsampled_data
            vst_logger.info(f"Downsampling step {step + 1}/{steps} - DONE")
            yield current_data


