import dataclasses
from typing import List

from volsegtools.core import LatticeKind, Vector3


@dataclasses.dataclass
class DescriptiveStatistics:
    """Represents statistics that should be collected for some data set for
       it to be representable in CIF.
    """
    mean: float
    std: float
    max: float
    min: float

@dataclasses.dataclass
class ChannelMetadata:
    id: int
    statistics: DescriptiveStatistics

@dataclasses.dataclass
class TimeFrameMetadata:
    # TODO: rename to 'name'
    axis_order: Vector3 = dataclasses.field(default_factory=Vector3)
    lattice_id: str = "unknown"
    kind: LatticeKind = dataclasses.field(default=LatticeKind.VOLUME)
    id: int = -1
    axis_order: Vector3 = dataclasses.field(default_factory=Vector3)
    resolution: int = -1
    origin: Vector3 = dataclasses.field(default_factory=Vector3)
    lattice_dimensions: Vector3 = dataclasses.field(default_factory=Vector3)
    voxel_size: Vector3 = dataclasses.field(default_factory=Vector3)
    channels: List[ChannelMetadata] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class OriginalTimeFrameMetadata(TimeFrameMetadata):
    axis_order: Vector3 = dataclasses.field(default_factory=Vector3)


@dataclasses.dataclass
class Metadata:
    original_time_frame: OriginalTimeFrameMetadata = dataclasses.field(default_factory=OriginalTimeFrameMetadata)
    time_frames: List[TimeFrameMetadata] = dataclasses.field(default_factory=list)
