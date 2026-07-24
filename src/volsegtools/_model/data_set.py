import re
from pathlib import Path
from typing import Optional, Self

import pydantic
import zarr
import zarr.storage

from volsegtools._model.data_handle import DataHandle
from volsegtools._model.metadata import (
    DataSetInfo,
    TimeFrameInfo,
    DescriptiveStatistics,
    ChannelInfo,
    MeshInfo,
)

from volsegtools.abc import ComputationBackend


class DataSet:
    def __init__(
        self, store: zarr.storage.StoreLike, metadata: Optional[DataSetInfo] = None
    ):
        self.store = store
        if metadata:
            self._metadata_is_set = True
            self.metadata = metadata
        else:
            self._metadata_is_set = False
            self.metadata = DataSetInfo()
        self.time_frames = []
        self._last_time_frame_num = 0

    @property
    def zarr_path(self):
        if self.metadata.kind.is_segmentation():
            root = Path("segmentation_data")
        else:
            root = Path("volume_data")
        return root / self.metadata.id / f"resolution_{self.metadata.resolution}"

    def __iter__(self):
        for frame in self.time_frames:
            yield frame

    def flat_channel_iter(self):
        for frame in self.time_frames:
            for channel in frame:
                yield channel

    def add_time_frame(self, id=-1):
        if id == -1:
            id = self._last_time_frame_num
            self._last_time_frame_num += 1

        # TODO: check that id is not present

        self.time_frames.append(TimeFrame(self, id))
        return self.time_frames[-1]

    def update_metadata(self, other: Self):
        """Updates missing parts of metadata from other data set.

        Generally, the other data set should contain the same data, but in
        different resolution.

        The resolution is basically the only kind of data that is changing
        from the conversion onwards. Therefore, it will not be updated here!
        """
        if not self._metadata_is_set:
            self.metadata = other.metadata.model_copy(deep=True)
            self._metadata_is_set = True

    def __str__(self):
        return f"DataSet({self.metadata}, {self.time_frames})"

    def __repr__(self):
        return self.__str__()


class TimeFrame:
    def __init__(self, parent: DataSet, id):
        self.parent = parent
        self.channels = []
        self.meshes = []
        self.metadata = TimeFrameInfo(id=id)

    @property
    def data_set(self):
        return self.parent

    @property
    def zarr_path(self):
        return self.data_set.zarr_path / f"time_frame_{self.metadata.id}"

    def add_channel(self, id):
        self.channels.append(Channel(self, id))
        return self.channels[-1]

    def add_mesh(self, id):
        self.meshes.append(Mesh(self, id))
        return self.meshes[-1]

    def __iter__(self):
        for channel in self.channels:
            yield channel

    def __str__(self):
        return f"TimerFrame({self.metadata}, {self.channels}, {self.meshes})"

    def __repr__(self):
        return self.__str__()


class Mesh:
    def __init__(self, parent: TimeFrame, id: int):
        self.parent = parent
        self.metadata = MeshInfo(id=id)

    def set_data(self, mesh_data, backend):
        self.handle = DataHandle(
            self.data_set.store, self.zarr_path, self.data_set.metadata.kind
        )
        self.handle.store_data(mesh_data, backend)

    @property
    def zarr_path(self):
        return self.time_frame.zarr_path / f"mesh_{self.metadata.id}"

    @property
    def data_set(self):
        return self.parent.parent

    @property
    def time_frame(self):
        return self.parent

    def __str__(self):
        return f"Mesh({self.metadata})"

    def __repr__(self):
        return self.__str__()


class Channel:
    def __init__(self, parent: TimeFrame, id: int):
        self.parent = parent
        self.metadata = ChannelInfo(id=id)
        self._handle: Optional[DataHandle] = None

    @property
    def handle(self) -> DataHandle:
        if self._handle is None:
            raise RuntimeError("There are not data in the channel")
        return self._handle

    @handle.setter
    def handle(self, new_handle):
        self._handle = new_handle

    def set_data(self, data, backend: ComputationBackend):
        self.handle = DataHandle(
            self.data_set.store, self.zarr_path, self.data_set.metadata.kind
        )
        self.handle.store_data(data, backend)
        self.metadata.statistics = self.handle.calculate_statistics(backend)

    @property
    def zarr_path(self):
        return self.time_frame.zarr_path / f"channel_{self.metadata.id}"

    @property
    def data_set(self):
        return self.parent.parent

    @property
    def time_frame(self):
        return self.parent

    def __str__(self):
        return f"Channel({self.metadata})"

    def __repr__(self):
        return self.__str__()


class DataSetDefaultDict(dict):
    def __missing__(self, key: int):
        if not isinstance(key, int):
            raise RuntimeError("Keys to data set dictionary have to be int")

        new_info = DataSetInfo(resolution=key)
        new_data_set = DataSet(new_info)

        self[key] = new_data_set
        return new_data_set


def create_file_name(channel: Channel, suffix: str = ".bcif"):
    return "{}_r{}_tf{}_c{}{}".format(
        channel.parent.parent.metadata.id,
        channel.parent.parent.metadata.resolution,
        channel.parent.metadata.id,
        channel.metadata.id,
        suffix,
    )


class FileNameInfo(pydantic.BaseModel):
    data_set: str
    resolution: int
    time_frame: int
    channel: int
    suffix: str
    file_path: Path


def info_from_file_path(file_path: Path):
    file_name = file_path.name
    if file_name == "":
        raise RuntimeError(f"Encountered empty file name from: '{file_path}'")

    file_name_re = r"(?P<set_id>.*)_r(?P<resolution>\d+)_tf(?P<time_frame>\d+)_ch(?P<channel>\d+)\.(?P<suffix>.*)$"

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
