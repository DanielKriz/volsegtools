from pathlib import Path
from typing import List
import dask.array as da

import logging
import ciftools.serialization

from volsegtools._model.dask_backend import DaskBackend
from volsegtools.abc import Converter
from volsegtools._core import DataKind, Vector3
from volsegtools._model.working_store import WorkingStore
from volsegtools._model.data_set import DataSet, DataSetInfo

vst_logger = logging.getLogger("volsegtools")


class CIFConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["cif", "bcif"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(self, input_path: Path) -> List[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        with open(input_path, "rb") as file:
            cif_data = ciftools.serialization.loads(file.read(), lazy=False)

        data_set = None
        for block in cif_data.data_blocks:
            if block.header != "VOLUME":
                continue

            metadata = block.categories["volume_data_3d_info"]
            data = block.categories["volume_data_3d"]["values"].as_ndarray()
            data = data.reshape(
                (
                    metadata["sample_count[0]"].get_integer(0),
                    metadata["sample_count[1]"].get_integer(0),
                    metadata["sample_count[2]"].get_integer(0),
                )
            )
            data = da.from_array(data)
            data_set_info = DataSetInfo(
                filename=input_path.name,
                resolution=0,
                axis_order=Vector3(
                    metadata["axis_order[0]"].get_float(0),
                    metadata["axis_order[1]"].get_float(0),
                    metadata["axis_order[2]"].get_float(0),
                ),
                voxel_size=Vector3(
                    metadata["spacegroup_cell_size[0]"].get_float(0),
                    metadata["spacegroup_cell_size[1]"].get_float(0),
                    metadata["spacegroup_cell_size[2]"].get_float(0),
                ),
                origin=Vector3(
                    metadata["origin[0]"].get_float(0),
                    metadata["origin[1]"].get_float(0),
                    metadata["origin[2]"].get_float(0),
                ),
                id=input_path.stem,
                kind=DataKind.VOLUME,
                lattice_shape=Vector3(
                    data.shape[0],
                    data.shape[1],
                    data.shape[2],
                ),
            )

            data_set = DataSet(WorkingStore.instance.data_store, data_set_info)
            frame = data_set.add_time_frame()
            channel = frame.add_channel(0)
            channel.set_data(data, DaskBackend)

        return [data_set] if data_set is not None else []

    async def convert_segmentation(self, input_path: Path) -> List[DataSet]:
        data_sets = await self.convert_volume(input_path)
        for ds in data_sets:
            ds.metadata.kind = DataKind.SEGMENTATION_VOLUME
        return data_sets

    async def collect_annotations(self, input_path) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path) -> None:
        raise NotImplementedError
