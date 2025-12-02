import numpy as np
import collections
import math
import logging
from typing import Tuple, List
import dask.array as da
import dask
import dask_image.ndfilters as dask_filter
import asyncio


from volsegtools.model import (
    Data,
    FlatChannelIterator,
    LatticeKind,
    ChannelMetadata,
    TimeFrameMetadata,
    DescriptiveStatistics,
    StoringParameters,
)
from volsegtools.downsampler import BaseDownsampler
from volsegtools.core import (
    DownsamplingParameters,
    to_bytes,
    Vector3,
    Bounds,
)

MIN_GRID_SIZE = 100 ** 1


class HierarchyDownsampler(BaseDownsampler):
    """
    """

    # This value was used in the previous version of the preprocessor.
    KERNEL_PARAMETERS: Tuple[int, int, int] = (1, 4, 6)


    def __init__(self):
        params = DownsamplingParameters()
        super().__init__(params)
        self.downsampling_params = params

    """
    def __init__(self, params = DownsamplingParameters()):
        super().__init__(params)
    """

    def downsample(self, data: Data) -> Data:
        self._data = data

        for _, volume_group in data.volume_data_group.groups():
            resolution_group = volume_group.require_group('resolution_0')
            time_group = resolution_group.require_group('time_frame_0')
            data_arr = list(time_group.arrays())[0][1]
            asyncio.run(self.downsample_lattice(
                volume_group.basename,
                da.from_zarr(data_arr),
                LatticeKind.VOLUME
            ))

        # Enable mask for segmentation
        self.downsampling_params.is_mask = True
        self.downsampling_params.acceptance_threshold = 0.1

        for _, segmentation_group in data.segmentation_data_group.groups():
            resolution_group = segmentation_group.require_group('resolution_0')
            time_group = resolution_group.require_group('time_frame_0')
            data_arr = list(time_group.arrays())[0][1]
            asyncio.run(self.downsample_lattice(
                segmentation_group.basename,
                da.from_zarr(data_arr),
                LatticeKind.SEGMENTATION
            ))

        return data

    def generate_kernel_3d_arr(self, pattern: list[int]) -> np.ndarray:
        """
        Generates conv kernel based on pattern provided (e.g. [1,4,6,4,1]).
        https://stackoverflow.com/questions/71739757/generate-3d-numpy-array-based-on-provided-pattern/71742892#71742892
        """
        try:
            assert len(pattern) == 5, "pattern should have length 5"
            pattern = pattern[0:3]
            x = np.array(pattern[-1]).reshape([1, 1, 1])
            for p in reversed(pattern[:-1]):
                x = np.pad(x, mode="constant", constant_values=p, pad_width=1)

            k = (1 / x.sum()) * x
            assert k.shape == (5, 5, 5)
        except AssertionError as e:
            logging.error(e, stack_info=True, exc_info=True)
            raise e
        return k

    async def downsample_lattice(self, name, lattice: da.Array, kind: LatticeKind) -> da.Array:
        if self.data == None:
            raise RuntimeError("there is no data class")

        cached_metadata = collections.defaultdict(lambda: collections.defaultdict(TimeFrameMetadata))
        original_voxel_size = self.data.metadata.original_time_frame.voxel_size

        channel_iter = FlatChannelIterator(
            self.data.get_data_group(kind).require_group(name)
        )

        for channel_info in channel_iter:
            if 1 in channel_info.data.shape:
                # TODO: Add some kind of message, that it does not make
                # sense, there is only a single dimension.
                continue

            dask_arr = da.from_zarr(
                url=channel_info.data,
                chunks=channel_info.data.chunks,
            )

            current_level_data = dask_arr

            downsampling_steps = self._calculate_downsampling_steps_count(
                dask_arr,
            )
            logging.info(f"Downsampling steps {downsampling_steps}")

            downsampling_levels = self._calculate_downsampling_levels(
                dask_arr,
                downsampling_steps=downsampling_steps,
                factor=8,
            )
            logging.info(f"Downsampling levels {downsampling_levels}")

            for step in range(downsampling_steps):
                # TODO use step to compute the voxel size
                current_ratio = 2 ** (step + 1)
                logging.info(f"Currently downsampling r{current_ratio}, {channel_info.time} and ch{channel_info.channel}")
                downsampled_data = dask_filter.convolve(
                    current_level_data,
                    # self.downsampling_params.kernel.as_ndarray(),
                    self.generate_kernel_3d_arr([1, 4, 5, 4, 1]),
                    mode='mirror',
                    cval=0.0,
                )
                # remove the neighbor?
                downsampled_data = downsampled_data[::2, ::2, ::2]

                if self.downsampling_params.acceptance_threshold != None:
                    logging.info("Using the acceptance threshold")
                    downsampled_data[
                        downsampled_data >= self.downsampling_params.acceptance_threshold
                    ]

                if current_ratio not in downsampling_levels:
                    continue

                if self.downsampling_params.is_mask:
                    # TODO: this is inefficient point of usage, merge this
                    # acceptance threshold check
                    logging.info("Converting to Mask")
                    downsampled_data = da.where(
                        downsampled_data > self.downsampling_params.acceptance_threshold,
                        1,
                        0
                    )

                stats = dask.compute(
                    da.mean(downsampled_data),
                    da.std(downsampled_data),
                    downsampled_data.max(),
                    downsampled_data.min(),
                )

                stats = DescriptiveStatistics(*stats)

                current_time_metadata = cached_metadata[current_ratio][channel_info.time]
                current_time_metadata.lattice_id = name
                current_time_metadata.id = int(channel_info.time.split('_')[-1])
                current_time_metadata.resolution = current_ratio
                current_time_metadata.lattice_dimensions = Vector3(
                    downsampled_data.shape[0],
                    downsampled_data.shape[1],
                    downsampled_data.shape[2],
                )
                current_time_metadata.voxel_size = Vector3(
                    original_voxel_size.x,
                    original_voxel_size.y,
                    original_voxel_size.z,
                )
                current_time_metadata.channels.append(
                    ChannelMetadata(int(channel_info.channel), stats)
                )

                params = StoringParameters(
                    resolution_level=current_ratio,
                    time_frame=int(channel_info.time.split('_')[-1]),
                    channel=int(channel_info.channel),
                    storage_dtype=np.byte if self.downsampling_params.is_mask else downsampled_data.dtype,
                    lattice_kind=kind,
                )
                self.data.store_lattice_time_frame(
                    params,
                    downsampled_data,
                    name,
                )
                current_level_data = downsampled_data

        # Writing metadata to the dataset
        frames = []
        for time_frames in cached_metadata.values():
            for frame in time_frames.values():
                frames.append(frame)

        # TODO: wrap this into a method
        # Does not work everytime!
        metadata = self.data.metadata
        metadata.time_frames = frames
        self.data.metadata = metadata

        return lattice


    def _calculate_downsampling_steps_count(
        self,
        data: da.Array,
        downsampling_factor: int = 8,
    ) -> int:
        """Calculates the number of steps that are going to be taken during
        the downsampling of the input data.

        Parameters
        ----------
        data: da.Array
            The input data that shall be downsampled.
        downsampling_factor: int
            The factor of downsampling.

        Returns
        -------
        int:
            the number of downsampling steps.
        """

        steps_count: int = 0

        # Steps are calculated either from bounds provided as downsampling 
        # parameters, if any. In that case the maximal bound has priority over
        # the minimal bound as it is the user's decision.
        # Otherwise we have to compute them manually.
        if self.params.downsampling_level_bounds:
            level_bounds: Bounds = self.params.downsampling_level_bounds
            if level_bounds.min:
                steps_count = int(math.log2(level_bounds.min))
            if level_bounds.max:
                steps_count = int(math.log2(level_bounds.max))
        else:
            input_grid_size: float = math.prod(data.shape)

            if input_grid_size <= MIN_GRID_SIZE:
                print("TOO SMALL GRID")
                return 1

            file_size_in_bytes = data.dtype.itemsize * input_grid_size
            size_per_downsampling = (
                file_size_in_bytes /
                to_bytes(self.params.size_per_level_bounds_in_mb.min)
            )
            steps_count = int(math.log(
                size_per_downsampling,
                downsampling_factor
            ))

        return steps_count


    def _calculate_downsampling_levels(
        self,
        data: da.Array,
        factor: int,
        downsampling_steps: int,
    ) -> List[int]:
        levels: List[int] = [2**x for x in range(1, downsampling_steps + 1)]

        if self.params.downsampling_level_bounds:
            level_bounds: Bounds = self.params.downsampling_level_bounds
            if level_bounds.max:
                predicate = lambda x: x <= level_bounds.max
                levels = [x for x in levels if predicate(x)]
            if level_bounds.min:
                predicate = lambda x: x >= level_bounds.min
                levels = [x for x in levels if predicate(x)]

        size_per_level: int = self.params.size_per_level_bounds_in_mb.max
        if size_per_level:
            # TODO: make this a parameters
            input_grid_size: float = math.prod(data.shape)
            file_size_in_bytes = data.dtype.itemsize * input_grid_size
            # TODO: this needs a better name
            n = math.ceil(
                math.log(
                    file_size_in_bytes
                    / (
                        # TODO: Make this a function or something
                        size_per_level * 1024**2
                    ),
                    factor,
                )
            )
            levels = [x for x in levels if x >= 2**n]

        if len(levels) == 0:
            raise RuntimeError(
                'No downsamplings could be saved because the max size per'
                f'channel ({size_per_level}) is too low'
            )
        return levels
