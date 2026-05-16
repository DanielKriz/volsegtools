import logging
from typing import List
from pathlib import Path
from volsegtools._model.data_set import DataSet
from volsegtools._model.mesh_backend import MeshBackend
from volsegtools.abc.serializer import Serializer

vst_logger = logging.getLogger("volsegtools")

# TODO: all of the files below have similar code, I could make private generator
# for them to create closures in the specialized classes...


def serialize_to_obj(output_path, filename, mesh):
    file_path = f"{output_path}/{filename}.obj"
    mesh.export(file_path, "obj")
    return file_path


def serialize_to_ply(output_path, filename, mesh):
    file_path = f"{output_path}/{filename}.ply"
    mesh.export(file_path, "ply")
    return file_path


def serialize_to_stl(output_path, filename, mesh):
    file_path = f"{output_path}/{filename}.stl"
    mesh.export(file_path, "stl")
    return file_path


class MeshSerializer(Serializer):
    def __init__(self, mesh_serialization_fn):
        self.serialization_fn = mesh_serialization_fn

    async def serialize(self, data_set: DataSet, output_path: Path) -> List[Path]:
        output_files = []

        for frame in data_set.time_frames:
            for mesh in frame.meshes:
                mesh_data = mesh.handle.get_mesh(MeshBackend)

                file_name = "{}_r{}_tf{}_m{}".format(
                    data_set.metadata.id,
                    data_set.metadata.resolution,
                    frame.metadata.id,
                    mesh.metadata.id,
                )

                output = self.serialization_fn(
                    output_path,
                    file_name,
                    mesh_data,
                )
                vst_logger.info(f"... serialized into {output}")
                output_files.append(output)

        return output_files


class OBJSerializer(MeshSerializer):
    def __init__(self):
        super().__init__(serialize_to_obj)


class PLYSerializer(MeshSerializer):
    def __init__(self):
        super().__init__(serialize_to_ply)


class STLSerializer(MeshSerializer):
    def __init__(self):
        super().__init__(serialize_to_stl)
