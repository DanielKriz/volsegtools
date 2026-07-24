import scipy
from typing import List
import logging
import math

from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
import volsegtools as vst

vst_logger = logging.getLogger("volsegtools")

class InterpolationBased(vst.abc.DownsamplingStrategy):
    TRILINEAR_FACTOR = 1
    TRICUBIC_FACTOR = 3
    TRIQUINTIC_FACTOR = 5

    def __init__(self, order, inv_factor):
        """
        inv_factor: down scaling factor, i.e., 2 means that the final output is
        going to be 0.5 of the original size.
        """
        if order not in [
            self.TRILINEAR_FACTOR,
            self.TRICUBIC_FACTOR,
            self.TRIQUINTIC_FACTOR,
        ]:
            raise RuntimeError("Unknown polynomial factor for interpolation")
        self.order = order
        self.factor = 1 / inv_factor
        self.inv_factor = inv_factor

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

    def calculate_new_chunks(self, channel, factor: float):
        return tuple(
            tuple(math.ceil(ax / factor) for ax in axes)
            for axes in channel.chunks
        )

    def execute(self, data: Channel):
        match self.order:
            case 1:
                vst_logger.info("Using the 'Trilinear' downsampling strategy")
            case 3:
                vst_logger.info("Using the 'Tricubic' downsampling strategy")
            case 5:
                vst_logger.info("Using the 'Triquintic' downsampling strategy")

        current_data = data.handle.get_lattice(DaskBackend)
        
        def block_zoom(block, zoom_factor=self.factor, order=self.order):
            return scipy.ndimage.zoom(
                block,
                zoom=zoom_factor,
                order=order,
                mode="reflect"
            )

        steps = self.calculate_steps(data)
        for _ in range(steps):
            current_data = current_data.map_blocks(
                block_zoom, 
                dtype=current_data.dtype,
                chunks=self.calculate_new_chunks(
                    current_data,
                    self.inv_factor
                ),
            )
            yield current_data

class TrilinearInterpolation(InterpolationBased):
    def __init__(self):
        super().__init__(self.TRILINEAR_FACTOR, 2)

class TricubicInterpolation(InterpolationBased):
    def __init__(self):
        super().__init__(self.TRICUBIC_FACTOR, 2)

class TriquinticInterpolation(InterpolationBased):
    def __init__(self):
        super().__init__(self.TRIQUINTIC_FACTOR, 2)
