from pathlib import Path

import logging

import trimesh

from volsegtools._core import AxisValues, DataKind
from volsegtools._model import DataSetInfo, PipelineContext
from volsegtools._processing.mesh_backend import MeshBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


class MeshConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["obj", "ply", "stl"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path) -> list[DataSet]:
        # TODO: we could include some algorithm for conversion of mesh to volume
        raise RuntimeError("Cannot convert mesh to volume")

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")
        mesh_data = trimesh.load_mesh(input_path)

        data_set_info = DataSetInfo(
            filename=input_path.name,
            resolution=0,
            axis_order=AxisValues(0, 1, 2),
            cell_size=AxisValues(0, 0, 0),
            origin=AxisValues(0, 0, 0),
            id=input_path.name,
            kind=DataKind.SEGMENTATION_MESH,
            lattice_shape=AxisValues(0, 0, 0),
        )
        data_set = DataSet(context.working_store, data_set_info)
        frame = data_set.add_time_frame()
        mesh = frame.add_mesh(0)
        mesh.set_data(mesh_data, MeshBackend)

        return [data_set]

    async def collect_annotations(self, input_path) -> None:
        pass

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError
