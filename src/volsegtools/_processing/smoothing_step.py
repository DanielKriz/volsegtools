from collections.abc import Callable

import logging

import numpy as np
import scipy

from volsegtools._core.data_kind import DataKind
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.data_set import DataSet
from volsegtools.abc import PostProcessingStep

vst_logger = logging.getLogger("volsegtools")


class SmoothingStep(PostProcessingStep):
    def __init__(
        self,
        appliable_kinds: list[DataKind] | None = None,
        filter_fn: Callable | None = None,
    ):
        if appliable_kinds is None:
            appliable_kinds = []
        self.appliable_kinds = appliable_kinds
        self.filter_fn = filter_fn

    def calculate_convolution_kernel(self):
        x = np.arange(-5, 5 + 1)
        kernel = np.exp(-(x**2) / (2 * 1**2))
        return kernel / kernel.sum()

    async def execute(
        self,
        data_sets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info("Started 'Smoothing' post-processing step")

        kernel = self.calculate_convolution_kernel()

        def smooth_block(block, axis):
            return scipy.ndimage.convolve1d(
                block, weights=kernel, axis=axis, mode="mirror"
            )

        results = []

        for data_set in data_sets:
            data_set_id = data_set.metadata.id
            data_set_resolution = data_set.metadata.resolution
            task_id = f"{data_set_id}-{data_set_resolution}"
            for channel in data_set.flat_channel_iter():
                id = channel.metadata.id
                vst_logger.info(f"... smoothing '{task_id}-ch{id}'")
                data = channel.handle.get_lattice(DaskBackend)
                for axis in [0, 1, 2]:
                    depth = {x: 5 if x == axis else 0 for x in range(3)}
                    smooth_data = data.map_overlap(
                        smooth_block,
                        axis=axis,
                        depth=depth,
                        boundary="reflect",
                        dtype=data.dtype,
                    )
                    channel.set_data(smooth_data, DaskBackend)
            results.append(data_set)
        return results
