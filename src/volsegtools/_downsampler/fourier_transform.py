import logging
import numpy as np
import dask.array as da
import dask.array.fft

from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
from volsegtools.abc.downsampling_strategy import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class FourierTransform(DownsamplingStrategy):
    def execute(self, data: Channel):
        array = data.handle.get_lattice(DaskBackend)
        original_dtype = array.dtype


        resolution = 1
        while array.nbytes > super().MIN_SIZE_THRESHOLD:
            log_msg = "... downsampling '{}' for resolution number {}"
            vst_logger.info(log_msg.format(data.data_set.metadata.id, resolution))

            F = da.fft.fftn(array)
            F_shifted = da.fft.fftshift(F)

            target_shape = tuple(ax // 2 for ax in array.shape)

            z_c, y_c, x_c = [ s // 2 for s in F_shifted.shape ]
            tz, ty, tx = [ s // 2 for s in target_shape ]

            F_cropped = F_shifted[
                z_c - tz : z_c + tz,
                y_c - ty : y_c + ty,
                x_c - tx : x_c + tx,
            ]

            F_cropped_unshifted = da.fft.ifftshift(F_cropped)
            downsampled = da.fft.ifftn(F_cropped_unshifted).real

            array = downsampled
            array = array.astype(original_dtype)
            array = array.rechunk("auto")
            resolution += 1
            yield array
