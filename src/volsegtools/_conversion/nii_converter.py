from pathlib import Path
from typing import List

import logging
import nibabel as nib

from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._core import DataKind, Vector3, WorkingStore
from volsegtools._model import DataSetInfo
from volsegtools._storage import DataSet

from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


class NiiConverter(Converter):
    @property
    def supported_suffixes(self):
        # Chosen from the NiBabel testing files
        # https://github.com/nipy/nibabel/tree/master/nibabel/tests/data
        return ["mnc", "nii", "PAR", "rst", "dcm", "HEAD", "tck", "trk"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        # TODO: we could include some algorithm for conversion of mesh to volume
        raise RuntimeError("Cannot convert mesh to volume")

    async def convert_segmentation(self, input_path: Path) -> List[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        nibabel_img = nib.load(str(input_path))
        data = nibabel_img.get_fdata()

        data_set_info = DataSetInfo(
            filename=input_path.name,
            resolution=0,
            axis_order=Vector3(0, 1, 2),
            voxel_size=Vector3(10, 10, 10),
            origin=Vector3(0, 0, 0),
            id=input_path.name,
            kind=DataKind.SEGMENTATION_VOLUME,
            lattice_shape=Vector3(data.shape[0], data.shape[1], data.shape[2]),
        )
        data_set = DataSet(WorkingStore.instance.data_store, data_set_info)
        frame = data_set.add_time_frame()
        channel = frame.add_channel(0)
        channel.set_data(data, NumPyBackend)

        return [data_set]

    async def collect_annotations(self, input_path) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError
