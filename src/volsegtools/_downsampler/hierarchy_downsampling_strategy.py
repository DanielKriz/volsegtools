from typing import List
import logging

import dask.array as da
import dask_image.ndfilters as dask_filter

from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
from volsegtools._core.gaussian_kernel_3D import Gaussian3DKernel
import volsegtools as vst

vst_logger = logging.getLogger("volsegtools")

# TODO: add support for Downsampling parameters!


# This should return raw data
class HierarchyDownsamplingStrategy(vst.abc.DownsamplingStrategy):
    # We have to choose some reasonable size of the chunks with which
    # we will be working here. This has been chosen because for floats
    # it has around 70MB, the chunk size should be somewhere between
    # 50-150MB on modern processors.
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

    def execute(self, channel: Channel):
        vst_logger.info("Using the 'Smoothing' downsampling strategy")

        if 1 in channel.handle.shape:
            yield from []

        current_data = channel.handle.get_lattice(DaskBackend)

        steps = self.calculate_steps(channel)
        vst_logger.info(f"Calculated downsampling steps: {steps}")
        for step in range(steps):
            vst_logger.info(f"Downsampling step {step + 1}/{steps}")
            downsampled_data = dask_filter.convolve(
                current_data,
                Gaussian3DKernel(5, 1.0).as_ndarray(),
                mode="mirror",
                cval=0.0,
            )
            downsampled_data = downsampled_data[::2, ::2, ::2]
            downsampled_data = downsampled_data.rechunk((256, 256, 256))
            current_data = downsampled_data
            vst_logger.info(f"Downsampling step {step + 1}/{steps} - DONE")
            yield current_data

