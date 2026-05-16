import numpy as np
from pathlib import Path
from typing import Union, Self, Any, Optional
import zarr
import zarr.storage
import trimesh

from volsegtools._core.data_kind import DataKind
from volsegtools._model.working_store import WorkingStore
from volsegtools._model.computation_backend import ComputationBackend

class DataHandle:
    def __init__(
        self, 
        store: zarr.storage.StoreLike,
        zarr_path: Path, 
        data_kind: DataKind, 
    ):
        self.store = store
        self.zarr_path: Path = zarr_path
        self.data_kind: DataKind = data_kind
        self._zarr_object: Optional[zarr.Group] = None

    @property
    def attributes(self) -> dict:
        return dict(self.zarr_object.attrs)

    def update_attributes(self, new_attrs) -> None:
        return self.zarr_object.attrs.update(new_attrs)

    @property
    def zarr_object(self) -> Union[zarr.Array, zarr.Group]:
        if self._zarr_object is None:
            self._zarr_object = zarr.open_group(
                self.store,
                path=str(self.zarr_path)
            )
        return self._zarr_object

    def store_data(self, data, backend, compressor = None):
        group = WorkingStore.instance.root_group.require_group(str(self.zarr_path))
        if isinstance(data, trimesh.Trimesh):
            self.require_kind(DataKind.SEGMENTATION_MESH)

            # We have to store components of the mesh separately, with this we
            # are then able to reconstruct it.

            group.require_array(
                name="vertices",
                data=data.vertices,
                dtype=float, # from trimesh documentation
            )
            group.require_array(
                name="faces",
                data=data.faces,
                dtype=np.int64, # from trimesh documentation
            )
            group.require_array(
                name="normals",
                data=data.face_normals,
                dtype=np.float64, # from trimesh documentation
            )
        else:
            self.require_kind(
                DataKind.SEGMENTATION_MASK,
                DataKind.SEGMENTATION_VOLUME,
                DataKind.VOLUME
            )
            chunks = data.chunksize if hasattr(data, "chunksize") else "auto"
            arr = group.require_array(
                name="data",
                shape=data.shape,
                dtype=data.dtype,
                chunks=chunks,
                overwrite=True,
            )
            backend.store_to_zarr(data, arr)

    def require_kind(self, *allowed_kinds: DataKind, inverse=False) -> None:
        result = self.data_kind not in allowed_kinds
        result = not result if inverse else result
        if result:
            raise RuntimeError(
                "Cannot proceed. Expected one of {}, got {}".format(
                    allowed_kinds,
                    self.data_kind,
                )
            )

    def get_lattice(self, backend: ComputationBackend) -> Any:
        self.require_kind(
            DataKind.VOLUME, 
            DataKind.SEGMENTATION_MASK, 
            DataKind.SEGMENTATION_VOLUME
        )

        return backend.load_from_zarr(self.zarr_object["data"])


    def get_mesh(self) -> trimesh.Trimesh:
        self.require_kind(DataKind.SEGMENTATION_MESH)

        if not isinstance(self.zarr_object, zarr.Group):
            raise ValueError("Expected zarr group, got array")

        if not ("vertices" in self.zarr_object and "faces" in self.zarr_object):
            raise ValueError("Zarr group does not contain mesh data")

        vertices = self.zarr_object["vertices"][:]
        faces = self.zarr_object["faces"][:]

        normals = None
        if "normals" in self.zarr_object:
            normals = self.zarr_object["normals"][:]

        if not isinstance(vertices, zarr.Array):
            raise TypeError("Vertices are not saved in an array")

        if not isinstance(faces, zarr.Array):
            raise TypeError("Faces are not saved in an array")

        if normals is not None and not isinstance(normals, zarr.Array):
            raise TypeError("Normals are not saved in an array")

        return trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            normals=normals,
            process=False,
        )

    def calculate_statistics(self, backend):
        return backend.calculate_statistics(self.zarr_object["data"])

    def close(self) -> None:
        """Closes the underlying Zarr store, if it is opened."""

        if self._zarr_object is not None:
            pass

    def __enter__(self) -> Self:
        # TODO: it should open the store here
        return self

    def __exit__(self) -> None:
        self.close()

    # Given that the lattice is holding a data lattice, we might need to
    # do some allocation of memory for some backend before we are able to
    # actually load the data => allow to access some metadata about the zarr
    # object before actually working with it

    @property
    def shape(self) -> tuple:
        self.require_kind(DataKind.SEGMENTATION_MESH, inverse=True)
        arr = self.zarr_object["data"]
        if not isinstance(arr, zarr.Array):
            raise TypeError(f"Expected array, got {arr}")

        return arr.shape

    @property
    def dtype(self):
        self.require_kind(DataKind.SEGMENTATION_MESH, inverse=True)
        arr = self.zarr_object["data"]
        if not isinstance(arr, zarr.Array):
            raise TypeError(f"Expected array, got {arr}")

        return arr.dtype

    @property
    def nbytes(self):
        self.require_kind(DataKind.SEGMENTATION_MESH, inverse=True)
        arr = self.zarr_object["data"]
        if not isinstance(arr, zarr.Array):
            raise TypeError(f"Expected array, got {arr}")

        return arr.nbytes
