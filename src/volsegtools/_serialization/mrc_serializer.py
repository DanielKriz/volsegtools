import logging
from pathlib import Path
from typing import List

import mrcfile

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing import DaskBackend
from volsegtools._storage.data_set import DataSet
from volsegtools.abc import Serializer

vst_logger = logging.getLogger("volsegtools")


class MRCSerializer(Serializer):
    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> List[Path]:
        output_files = []

        for channel in data_set.flat_channel_iter():
            file_name = "{}_r{}_tf{}_ch{}.mrc".format(
                data_set.metadata.id,
                data_set.metadata.resolution,
                channel.parent.metadata.id,
                channel.metadata.id,
            )
            output_file_path = output_path / file_name
            vst_logger.info(f"... serialized into {output_file_path}")

            with mrcfile.new(output_file_path) as mrc:
                mrc.header.mapc = data_set.metadata.axis_order.x + 1
                mrc.header.mapr = data_set.metadata.axis_order.y + 1
                mrc.header.maps = data_set.metadata.axis_order.z + 1

                mrc.header.nx = data_set.metadata.lattice_shape.x
                mrc.header.ny = data_set.metadata.lattice_shape.y
                mrc.header.nz = data_set.metadata.lattice_shape.z

                mrc.header.cella.x = data_set.metadata.voxel_size.x
                mrc.header.cella.y = data_set.metadata.voxel_size.y
                mrc.header.cella.z = data_set.metadata.voxel_size.z

                mrc.header.nxstart = (
                    data_set.metadata.origin.x / data_set.metadata.voxel_size.x
                )
                mrc.header.nystart = (
                    data_set.metadata.origin.y / data_set.metadata.voxel_size.y
                )
                mrc.header.nzstart = (
                    data_set.metadata.origin.z / data_set.metadata.voxel_size.z
                )
                data = channel.handle.get_lattice(DaskBackend)
                data = data.astype("float32")
                mrc.set_data(data)

            output_files.append(output_file_path)

        return output_files
