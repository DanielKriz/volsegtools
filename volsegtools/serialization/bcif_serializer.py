import sys
import numpy as np
import dataclasses

from pathlib import Path
from typing import Collection

import ciftools
import ciftools.serialization
from ciftools.models.writer import (
    CIFCategoryDesc as CategoryDesc,
    CIFFieldDesc as Field,
)
from ciftools.binary.writer import EncodedCIFData
from ciftools.binary.decoder import ByteArrayEncoding, DataType
from ciftools.binary.encoder import BinaryCIFEncoder, DataTypeEnum, BYTE_ARRAY

from volsegtools.abc import Serializer
from volsegtools.model import (
    ChannelMetadata,
    OriginalTimeFrameMetadata,
    TimeFrameMetadata,
)


@dataclasses.dataclass
class VolumeDataBatch:
    original_metadata: OriginalTimeFrameMetadata
    target_metadata: TimeFrameMetadata
    channel: ChannelMetadata


class DummyVolumeServerEncoder(BinaryCIFEncoder):
    def encode(self, data: np.ndarray) -> EncodedCIFData:
        data_type: DataTypeEnum = DataType.from_dtype(data.dtype)
        encoding: ByteArrayEncoding = {
            "kind": "VolumeServer",
            "type": data_type,
        }

        bo = data.dtype.byteorder
        if bo == ">" or (bo == "=" and sys.byteorder == "big"):
            new_bo = data.dtype.newbyteorder("<")
            data = np.array(data, dtype=new_bo)

        return EncodedCIFData(data=data.tobytes(), encoding=[encoding])


DUMMY_VOLUME_SERVER = DummyVolumeServerEncoder()


class VolumeData3DInfoDesc(CategoryDesc):
    name = "volume_data_3d_info"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(data: VolumeDataBatch) -> Collection[Field]:
        volume_server_encoder = lambda _: BYTE_ARRAY
        return [
            Field.strings(
                name = "name",
                value = lambda d, i: str(data.target_metadata.id),
            ),

            Field.numbers(
                name = "axis_order[0]",
                value = lambda d, i: data.original_metadata.axis_order.x,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "axis_order[1]",
                value = lambda d, i: data.original_metadata.axis_order.y,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "axis_order[2]",
                value = lambda d, i: data.original_metadata.axis_order.z,
                encoder = volume_server_encoder,
                dtype="i4",
            ),

            Field.numbers(
                name = "origin[0]",
                value = lambda d, i: data.target_metadata.origin.x,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "origin[1]",
                value = lambda d, i: data.target_metadata.origin.y,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "origin[2]",
                value = lambda d, i: data.target_metadata.origin.z,
                encoder = volume_server_encoder,
                dtype="i4",
            ),

            Field.numbers(
                name = "dimensions[0]",
                value = lambda d, i: 1,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "dimensions[1]",
                value = lambda d, i: 1,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "dimensions[2]",
                value = lambda d, i: 1,
                encoder = volume_server_encoder,
                dtype="i4",
            ),

            Field.numbers(
                name = "sample_rate",
                value = lambda d, i: data.target_metadata.resolution,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "sample_count[0]",
                value = lambda d, i: data.target_metadata.lattice_dimensions.x,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "sample_count[1]",
                value = lambda d, i: data.target_metadata.lattice_dimensions.y,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "sample_count[2]",
                value = lambda d, i: data.target_metadata.lattice_dimensions.z,
                encoder = volume_server_encoder,
                dtype="i4",
            ),

            Field.numbers(
                name = "spacegroup_number",
                value = lambda d, i: 1,
                encoder = volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name = "spacegroup_cell_size[0]",
                value = lambda d, i: data.target_metadata.voxel_size.x,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "spacegroup_cell_size[1]",
                value = lambda d, i: data.target_metadata.voxel_size.y,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "spacegroup_cell_size[2]",
                value = lambda d, i: data.target_metadata.voxel_size.z,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "spacegroup_cell_angles[0]",
                value = lambda d, i: 90,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "spacegroup_cell_angles[1]",
                value = lambda d, i: 90,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "spacegroup_cell_angles[2]",
                value = lambda d, i: 90,
                encoder = volume_server_encoder,
                dtype="f8",
            ),

            Field.numbers(
                name = "mean_source",
                value = lambda d, i: data.channel.statistics.mean,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "mean_sampled",
                value = lambda d, i: data.channel.statistics.mean,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "sigma_source",
                value = lambda d, i: data.channel.statistics.std,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "sigma_sampled",
                value = lambda d, i: data.channel.statistics.std,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "min_source",
                value = lambda d, i: data.channel.statistics.min,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "min_sampled",
                value = lambda d, i: data.channel.statistics.min,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "max_source",
                value = lambda d, i: data.channel.statistics.max,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name = "max_sampled",
                value = lambda d, i: data.channel.statistics.max,
                encoder = volume_server_encoder,
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
            Field.strings(
                name = "query_type",
                value = lambda d, i: "box"
            ),
        ]


class VolumeData3DDesc(CategoryDesc):
    name = "volume_data_3d"

    @staticmethod
    def get_row_count(data: np.ndarray) -> int:
        return data.size

    @staticmethod
    def get_field_descriptors(data: np.ndarray) -> Collection[Field]:
        volume_server_encoder = lambda _: BYTE_ARRAY
        return [
            Field.number_array(
                name="values",
                array=lambda volume: volume,
                encoder = volume_server_encoder,
                dtype="f8",
            ),
        ]


class BCIFSerializer(Serializer):
    @staticmethod
    async def serialize(data, output_path: Path) -> None:
        for time_frame in data.metadata.time_frames:
            for channel in time_frame.channels:
                data_batch = VolumeDataBatch(
                    data.metadata.original_time_frame,
                    time_frame,
                    channel,
                )
                writer = ciftools.serialization.create_binary_writer()

                # We have to create the SERVER category, because it is required, we
                # just have to say that it is a box
                writer.start_data_block("SERVER")
                # Adding a dummy
                writer.write_category(DensityServerResultDesc, [np.arange(0)])

                writer.start_data_block("VOLUME")
                writer.write_category(VolumeData3DInfoDesc, [data_batch])
                print(dataclasses.asdict(data_batch))
                (output_path / "metadata.json").write_text(str(dataclasses.asdict(data_batch)))

                lattice = data.get_data_array(
                    time_frame.lattice_id,
                    time_frame.resolution,
                    time_frame.id,
                    int(channel.id)
                )
                # We have to make the array 1D
                writer.write_category(VolumeData3DDesc, [np.ravel(lattice, "F")])

                file_name = f"{time_frame.lattice_id}_r{time_frame.resolution}_tf{time_frame.id}.bcif"
                (output_path / file_name).write_bytes(writer.encode())

