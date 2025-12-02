import zarr
import zarr.storage

import numpy as np
import dask.array as da
import dataclasses
from pathlib import Path

from typing import Tuple
from volsegtools.model.storing_parameters import StoringParameters
from volsegtools.model.lattice_kind import LatticeKind
from volsegtools.model.chunking_mode import ChunkingMode
from volsegtools.model.metadata import Metadata

class TimeFrameIterator():
    ...

class ResolutionIterator():
    ...

class ChannelIterator():
    ...

@dataclasses.dataclass
class ChannelInfo():
    resolution: str
    time: str
    channel: str
    data: zarr.Array

class FlatChannelIterator():
    def __init__(self, group):
        self.group = group
        self._iter = self._group_iter()


    def _group_iter(self):
        for resolution, resolution_group in self.group.groups():
            for time, time_group in resolution_group.groups():
                for channel, channel_arr in time_group.arrays():
                    yield ChannelInfo(
                        resolution,
                        time,
                        channel,
                        channel_arr
                    )


    def __iter__(self):
        return self


    def __next__(self) -> ChannelInfo:
        return next(self._iter)


class Data():
    def __init__(self, store_path: Path):
        self.data_store = zarr.storage.LocalStore(root=store_path)
        self.root_group = zarr.create_group(store=self.data_store)

        self._metadata = Metadata()

        self.volume_dtype = np.float64
        self.is_volume_dtype_set = False

        self.segmentation_dtype = np.float64
        self.is_segmentation_dtype_set = False

        self._volume_data_group = self.root_group.require_group('volume_data')
        self._segmentation_data_group = self.root_group.require_group(
            'segmentation_data'
        )

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value
        # TODO: it should return a dictionary
        # self.root_group.attrs.put(dataclasses.asdict(self._metadata))


    @property
    def volume_data_group(self):
        return self._volume_data_group


    @property
    def segmentation_data_group(self):
        return self._segmentation_data_group


    def get_data_array(self, lattice_id, resolution, time_frame, channel):
        kind_group = self.get_data_group(LatticeKind.VOLUME)
        lattice_group = kind_group.require_group(lattice_id)
        resolution_group: zarr.Group = lattice_group.require_group(
            f"resolution_{resolution}"
        )
        time_frame_group: zarr.Group = resolution_group.require_group(
            f"time_frame_{time_frame}"
        )
        return list(time_frame_group.arrays())[channel][1][:]


    @staticmethod
    def _compute_chunk_size_based_on_data(
        data_shape: Tuple[int, ...]
    ) -> Tuple[int, ...]:
        chunks = tuple([int(i / 4) if i > 4 else i for i in data_shape])
        return chunks


    @staticmethod
    def _resolve_chunking_method(mode: ChunkingMode, data_shape: Tuple[int, ...]):
        match mode:
            case ChunkingMode.AUTO:
                print("CHUNKING WITH ATOU")
                return "auto"
            case ChunkingMode.NONE:
                return (0, 0)
            case ChunkingMode.CUSTOM:
                return Data._compute_chunk_size_based_on_data(data_shape)
            case _:
                raise RuntimeError("Unsupported chunking method!")


    def get_data_group(self, lattice_kind: LatticeKind):
        match lattice_kind:
            case LatticeKind.VOLUME:
                return self.volume_data_group
            case LatticeKind.SEGMENTATION:
                return self.segmentation_data_group
            case _:
                raise RuntimeError("Unknown lattice kind encountered.")


    def store_lattice_time_frame(
        self,
        params: StoringParameters,
        data: da.Array,
        lattice_id: str,
    ) -> None:
        kind_group = self.get_data_group(params.lattice_kind)
        lattice_group = kind_group.require_group(lattice_id)
        resolution_group: zarr.Group = lattice_group.require_group(
            f"resolution_{params.resolution_level}"
        )
        time_frame_group: zarr.Group = resolution_group.require_group(
            f"time_frame_{params.time_frame}"
        )

        used_compressor = None
        if params.is_compression_enabled:
            used_compressor = params.compressor

        print(params)

        zarr_repr: zarr.Array = time_frame_group.create_array(
            name=str(params.channel),
            chunks=Data._resolve_chunking_method(
                params.chunking_mode,
                data.shape
            ),
            dtype=params.storage_dtype,
            compressors=[used_compressor] if used_compressor is not None else None,
            shape=data.shape,
            overwrite=True,
        )

        print(data)
        print(zarr_repr)

        da.to_zarr(arr=data, url=zarr_repr, overwrite=True, compute=True)
