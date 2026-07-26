import logging

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.data_set import Channel
from volsegtools.abc import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class NearestNeighbor(DownsamplingStrategy):
    def __init__(self, factor=2):
        assert factor > 1
        self.factor = factor

    def execute(self, channel: Channel, context: PipelineContext):
        vst_logger.info("Using the 'Neareast Neighbor' downsampling strategy")
        data = channel.handle.get_lattice(DaskBackend)

        while data.nbytes > super().MIN_SIZE_THRESHOLD:
            data = data[:: self.factor, :: self.factor, :: self.factor]
            yield data
