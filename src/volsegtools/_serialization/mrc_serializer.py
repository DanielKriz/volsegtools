from pathlib import Path

import logging

from mrcfile.utils import mode_from_dtype

import dask.array as da
import mrcfile

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing import DaskBackend
from volsegtools._storage import Dataset
from volsegtools.abc import Serializer

vst_logger = logging.getLogger("volsegtools")


class MRCSerializer(Serializer):
    async def serialize(
        self,
        data_set: Dataset,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]:
        output_files = []

        for channel in data_set.flat_channel_iter():
            file_name = (
                f"{data_set.metadata.id}"
                f"_r{data_set.metadata.resolution}"
                f"_tf{channel.parent.metadata.id}"
                f"_ch{channel.metadata.id}.mrc"
            )
            output_file_path = output_path / file_name
            vst_logger.info(f"... serialized into {output_file_path}")

            data = channel.handle.get_lattice(DaskBackend)
            data = data.transpose(data_set.metadata.axis_order.to_tuple(dtype=int))

            with mrcfile.new_mmap(
                output_file_path,
                shape=data.shape,
                mrc_mode=mode_from_dtype(data.dtype),
                overwrite=True,
            ) as mrc:
                da.store(data, mrc.data, lock=False)

                mrc.set_volume()

                mrc.header.maps = data_set.metadata.axis_order.x + 1
                mrc.header.mapr = data_set.metadata.axis_order.y + 1
                mrc.header.mapc = data_set.metadata.axis_order.z + 1

                mrc.header.cella.x = data_set.metadata.cell_size.x
                mrc.header.cella.y = data_set.metadata.cell_size.y
                mrc.header.cella.z = data_set.metadata.cell_size.z

                mrc.header.nxstart = data_set.metadata.origin.x
                mrc.header.nystart = data_set.metadata.origin.y
                mrc.header.nzstart = data_set.metadata.origin.z

                mrc.update_header_stats()

            output_files.append(output_file_path)

        return output_files
