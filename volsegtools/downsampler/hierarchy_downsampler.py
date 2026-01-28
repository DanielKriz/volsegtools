import asyncio
import collections
import logging
import math
from typing import List, Tuple

import dask
import dask.array as da
import dask_image.ndfilters as dask_filter
import numpy as np

from volsegtools.core import (
    Bounds,
    DownsamplingParameters,
    LatticeKind,
    Vector3,
    to_bytes,
)
from volsegtools.downsampler import BaseDownsampler
from volsegtools.model import (
    ChannelMetadata,
    DescriptiveStatistics,
    FlatChannelIterator,
    OpaqueDataHandle,
    StoringParameters,
    TimeFrameMetadata,
)
from volsegtools.model.working_store import WorkingStore

MIN_GRID_SIZE = 100**1


class HierarchyDownsampler(BaseDownsampler):
    """ """

    # This value was used in the previous version of the preprocessor.
    KERNEL_PARAMETERS: Tuple[int, int, int] = (1, 4, 6)

    def __init__(self):
        _parameters = DownsamplingParameters()
        super().__init__(_parameters)

    """
    def __init__(self, params = DownsamplingParameters()):
        super().__init__(params)
    """

    async def downsample_lattice(
        self, data: OpaqueDataHandle
    ) -> List[OpaqueDataHandle]:
        # We have to get the actual data from the zarr store.
        store = WorkingStore.instance
        channel_iter = FlatChannelIterator(
            store.get_data_group(data.metadata.kind).require_group(
                data.metadata.lattice_id
            )
        )

        ret_value = []

        # Each time frame can have multiple channels, this flat channel
        # iterator iterates over each channel in each resolution for this
        # particular data lattice.
        for channel_info in channel_iter:
            if 1 in channel_info.data.shape:
                # TODO: Add some kind of message, that it does not make
                # sense, fi there is only a single dimension.
                continue

            # This is always true, becase we are reading from the zarr store.
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
                # TODO: this should be changeable with some "additional_downsampler_config" which
                # would be just an arbitrary dictionary.
                factor=8,
            )
            logging.info(f"Downsampling levels {downsampling_levels}")

            for step in range(downsampling_steps):
                # TODO use step to compute the voxel size
                current_ratio = 2 ** (step + 1)
                logging.info(
                    f"Currently downsampling r{current_ratio}, {channel_info.time} and ch{channel_info.channel}"
                )
                downsampled_data = dask_filter.convolve(
                    current_level_data,
                    self.parameters.kernel.as_ndarray(),
                    mode="mirror",
                    cval=0.0,
                )
                # TODO: find out what this does, removes the neighbor?
                downsampled_data = downsampled_data[::2, ::2, ::2]

                if current_ratio not in downsampling_levels:
                    continue

                if self.parameters.acceptance_threshold != None:
                    logging.info("Using the acceptance threshold")
                    downsampled_data[
                        downsampled_data >= self.parameters.acceptance_threshold
                    ]

                if self.parameters.is_mask:
                    # TODO: this is inefficient point of usage, merge this
                    # acceptance threshold check
                    logging.info("Converting to Mask")
                    downsampled_data = da.where(
                        downsampled_data > self.parameters.acceptance_threshold, 1, 0
                    )

                stats = dask.compute(
                    da.mean(downsampled_data),
                    da.std(downsampled_data),
                    downsampled_data.max(),
                    downsampled_data.min(),
                )
                stats = DescriptiveStatistics(*stats)

                data_ref = OpaqueDataHandle(downsampled_data)
                data_ref.metadata = data.metadata

                # Only change things that are really different.
                data_ref.metadata.id = int(channel_info.time.split("_")[-1])
                data_ref.metadata.resolution = current_ratio
                data_ref.metadata.lattice_dimensions = Vector3(
                    downsampled_data.shape[0],
                    downsampled_data.shape[1],
                    downsampled_data.shape[2],
                )
                data_ref.metadata.channels.append(
                    ChannelMetadata(int(channel_info.channel), stats)
                )

                ret_value.append(data_ref)

                params = StoringParameters(
                    resolution_level=current_ratio,
                    time_frame=int(channel_info.time.split("_")[-1]),
                    channel=int(channel_info.channel),
                    storage_dtype=np.byte
                    if self.parameters.is_mask
                    else downsampled_data.dtype,
                    lattice_kind=data.metadata.kind,
                )
                WorkingStore.instance.store_lattice_time_frame(
                    params,
                    downsampled_data,
                    data.metadata.lattice_id,
                )
                current_level_data = downsampled_data
        return ret_value

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
        if self.parameters.downsampling_level_bounds:
            level_bounds: Bounds = self.parameters.downsampling_level_bounds
            if level_bounds.min:
                steps_count = int(math.log2(level_bounds.min))
            if level_bounds.max:
                steps_count = int(math.log2(level_bounds.max))
        else:
            input_grid_size: float = math.prod(data.shape)

            if input_grid_size <= MIN_GRID_SIZE:
                return 1

            file_size_in_bytes = data.dtype.itemsize * input_grid_size
            size_per_downsampling = file_size_in_bytes / to_bytes(
                self.parameters.size_per_level_bounds_in_mb.min
            )
            steps_count = int(math.log(size_per_downsampling, downsampling_factor))

        return steps_count

    def _calculate_downsampling_levels(
        self,
        data: da.Array,
        factor: int,
        downsampling_steps: int,
    ) -> List[int]:
        levels: List[int] = [2**x for x in range(1, downsampling_steps + 1)]

        if self.parameters.downsampling_level_bounds:
            level_bounds: Bounds = self.parameters.downsampling_level_bounds
            if level_bounds.max:
                predicate = lambda x: x <= level_bounds.max
                levels = [x for x in levels if predicate(x)]
            if level_bounds.min:
                predicate = lambda x: x >= level_bounds.min
                levels = [x for x in levels if predicate(x)]

        size_per_level: int = self.parameters.size_per_level_bounds_in_mb.max
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
                "No downsamplings could be saved because the max size per"
                f"channel ({size_per_level}) is too low"
            )
        return levels
