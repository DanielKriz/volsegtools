import dataclasses
from pathlib import Path
from typing import Tuple

import dask.array as da
import numpy as np
import zarr
import zarr.storage

from volsegtools.core import LatticeKind
from volsegtools.model.chunking_mode import ChunkingMode
from volsegtools.model.metadata import Metadata
from volsegtools.model.opaque_data_handle import OpaqueDataHandle
from volsegtools.model.storing_parameters import StoringParameters


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    @property
    def instance(cls):
        return cls._instances[cls]


class WorkingStore(metaclass=Singleton):
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


    def get_data_array(self, lattice_id, resolution, time_frame, channel, kind=LatticeKind.VOLUME):
        kind_group = self.get_data_group(kind)
        lattice_group = kind_group.require_group(lattice_id)
        resolution_group: zarr.Group = lattice_group.require_group(
            f"resolution_{resolution}"
        )
        time_frame_group: zarr.Group = resolution_group.require_group(
            f"time_frame_{time_frame}"
        )
        # FIX: this is unsafe, there should be some check!
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
    ) -> OpaqueDataHandle:
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

        zarr_repr: zarr.Array = time_frame_group.create_array(
            name=str(params.channel),
            chunks=WorkingStore._resolve_chunking_method(
                params.chunking_mode,
                data.shape
            ),
            dtype=params.storage_dtype,
            compressors=[used_compressor] if used_compressor is not None else None,
            shape=data.shape,
            overwrite=True,
        )

        da.to_zarr(arr=data, url=zarr_repr, overwrite=True, compute=True)
        ref = OpaqueDataHandle(zarr_repr)
        ref.metadata.lattice_id = lattice_id
        return ref
