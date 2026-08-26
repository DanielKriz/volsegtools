from pydantic import Field

import pydantic

from volsegtools._core import AxisValues, DataKind


class DataSetInfo(pydantic.BaseModel):
    """Metadata related to the data set.

    Attributes
    ----------
    filename: str
        File name of the input data.
    resolution: int
        Current resolution of said dataset.
    axis_order: AxisValues
        Axis order of the data held by the dataset.
    cell_size: AxisValues
        Dimensions of a single cell in the dataset.
    origin: AxisValues
        Origin of the coordinate system of the dataset.
    id: str
        Name of the dataset.
    kind: DataKind
        Kind of the data held by the dataset.
    lattice_shape: AxisValues
        Dimensions of the data lattice.
    """

    filename: str = "Unknown File"
    resolution: int = -1
    axis_order: AxisValues = Field(default_factory=AxisValues)
    cell_size: AxisValues = Field(default_factory=AxisValues)
    origin: AxisValues = Field(default_factory=AxisValues)
    id: str = "Unknown"
    kind: DataKind = DataKind.VOLUME
    lattice_shape: AxisValues = Field(default_factory=AxisValues)


class TimeFrameInfo(pydantic.BaseModel):
    """Metadata related to a single time frame.

    Attributes
    ----------
    id: int
        Unique identifier of the time frame in its parent dataset.
    """

    id: int = -1


@pydantic.dataclasses.dataclass
class DescriptiveStatistics:
    """Statistics about the data that might be required for serialization.

    Attributes
    ----------
    mean: float
        Mean of the whole channel (one layer of data).
    std: float
        Standard deviation of the whole channel.
    min: float
        Minimum value in the channel.
    max: float
        Maximum value in the channel.
    """

    mean: float = 0.0
    std: float = 0.0
    max: float = 0.0
    min: float = 0.0


class ChannelInfo(pydantic.BaseModel):
    """Metadata related to a single data channel.

    Attributes
    ----------
    id: int
        Unique identifier in its parent time frame.
    statistics: DescriptiveStatistics
        Statistics related to this channel.
    """

    id: int = -1
    statistics: DescriptiveStatistics = Field(default_factory=DescriptiveStatistics)


class MeshInfo(pydantic.BaseModel):
    """Metadata related to a mesh data.

    Attributes
    ----------
    id: int
        Unique identifier in its parent time frame.
    """

    id: int = -1
