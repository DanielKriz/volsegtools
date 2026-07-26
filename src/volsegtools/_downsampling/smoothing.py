from collections.abc import Iterator

import logging

import dask_image.ndfilters as dask_filter
import numpy as np
import scipy

from volsegtools._core import ConvolutionKernel, Gaussian3DKernel
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.channel import Channel
from volsegtools.abc import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class Smoothing(DownsamplingStrategy[Channel]):
    # We have to choose some reasonable size of the chunks with which
    # we will be working here. This has been chosen because for floats
    # it has around 70MB, the chunk size should be somewhere between
    # 50-150MB on modern processors.
    CHUNKS = (256, 256, 256)

    def calculate_approx_downsampled_sizes(self, channel: Channel) -> list[float]:
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

    def execute(
        self,
        data: Channel,
        context: PipelineContext
    ) -> Iterator[Channel]:
        vst_logger.info("Using the 'Smoothing' downsampling strategy")

        if 1 in data.handle.shape:
            yield from []

        current_data = data.handle.get_lattice(DaskBackend)

        steps = self.calculate_steps(data)
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


class SeparatedSmoothing(DownsamplingStrategy[Channel]):
    def __init__(self, size: int, sigma: float):
        self.radius = int(size * sigma + 0.5)
        self.sigma = sigma

    CHUNKS = (256, 256, 256)

    def calculate_approx_downsampled_sizes(self, channel: Channel) -> list[float]:
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
        return kernel / kernel.sum()

    def execute(
        self,
        data: Channel,
        context: PipelineContext
    ) -> Iterator[Channel]:
        kernel = self.calculate_convolution_kernel()

        def conv_block(block, axis):
            return scipy.ndimage.convolve1d(
                block, weights=kernel, axis=axis, mode="mirror"
            )

        current_data = data.handle.get_lattice(DaskBackend)

        steps = self.calculate_steps(data)
        vst_logger.info(f"Calculated downsampling steps: {steps}")
        for step in range(steps):
            downsampled_data = current_data
            for axis in [0, 1, 2]:
                depth = {x: self.radius if x == axis else 0 for x in range(3)}
                downsampled_data = downsampled_data.map_overlap(
                    conv_block,
                    axis=axis,
                    depth=depth,
                    boundary="reflect",
                    dtype=current_data.dtype,
                )
            downsampled_data = downsampled_data[::2, ::2, ::2]
            downsampled_data = downsampled_data.rechunk((256, 256, 256))
            current_data = downsampled_data
            vst_logger.info(f"Downsampling step {step + 1}/{steps} - DONE")
            yield current_data


class StridedSmoothing(DownsamplingStrategy[Channel]):
    def __init__(self, kernel: ConvolutionKernel, stride=2):
        self.kernel = kernel
        self.stride = stride

    CHUNKS = (256, 256, 256)

    def calculate_approx_downsampled_sizes(self, channel: Channel) -> list[float]:
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

    def execute(
        self,
        data: Channel,
        context: PipelineContext,
    ) -> Iterator[Channel]:
        radius = self.kernel.size
        kernel_arr = self.kernel.as_ndarray()

        def conv_and_slice_block(block):
            conv = scipy.ndimage.convolve(block, weights=kernel_arr, mode="reflect")
            return conv[:: self.stride, :: self.stride, :: self.stride]

        current_data = data.handle.get_lattice(DaskBackend)

        steps = self.calculate_steps(data)
        vst_logger.info(f"Calculated downsampling steps: {steps}")
        for step in range(steps):
            downsampled_data = current_data
            new_chunks = tuple(
                tuple(c // self.stride for c in axis_chunks)
                for axis_chunks in downsampled_data.chunks
            )
            downsampled_data = downsampled_data.map_overlap(
                conv_and_slice_block,
                depth=radius,
                boundary="reflect",
                # TODO: research what this does...
                drop_axis=[0, 1, 2],
                new_axis=[0, 1, 2],
                chunks=new_chunks,
                dtype=current_data.dtype,
            )
            # downsampled_data = downsampled_data.rechunk((256, 256, 256))
            current_data = downsampled_data
            vst_logger.info(f"Downsampling step {step + 1}/{steps} - DONE")
            yield current_data
