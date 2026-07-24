import zarr
import trimesh

from typing import Any

from volsegtools.abc import ComputationBackend
from volsegtools._model.data_set import DescriptiveStatistics
from volsegtools.typing import ZarrObject


class MeshBackend(ComputationBackend):
    @staticmethod
    def get_name() -> str:
        return "mesh"

    @staticmethod
    def load_from_zarr(zarr_object: ZarrObject) -> trimesh.Trimesh:
        if isinstance(zarr_object, zarr.Array):
            raise RuntimeError("Cannot load mesh from array")

        return trimesh.Trimesh(
            vertices=zarr_object["vertices"],
            faces=zarr_object["faces"],
            face_normals=zarr_object["normals"],
        )

    @staticmethod
    def calculate_statistics(_: Any) -> DescriptiveStatistics:
        return NotImplemented()

    @staticmethod
    def store_to_zarr(array: trimesh.Trimesh, target_zarr: ZarrObject) -> None:
        # Alias for better work
        mesh = array
        if isinstance(target_zarr, zarr.Array):
            raise RuntimeError("Cannot store mesh to array")

        # types and dimenesions are based on documentation:
        # https://trimesh.org/trimesh.html#trimesh.Trimesh
        vertices = target_zarr.require_array(
            "vertices",
            shape=mesh.vertices.shape,
            dtype=mesh.vertices.dtype,
        )
        faces = target_zarr.require_array(
            "faces",
            shape=mesh.faces.shape,
            dtype=mesh.faces.dtype,
        )
        normals = target_zarr.require_array(
            "normals",
            shape=mesh.face_normals.shape,
            dtype=mesh.face_normals.dtype,
        )

        vertices[:] = mesh.vertices[:]
        faces[:] = mesh.faces[:]
        normals[:] = mesh.face_normals[:]
