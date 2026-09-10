from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Self

import re

import pydantic

from volsegtools._model import DatasetMetadata
from volsegtools._storage.time_frame import TimeFrame

if TYPE_CHECKING:
    from collections.abc import Iterator

    from volsegtools._core.working_store import WorkingStore
    from volsegtools._storage.channel import Channel


class Dataset:
    def __init__(self, store: WorkingStore, metadata: DatasetMetadata | None = None):
        self.store = store
        if metadata:
            self._metadata_is_set = True
            self.metadata = metadata
        else:
            self._metadata_is_set = False
            self.metadata = DatasetMetadata()
        self.time_frames = []
        self._last_time_frame_num = 0

    @property
    def zarr_path(self) -> Path:
        if self.metadata.kind.is_segmentation():
            root = Path("segmentation_data")
        else:
            root = Path("volume_data")
        return root / self.metadata.id / f"resolution_{self.metadata.resolution}"

    def __iter__(self) -> Iterator[TimeFrame]:
        yield from self.time_frames

    # TODO: this should work with meshes too
    def flat_channel_iter(self) -> Iterator[Channel]:
        for frame in self.time_frames:
            yield from frame

    def add_time_frame(self, id: int = -1) -> TimeFrame:
        if id == -1:
            id = self._last_time_frame_num
            self._last_time_frame_num += 1

        # TODO: check that id is not present

        self.time_frames.append(TimeFrame(self, id))
        return self.time_frames[-1]

    def update_metadata(self, other: Self) -> None:
        """Updates missing parts of metadata from other data set.

        Generally, the other data set should contain the same data, but in
        different resolution.

        The resolution is basically the only kind of data that is changing
        from the conversion onwards. Therefore, it will not be updated here!
        """
        if not self._metadata_is_set:
            self.metadata = other.metadata.model_copy(deep=True)
            self._metadata_is_set = True

    def __str__(self) -> str:
        return f"Dataset({self.metadata}, {self.time_frames})"

    def __repr__(self) -> str:
        return self.__str__()


def create_file_name(channel: Channel, suffix: str = ".bcif") -> str:
    return (
        f"{channel.parent.parent.metadata.id}"
        f"_r{channel.parent.parent.metadata.resolution}"
        f"_tf{channel.parent.metadata.id}"
        f"_c{channel.metadata.id}{suffix}"
    )


class FileNameInfo(pydantic.BaseModel):
    data_set: str
    resolution: int
    time_frame: int
    channel: int
    suffix: str
    file_path: Path


def info_from_file_path(file_path: Path) -> FileNameInfo:
    file_name = file_path.name
    if file_name == "":
        raise RuntimeError(f"Encountered empty file name from: '{file_path}'")

    file_name_re = re.compile(
        r"(?P<set_id>.*)"
        r"_r(?P<resolution>\d+)"
        r"_tf(?P<time_frame>\d+)"
        r"_ch(?P<channel>\d+)\.(?P<suffix>.*)$"
    )

    match = re.match(file_name_re, file_name)
    if match is None:
        raise RuntimeError("File name does not satisfy format!")

    return FileNameInfo(
        data_set=match.group("set_id"),
        resolution=int(match.group("resolution")),
        time_frame=int(match.group("time_frame")),
        channel=int(match.group("channel")),
        suffix=match.group("suffix"),
        file_path=file_path,
    )
