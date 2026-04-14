import enum


class LatticeKind(enum.Enum):
    """ """

    VOLUME = 1
    SEGMENTATION = 2


class DataKind(enum.IntEnum):
    VOLUME = 1
    SEGMENTATION_VOLUME = 2
    SEGMENTATION_MASK = 3
    SEGMENTATION_MESH = 4
