from __future__ import annotations

from typing import TYPE_CHECKING

from volsegtools._model import MeshInfo
from volsegtools._storage.data_handle import DataHandle

if TYPE_CHECKING:
    import trimesh

    from volsegtools._core.computation_backend import ComputationBackend

    from .volsegtools._storage.time_frame import TimeFrame


class Mesh:
    def __init__(self, parent: TimeFrame, id: int):
        self.parent = parent
        self.metadata = MeshInfo(id=id)

    def set_data(self, mesh_data: trimesh.Trimesh, backend: ComputationBackend):
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
