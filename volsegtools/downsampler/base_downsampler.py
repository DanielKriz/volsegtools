from typing import List

from volsegtools.abc.downsampler import Downsampler
from volsegtools.core.downsampling_parameters import DownsamplingParameters
from volsegtools.model.opaque_data_handle import OpaqueDataHandle


class BaseDownsampler(Downsampler):
    # TODO: There shouldn't be any of this, this is just interface...
    def __init__(self, parameters: DownsamplingParameters):
        self._parameters = parameters
        self.data = None

    @property
    def parameters(self) -> DownsamplingParameters:
        return self._parameters

    async def downsample_lattice(
        self, _: OpaqueDataHandle
    ) -> List[OpaqueDataHandle]: ...
