from pathlib import Path

import ome_zarr.io
import ome_zarr.reader

from volsegtools._core import AxisValues, DataKind
from volsegtools._model import DataSetInfo, PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter


class NGFFConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["zarr"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        nodes = ome_zarr.reader.Reader(ome_zarr.io.ZarrLocation(input_path))()
        data_node = next(nodes)
        metadata = data_node.metadata
        data_arr = data_node.data[0]

        axis_order = {}
        current_order = ""
        for idx, ax in enumerate(metadata["axes"]):
            axis_order[ax["name"]] = idx
            if ax["name"] not in ["X", "Y", "Z"]:
                continue
            current_order += ax["name"]

        # TODO: this is second time using this, it should be move to upper
        # module.
        reordering = tuple(current_order.find(ax) for ax in "XYZ")

        # The 0 is for the 0th resolution
        voxel_size_info = metadata["coordinateTransformations"][0][0]["scale"]

        info = DataSetInfo(
            filename=input_path.name,
            resolution=0,
            axis_order=AxisValues(0, 1, 2),
            voxel_size=AxisValues(
                100 * voxel_size_info[axis_order["x"]],
                100 * voxel_size_info[axis_order["y"]],
                100 * voxel_size_info[axis_order["z"]],
            ),
            id=input_path.name,
            kind=DataKind.VOLUME,
            lattice_shape=AxisValues(
                data_arr.shape[axis_order["x"]],
                data_arr.shape[axis_order["y"]],
                data_arr.shape[axis_order["z"]],
            ),
        )
        data_set = DataSet(context.working_store, info)

        # If we have time frames then we have to iterate over them
        time_frames = data_arr if data_arr.ndim > 4 else [data_arr]

        for frame_data in time_frames:
            for idx, channel_data in enumerate(frame_data):
                transposed = channel_data.transpose(reordering)
                frame = data_set.add_time_frame()
                channel = frame.add_channel(idx)
                transposed = transposed.rechunk("auto")
                channel.set_data(transposed, DaskBackend)

        return [data_set]

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        raise await self.convert_volume(input_path, context)

    async def collect_annotations(self, input_path, context) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError
