import enum


class DataKind(enum.IntEnum):
    """Representation of a data kind.

    During processing it is often required to know which kind of data is the
    currently processed dataset. For this reason each dataset should be
    accompanied with this value.

    Attributes
    ----------
    VOLUME
        The data is a simple volumetric data.
    SEGMENTATION_VOLUME
        The data is volumetric, but it is representing a segmentation.
    SEGMENTATION_MASK
        The data is volumetric, representing a segmentation and it is
        categorical.
    SEGMENTATION_MASK
        The data is represented as a triangular mesh and it is representing
        a segmentation.
    """

    VOLUME = enum.auto()
    SEGMENTATION_VOLUME = enum.auto()
    SEGMENTATION_MASK = enum.auto()
    SEGMENTATION_MESH = enum.auto()

    def is_volume(self) -> bool:
        """Checks whether the current kind is volumetric.

        Returns
        -------
        bool:
            Whether current instance is volumetric.
        """
        return self.value < DataKind.SEGMENTATION_VOLUME

    def is_segmentation(self) -> bool:
        """Checks whether the current kind is a segmentation.

        Returns
        -------
        bool:
            Whether current instance is a segmentation.
        """
        return self.value >= DataKind.SEGMENTATION_VOLUME
