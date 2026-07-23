import logging
import numpy as np
import dask.array as da
import pywt

from volsegtools._model.dask_backend import DaskBackend
from volsegtools._model.data_set import Channel
from volsegtools.abc.downsampling_strategy import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class WaveletTransform(DownsamplingStrategy):
    DEFAULT_BLOCK_SIZE = 2
    DEFAULT_PADDING_MODE = "reflect"

    def execute(self, data: Channel):
        array = data.handle.get_lattice(DaskBackend)

        original_dtype = array.dtype

        def dwt_block(block, wavelet="db1", trim_depth=0):
            coeffs = pywt.dwtn(block, wavelet)
            approx = coeffs['aaa']

            if trim_depth > 0:
                return approx[
                    trim_depth:-trim_depth,
                    trim_depth:-trim_depth,
                    trim_depth:-trim_depth,
                ]
            return approx


        w = pywt.Wavelet("db1")
        # pad = w.dec_len + 1
        pad = 0
        if pad % 2 != 0:
            pad += 1

        out_trim = pad // 2

        array = da.overlap.overlap(array, depth={0:pad, 1:pad, 2:pad}, boundary="reflect")

        # overlap_depth = w.dec_len // 2

        # print(array.shape)

        resolution = 1
        while array.nbytes > super().MIN_SIZE_THRESHOLD:
            log_msg = "... downsampling '{}' for resolution number {}"
            vst_logger.info(log_msg.format(data.data_set.metadata.id, resolution))

            new_chunks = tuple(
                tuple(c // 2 for c in axes)
                for axes in array.chunks
            )

            # print(tuple(c // 2 for c in array.chunksize))
            downsampled = array.map_blocks(
                dwt_block,
                trim_depth=out_trim,
                dtype=np.float32,
                chunks=new_chunks,
            )
            print(downsampled)
            print(downsampled.shape)
            print(downsampled.chunks)

            array = downsampled
            array = array.astype(original_dtype)
            array = array.rechunk("auto")
            resolution += 1
            yield array
