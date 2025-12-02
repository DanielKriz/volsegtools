import dataclasses
from typing import List

from volsegtools.core import Vector3

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
    lattice_id: str = "unknown"
    id: int = -1
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

def fake_metadata() -> Metadata:
    metadata = Metadata(
        OriginalTimeFrameMetadata(
            "unknown",
            0,
            0,
            Vector3(4, 5, 6),
            Vector3(4, 5, 6),
            Vector3(4, 5, 6),
            [
                ChannelMetadata(0, DescriptiveStatistics(1, 2, 3, 4)),
                ChannelMetadata(1, DescriptiveStatistics(1, 2, 3, 4)),
                ChannelMetadata(2, DescriptiveStatistics(1, 2, 3, 4)),
            ],
            Vector3(4, 5, 6),
        ),
        [
            TimeFrameMetadata(
                "unknown",
                0,
                0,
                Vector3(4, 5, 6),
                Vector3(4, 5, 6),
                Vector3(4, 5, 6),
                [
                    ChannelMetadata(0, DescriptiveStatistics(1, 2, 3, 4)),
                    ChannelMetadata(1, DescriptiveStatistics(1, 2, 3, 4)),
                    ChannelMetadata(2, DescriptiveStatistics(1, 2, 3, 4)),
                ]
            ),
            TimeFrameMetadata(
                "unknown",
                1,
                0,
                Vector3(4, 5, 6),
                Vector3(4, 5, 6),
                Vector3(4, 5, 6),
                [
                    ChannelMetadata(0, DescriptiveStatistics(1, 2, 3, 4)),
                    ChannelMetadata(1, DescriptiveStatistics(1, 2, 3, 4)),
                    ChannelMetadata(2, DescriptiveStatistics(1, 2, 3, 4)),
                ]
            ),
        ],
    )

    return metadata
