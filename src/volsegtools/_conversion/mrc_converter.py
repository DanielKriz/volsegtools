from pathlib import Path

import logging

import dask.array as da
import mrcfile

from volsegtools._core import AxisValues, DataKind
from volsegtools._core.axis_values import create_reorder_permutation
from volsegtools._model import DataSetInfo, PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


# TODO: Make this a template method, where most of the logging is going to be
# handled by the base class.


class MRCConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["mrc", "map", "cpp4"]

    @property
    def supports_compression(self) -> bool:
        return True

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        mrc = mrcfile.mmap(input_path, "r")
        if mrc.data is None or mrc.header is None:
            raise RuntimeError("Failed to read data from MAP file")

        order = (
            int(mrc.header.maps) - 1,
            int(mrc.header.mapr) - 1,
            int(mrc.header.mapc) - 1,
        )

        array = da.from_array(mrc.data, chunks=(256, 256, 256))
        array = array.transpose(create_reorder_permutation(order))

        data_set_info = MRCConverter._collect_data_set_metadata(
            input_path,
            mrc.header,
            array,
            DataKind.VOLUME,
        )
        mrc.close()

        data_set = DataSet(context.working_store, data_set_info)
        frame = data_set.add_time_frame()

        channel = frame.add_channel(0)
        channel.set_data(array, DaskBackend)
        return [data_set]

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        data_sets = await self.convert_volume(input_path, context)
        for ds in data_sets:
            ds.metadata.kind = DataKind.SEGMENTATION_VOLUME
        return data_sets

    async def collect_annotations(self, input_path, context) -> None:
        pass

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError

    @staticmethod
    def _collect_data_set_metadata(file, mrc_header, array, kind) -> DataSetInfo:

        original_order = AxisValues(
            int(mrc_header.maps) - 1,
            int(mrc_header.mapr) - 1,
            int(mrc_header.mapc) - 1,
        )

        lattice_shape = AxisValues(*array.shape)

        cell_size = AxisValues(
            float(mrc_header.cella.x),
            float(mrc_header.cella.y),
            float(mrc_header.cella.z),
        )

        origin = AxisValues(
            float(mrc_header.origin.x),
            float(mrc_header.origin.y),
            float(mrc_header.origin.z),
        )

        # We have to completely remove the suffixes to get the id.
        filename = Path(str(file).strip("".join(file.suffixes))).stem

        return DataSetInfo(
            filename=str(file),
            resolution=0,
            axis_order=original_order,
            cell_size=cell_size,
            origin=origin,
            id=filename,
            kind=kind,
            lattice_shape=lattice_shape,
        )
