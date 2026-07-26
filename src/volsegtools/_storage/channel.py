from __future__ import annotations

from typing import TYPE_CHECKING

from volsegtools._model import ChannelInfo
from volsegtools._storage.data_handle import DataHandle

if TYPE_CHECKING:
    from volsegtools._core.computation_backend import ComputationBackend

    from .volsegtools._storage.time_frame import TimeFrame


class Channel:
    def __init__(self, parent: TimeFrame, id: int):
        self.parent = parent
        self.metadata = ChannelInfo(id=id)
        self._handle: DataHandle | None = None

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

