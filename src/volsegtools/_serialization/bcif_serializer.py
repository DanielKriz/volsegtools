from pathlib import Path
from typing import Collection, List
from ciftools.binary.encoder import BYTE_ARRAY
from ciftools.models.writer import CIFCategoryDesc as CategoryDesc
from ciftools.models.writer import CIFFieldDesc as Field

import ciftools
import ciftools.serialization
import numpy as np

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._storage import Channel, DataSet
from volsegtools._processing import NumPyBackend

from volsegtools.abc import Serializer


class BCIFSerializer(Serializer):
    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> List[Path]:
        # This is currently working only for volumes!
        output_files = []
        for channel in data_set.flat_channel_iter():
            writer = ciftools.serialization.create_binary_writer()

            # We have to create the SERVER category, because it is required, we
            # just have to say that it is a box
            writer.start_data_block("SERVER")
            writer.write_category(DensityServerResultDesc, [np.arange(0)])

            writer.start_data_block("VOLUME")
            writer.write_category(VolumeData3DInfoDescNew, [channel])

            data = channel.handle.get_lattice(NumPyBackend)

            writer.write_category(VolumeData3DDesc, [np.ravel(data, order="F")])

            file_name = "{}_r{}_tf{}_ch{}.bcif".format(
                data_set.metadata.id,
                data_set.metadata.resolution,
                channel.parent.metadata.id,
                channel.metadata.id,
            )
            output_file_path = output_path / file_name
            output_file_path.write_bytes(writer.encode())
            output_files.append(output_file_path)
        return output_files


class VolumeData3DInfoDescNew(CategoryDesc):
    name = "volume_data_3d_info"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(channel: Channel) -> Collection[Field]:
        def volume_server_encoder(_):
            return BYTE_ARRAY

        data_set = channel.parent.parent

        return [
            Field.strings(
                name="name",
                value=lambda d, i: str(data_set.metadata.id),
            ),
            Field.numbers(
                name="axis_order[0]",
                value=lambda d, i: data_set.metadata.axis_order.x,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="axis_order[1]",
                value=lambda d, i: data_set.metadata.axis_order.y,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="axis_order[2]",
                value=lambda d, i: data_set.metadata.axis_order.z,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="origin[0]",
                value=lambda d, i: data_set.metadata.origin.x,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="origin[1]",
                value=lambda d, i: data_set.metadata.origin.y,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="origin[2]",
                value=lambda d, i: data_set.metadata.origin.z,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="dimensions[0]",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="dimensions[1]",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="dimensions[2]",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_rate",
                value=lambda d, i: 2**data_set.metadata.resolution,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[0]",
                value=lambda d, i: data_set.metadata.lattice_shape.x,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[1]",
                value=lambda d, i: data_set.metadata.lattice_shape.y,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[2]",
                value=lambda d, i: data_set.metadata.lattice_shape.z,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="spacegroup_number",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="spacegroup_cell_size[0]",
                value=lambda d, i: data_set.metadata.voxel_size.x,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_size[1]",
                value=lambda d, i: data_set.metadata.voxel_size.y,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_size[2]",
                value=lambda d, i: data_set.metadata.voxel_size.z,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[0]",
                value=lambda d, i: 90,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[1]",
                value=lambda d, i: 90,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[2]",
                value=lambda d, i: 90,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="mean_source",
                value=lambda d, i: channel.metadata.statistics.mean,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="mean_sampled",
                value=lambda d, i: channel.metadata.statistics.mean,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="sigma_source",
                value=lambda d, i: channel.metadata.statistics.std,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="sigma_sampled",
                value=lambda d, i: channel.metadata.statistics.std,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="min_source",
                value=lambda d, i: channel.metadata.statistics.min,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="min_sampled",
                value=lambda d, i: channel.metadata.statistics.min,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="max_source",
                value=lambda d, i: channel.metadata.statistics.max,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="max_sampled",
                value=lambda d, i: channel.metadata.statistics.max,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
        ]


class DensityServerResultDesc(CategoryDesc):
    name = "density_server_result"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(data) -> Collection[Field]:
        return [
            Field.strings(name="query_type", value=lambda d, i: "box"),
        ]


class VolumeData3DDesc(CategoryDesc):
    name = "volume_data_3d"

    @staticmethod
    def get_row_count(data: np.ndarray) -> int:
        return data.size

    @staticmethod
    def get_field_descriptors(data: np.ndarray) -> Collection[Field]:
        def volume_server_encoder(_):
            return BYTE_ARRAY

        return [
            Field.number_array(
                name="values",
                array=lambda volume: volume,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
        ]
