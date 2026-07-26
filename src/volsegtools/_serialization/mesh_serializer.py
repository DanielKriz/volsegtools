import logging
from pathlib import Path

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing import MeshBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Serializer

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

    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]:
        output_files = []

        for frame in data_set.time_frames:
            for mesh in frame.meshes:
                mesh_data = mesh.handle.get_mesh(MeshBackend)

                file_name = (
                    f"{data_set.metadata.id}"
                    f"_r{data_set.metadata.resolution}"
                    f"_tf{frame.metadata.id}"
                    f"_m{mesh.metadata.id}.mrc"
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
