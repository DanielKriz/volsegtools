from collections.abc import Iterator

import logging

from volsegtools._downsampling.common import calculate_steps
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.channel import Channel
from volsegtools.abc import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class NearestNeighbor(DownsamplingStrategy[Channel]):
    def __init__(self, factor=2):
        if factor < 1:
            raise RuntimeError("factor has to be atleast 2")
        self.factor = factor

    def execute(
        self,
        data: Channel,
        context: PipelineContext
    ) -> Iterator[Channel]:
        vst_logger.info("Using the 'Neareast Neighbor' downsampling strategy")
        lattice = data.handle.get_lattice(DaskBackend)

        for _ in range(calculate_steps(data, context.size_threshold, self.factor)):
            lattice = lattice[:: self.factor, :: self.factor, :: self.factor]
            yield lattice
