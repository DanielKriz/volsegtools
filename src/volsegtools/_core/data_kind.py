from typing import Annotated

import enum

import pydantic


class DataKind(enum.IntEnum):
    VOLUME = enum.auto()
    SEGMENTATION_VOLUME = enum.auto()
    SEGMENTATION_MASK = enum.auto()
    SEGMENTATION_MESH = enum.auto()

    def is_volume(self) -> bool:
        return self.value < DataKind.SEGMENTATION_VOLUME

    def is_segmentation(self) -> bool:
        return self.value >= DataKind.SEGMENTATION_VOLUME


SerializableDataKind = Annotated[
    DataKind,
    pydantic.PlainSerializer(
        lambda v: v.name.lower(),
        return_type=str,
    ),
]
