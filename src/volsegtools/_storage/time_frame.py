from __future__ import annotations

from typing import TYPE_CHECKING

from volsegtools._model import TimeFrameInfo
from volsegtools._storage.channel import Channel
from volsegtools._storage.mesh import Mesh

if TYPE_CHECKING:
    from .volsegtools._storage.data_set import DataSet


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
        yield from self.channels

    def __str__(self):
        return f"TimerFrame({self.metadata}, {self.channels}, {self.meshes})"

    def __repr__(self):
        return self.__str__()
