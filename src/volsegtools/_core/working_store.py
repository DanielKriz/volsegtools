from pathlib import Path
from typing import Tuple

import numpy as np
import zarr
import zarr.storage

from volsegtools._core.data_kind import DataKind
from volsegtools._core.chunking_mode import ChunkingMode

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


# TODO: Remove the Singleton
# TODO: Make it possible to share existing store
# TODO: Rename to 'Workspace'
# TODO: There is huge chance, that we do not need this...
class WorkingStore:
    def __init__(self, store_path: Path):
        self.data_store = zarr.storage.LocalStore(root=store_path)
        self.root_group = zarr.open_group(store=self.data_store, mode="a")

        self.volume_dtype = np.float64
        self.is_volume_dtype_set = False

        self.segmentation_dtype = np.float64
        self.is_segmentation_dtype_set = False

        self._volume_data_group = self.root_group.require_group("volume_data")
        self._segmentation_data_group = self.root_group.require_group(
            "segmentation_data"
        )

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def volume_data_group(self):
        return self._volume_data_group

    @property
    def segmentation_data_group(self):
        return self._segmentation_data_group

    def get_data_array(
        self, lattice_id, resolution, time_frame, channel, kind=DataKind.VOLUME
    ):
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
        data_shape: Tuple[int, ...],
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
                return WorkingStore._compute_chunk_size_based_on_data(data_shape)
            case _:
                raise RuntimeError("Unsupported chunking method!")

    def get_data_group(self, lattice_kind: DataKind):
        match lattice_kind:
            case DataKind.VOLUME:
                return self.volume_data_group
            case DataKind.SEGMENTATION_VOLUME:
                return self.segmentation_data_group
            case _:
                raise RuntimeError("Unknown lattice kind encountered.")
