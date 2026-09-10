from pathlib import Path

import logging

import ciftools.serialization
import dask.array as da

from volsegtools._core import AxisValues, DataKind
from volsegtools._model import DatasetMetadata, PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import Dataset
from volsegtools.abc import Converter

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

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[Dataset]:
        vst_logger.info(f"... converting '{input_path}'")

        with Path.open(input_path, "rb") as file:
            cif_data = ciftools.serialization.loads(file.read(), lazy=False)

        data_set = None
        for block in cif_data.data_blocks:
            if block.header != "VOLUME" and block.header != "EM":
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
            data_set_info = DatasetMetadata(
                filename=input_path.name,
                resolution=0,
                axis_order=AxisValues(
                    metadata["axis_order[0]"].get_float(0),
                    metadata["axis_order[1]"].get_float(0),
                    metadata["axis_order[2]"].get_float(0),
                ),
                cell_size=AxisValues(
                    metadata["spacegroup_cell_size[0]"].get_float(0),
                    metadata["spacegroup_cell_size[1]"].get_float(0),
                    metadata["spacegroup_cell_size[2]"].get_float(0),
                ),
                origin=AxisValues(
                    metadata["origin[0]"].get_float(0),
                    metadata["origin[1]"].get_float(0),
                    metadata["origin[2]"].get_float(0),
                ),
                id=input_path.stem,
                kind=DataKind.VOLUME,
                lattice_shape=AxisValues(
                    data.shape[0],
                    data.shape[1],
                    data.shape[2],
                ),
            )

            data_set = Dataset(context.working_store, data_set_info)
            frame = data_set.add_time_frame()
            channel = frame.add_channel(0)
            channel.set_data(data, DaskBackend)

        return [data_set] if data_set is not None else []

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[Dataset]:
        data_sets = await self.convert_volume(input_path, context)
        for ds in data_sets:
            ds.metadata.kind = DataKind.SEGMENTATION_VOLUME
        return data_sets

    async def collect_annotations(self, input_path, context) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError
