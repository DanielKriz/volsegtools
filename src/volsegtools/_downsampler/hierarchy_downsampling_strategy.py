from typing import List

import dask.array as da
import dask_image.ndfilters as dask_filter

from volsegtools._model.data_set import Channel
from volsegtools._core.gaussian_kernel_3D import Gaussian3DKernel
import volsegtools as vst


# TODO: add support for Downsampling parameters!


# This should return raw data
class HierarchyDownsamplingStrategy(vst.abc.DownsamplingStrategy):
    MIN_SIZE_THRESHOLD = 1_000_000  # 1 MB

    def calculate_approx_downsampled_sizes(self, channel: Channel) -> List[float]:
        bytes_count = channel.data.access().nbytes
        sizes = []
        while bytes_count > HierarchyDownsamplingStrategy.MIN_SIZE_THRESHOLD:
            bytes_count /= 8
            if bytes_count < HierarchyDownsamplingStrategy.MIN_SIZE_THRESHOLD:
                break
            sizes.append(bytes_count)
        return sizes

    def calculate_steps(self, channel: Channel) -> int:
        return len(self.calculate_approx_downsampled_sizes(channel))

    def execute(self, channel: Channel):
        current_data = da.from_zarr(
            url=channel.data.access(),
            # chunks=channel.data.access().chunks,
            chunks=(256, 256, 256),
        )

        if 1 in channel.data.access().shape:
            yield from []

        for _ in range(self.calculate_steps(channel)):
            downsampled_data = dask_filter.convolve(
                current_data,
                Gaussian3DKernel(5, 1.0).as_ndarray(),
                mode="mirror",
                cval=0.0,
            )
            downsampled_data = downsampled_data[::2, ::2, ::2]
            downsampled_data = downsampled_data.rechunk((256, 256, 256))
            current_data = downsampled_data
            yield current_data


class NullDownsamplingStrategy(vst.abc.DownsamplingStrategy):
    def execute(self, _):
        yield from []
