from pathlib import Path
from typing import List
import logging
import sfftkrw as sff

from volsegtools._processing.mesh_backend import MeshBackend
from volsegtools._processing.numpy_backend import NumPyBackend
from volsegtools.abc import Converter
from volsegtools._core import DataKind, Vector3
from volsegtools._model.working_store import WorkingStore
from volsegtools._model.data_set import DataSet, DataSetInfo

vst_logger = logging.getLogger("volsegtools")


class SFFConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["sff", "hff"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        raise RuntimeError("SFF does not support normal volumes")

    async def convert_segmentation(self, input_path: Path) -> List[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        seg = sff.SFFSegmentation.from_file(str(input_path))

        # Determine whether it contains volumes, meshes, or both

        # This is going to work only if there are not multiple segmentations
        # in a single file...
        lshape = seg.lattice_list[0].data_array.shape

        data_set_info = DataSetInfo(
            filename=input_path.name,
            resolution=0,
            axis_order=Vector3(0, 1, 2),
            voxel_size=Vector3(10, 10, 10),
            origin=Vector3(0, 0, 0),
            id=input_path.name,
            kind=DataKind.SEGMENTATION_MASK,
            lattice_shape=Vector3(lshape[0], lshape[1], lshape[2]),
        )
        data_set = DataSet(WorkingStore.instance.data_store, data_set_info)
        frame = data_set.add_time_frame()

        for idx, lattice in enumerate(seg.lattice_list):
            channel = frame.add_channel(idx)
            channel.set_data(lattice.data_array, NumPyBackend)

        for segment in seg.segment_list:
            if not segment.mesh_list:
                continue
            for idx, mesh_data in segment.mesh_list:
                mesh = frame.add_mesh(idx)
                # TODO: this needs better handling for cases when we do not
                # have faces...
                mesh.set_data(mesh_data, MeshBackend)

        return [data_set]

    async def collect_annotations(self, input_path) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError
