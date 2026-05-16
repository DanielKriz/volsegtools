import scipy
from typing import List
import logging

from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
import volsegtools as vst
from volsegtools.abc.kernel import ConvolutionKernel

vst_logger = logging.getLogger("volsegtools")


class StridedSmoothing(vst.abc.DownsamplingStrategy):
    def __init__(self, kernel: ConvolutionKernel, stride=2):
        self.kernel = kernel
        self.stride = stride

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

    def execute(self, data: Channel):
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
