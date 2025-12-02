import dask.array as da

from volsegtools.abc.downsampler import Downsampler
from volsegtools.model import Data
from volsegtools.core.downsampling_parameters import (
    DownsamplingParameters
)

class BaseDownsampler(Downsampler):

    # TODO: There shouldn't be any of this, this is just interface...
    def __init__(self, params: DownsamplingParameters):
        self.params = params
        self.data = None

    @property
    def parameters(self) -> DownsamplingParameters:
        return self.params

    async def downsample_lattice(self, name, lattice: da.Array, kind) -> da.Array:
        raise NotImplementedError()

    def downsample(self, data: Data) -> Data:
        raise NotImplementedError()
