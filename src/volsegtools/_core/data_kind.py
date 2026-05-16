import enum


class DataKind(enum.IntEnum):
    VOLUME = enum.auto()
    SEGMENTATION_VOLUME = enum.auto()
    SEGMENTATION_MASK = enum.auto()
    SEGMENTATION_MESH = enum.auto()

    def is_volume(self):
        return self.value < DataKind.SEGMENTATION_VOLUME

    def is_segmentation(self):
        return self.value >= DataKind.SEGMENTATION_VOLUME
