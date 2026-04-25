import re
from pathlib import Path
from typing import Optional, Self

import pydantic
from numpy.typing import ArrayLike
from pydantic import Field
from volsegtools._core.lattice_kind import LatticeKind
from volsegtools._core.vector import Vector3
from volsegtools._model.metadata import DescriptiveStatistics
from volsegtools._model.opaque_data_handle import OpaqueDataHandle
from volsegtools._model.storing_parameters import StoringParameters
from volsegtools._model.working_store import WorkingStore


class DataSetInfo(pydantic.BaseModel):
    filename: str = "Unknown File"
    resolution: int = -1
    axis_order: Vector3 = Field(default_factory=Vector3)
    voxel_size: Vector3 = Field(default_factory=Vector3)
    origin: Vector3 = Field(default_factory=Vector3)
    id: str = "Unknown"
    # kind: LatticeKind = Field(default_factory=LatticeKind)
    kind: LatticeKind = LatticeKind.VOLUME
    lattice_shape: Vector3 = Field(default_factory=Vector3)


class TimeFrameInfo(pydantic.BaseModel):
    id: int = -1


class ChannelInfoV2(pydantic.BaseModel):
    id: int = -1
    statistics: DescriptiveStatistics = Field(default_factory=DescriptiveStatistics)


class DataSet:
    def __init__(self, metadata: Optional[DataSetInfo] = None):
        if metadata:
            self._metadata_is_set = True
            self.metadata = metadata
        else:
            self._metadata_is_set = False
            self.metadata = DataSetInfo()
        self.time_frames = []
        self._last_time_frame_num = 0

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
        self.metadata = TimeFrameInfo(id=id)

    def add_channel(self, data, id):
        self.channels.append(Channel(self, data, id))

    def __iter__(self):
        for channel in self.channels:
            yield channel

    def __str__(self):
        return f"TimerFrame({self.metadata}, {self.channels})"

    def __repr__(self):
        return self.__str__()


class Channel:
    def __init__(self, parent: TimeFrame, data: ArrayLike, id: int):
        self.parent = parent
        self.metadata = ChannelInfoV2(id=id)

        self._data = None
        self.data = data

    @property
    def data(self) -> OpaqueDataHandle:
        return self._data

    @data.setter
    def data(self, data_array: ArrayLike):
        if isinstance(data_array, OpaqueDataHandle):
            self._data = data_array
            return

        self._data = WorkingStore.instance.store_lattice_time_frame(
            StoringParameters(
                storage_dtype=data_array.dtype,
                resolution_level=self.parent.parent.metadata.resolution,
                time_frame=self.parent.metadata.id,
                channel=self.metadata.id,
                lattice_kind=self.parent.parent.metadata.kind,
            ),
            data_array,
            self.parent.parent.metadata.id,
        )
        self.metadata.statistics = self._data.calculate_statistics()

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
