import datetime
import itertools
import json
import logging
import math
from pathlib import Path
from typing import Protocol

import dask.array as da
import numpy as np
import scipy
from scipy.ndimage import gaussian_laplace
from skimage.metrics import structural_similarity as ssim

from volsegtools._core.timer import Timer
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.data_set import DataSet
from volsegtools.abc import PostProcessingStep

vst_logger = logging.getLogger("volsegtools")


class ErrorFunction(Protocol):
    def evaluate(
        self,
        new,
        old,
    ) -> float: ...

    def __call__(self, new, old) -> float:
        return self.evaluate(new, old)

    @property
    def name(self) -> str: ...


class HFEN(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        sigma = 1.5
        depth = int(np.ceil(4 * sigma))

        def calculate_log(block, sigma):
            return gaussian_laplace(block, sigma=sigma)

        log_old = old.map_overlap(
            calculate_log,
            depth=depth,
            boundary="reflect",
            dtype="float32",
            sigma=sigma,
        )

        log_new = new.map_overlap(
            calculate_log,
            depth=depth,
            boundary="reflect",
            dtype="float32",
            sigma=sigma,
        )

        diff = log_old - log_new
        numerator = da.sqrt(da.sum(diff**2))
        denominator = da.sqrt(da.sum(log_old**2))
        denominator = da.where(denominator == 0, 1e-10, denominator)

        hfen_score = (numerator / denominator).compute()

        return float(hfen_score)

    @property
    def name(self) -> str:
        return "HFEN"


class VFM(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        print("CALCULING VFM FFS")
        THRESHOLD = 0.0

        original_empty_count = (old < THRESHOLD).sum()
        upscaled_empty_count = (new < THRESHOLD).sum()

        value = (upscaled_empty_count / original_empty_count).compute()
        print(value)
        return value

    @property
    def name(self) -> str:
        return "VFM"


class SSIM(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        def calculate_ssim(block1, block2, data_range):
            if data_range <= 0:
                data_range = 1.0

            _, ssim_map = ssim(
                block1, block2, data_range=float(data_range), full=True, win_size=5
            )
            return ssim_map

        old = old.astype(np.float64)
        new = new.astype(np.float64)

        v_max, v_min = da.compute(old.max(), old.min())
        global_range = float(v_max - v_min)

        results = da.map_overlap(
            calculate_ssim,
            old,
            new,
            depth=2,
            boundary="reflect",
            dtype="float64",
            data_range=global_range,
        )

        mask = old > 0
        masked_results = da.where(mask, results, np.nan)

        return da.nanmean(masked_results).compute()

    @property
    def name(self) -> str:
        return "SSIM"


class MSE(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        mse = da.mean((old - new) ** 2)
        return mse.compute()

    @property
    def name(self) -> str:
        return "MSE"


class MAE(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        old = old.astype(np.float64)
        new = new.astype(np.float64)
        mae = da.mean(da.fabs(old - new))
        return mae.compute()

    @property
    def name(self) -> str:
        return "MAE"


class RMSE(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        mse = da.mean((old - new) ** 2)
        rmse = da.sqrt(mse)
        return rmse.compute()

    @property
    def name(self) -> str:
        return "RMSE"


class PSNR(ErrorFunction):
    def evaluate(
        self,
        new,
        old,
    ) -> float:
        old = old.astype(np.float64)
        new = new.astype(np.float64)
        data_range = old.max() - old.min()
        mse = da.mean((old - new) ** 2)
        return da.where(
            mse == 0, float("inf"), 20 * da.log10(data_range / da.sqrt(mse))
        )

    @property
    def name(self) -> str:
        return "PSNR"


def mse(original, reconstructed):
    mse = da.mean((original - reconstructed) ** 2)
    return mse.compute()


def rmse(original, reconstructed):
    mse = da.mean((original - reconstructed) ** 2)
    rmse = da.sqrt(mse)
    return rmse.compute()


class ErrorEvaluationStep(PostProcessingStep):
    def __init__(
        self,
        error_fn: ErrorFunction | str = MSE(),
        output_path: Path | None = None,
        output_to_stdout: bool = False,
        label: str = "",
    ):
        if isinstance(error_fn, str):
            match error_fn.lower():
                case "mse":
                    self.error_fn = MSE()
                case "mae":
                    self.error_fn = MAE()
                case "rmse":
                    self.error_fn = RMSE()
                case "psnr":
                    self.error_fn = PSNR()
                case "ssim":
                    self.error_fn = SSIM()
                case "vfm":
                    self.error_fn = VFM()
                case "hfen":
                    self.error_fn = HFEN()
        else:
            self.error_fn = error_fn

        self.output_path = output_path
        self.output_to_stdout = output_to_stdout
        self.label = label

    # TODO is from elsewhere
    def calculate_new_chunks(self, channel, factor: float | tuple[float, ...]):
        if isinstance(factor, float):
            return tuple(
                tuple(math.ceil(ax * factor) for ax in axes) for axes in channel.chunks
            )
        elif isinstance(factor, tuple):
            return tuple(
                tuple(math.ceil(ax * factor[idx]) for ax in axes)
                for idx, axes in enumerate(channel.chunks)
            )
        else:
            raise TypeError("Unsupported type for chunk calculation")

    def _upsample_data(self, original: da.Array, data: da.Array):

        zoom = tuple(x / y for x, y in zip(original.shape, data.shape))

        def block_triquintic_zoom(block):
            return scipy.ndimage.zoom(block, zoom=zoom, order=3, mode="reflect")

        return data.map_blocks(
            block_triquintic_zoom,
            dtype=data.dtype,
            chunks=self.calculate_new_chunks(data, zoom),
        )

    async def execute(
        self,
        data_sets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info(
            f"Started 'Error Evaluation - {self.error_fn.name}' post-processing step"
        )
        resolution_to_data = {}
        for _, group in itertools.groupby(data_sets, lambda x: x.metadata.id):
            resolution_to_data = {d.metadata.resolution: d for d in group}

        if len(resolution_to_data) <= 1:
            return data_sets

        errors = []

        for resolution in range(1, len(resolution_to_data)):
            for original_data, data in zip(
                resolution_to_data[0].flat_channel_iter(),
                resolution_to_data[resolution].flat_channel_iter(),
            ):
                data_set_id = data.data_set.metadata.id
                data_set_resolution = data.data_set.metadata.resolution
                task_id = f"{data_set_id}-{data_set_resolution}"
                vst_logger.info(
                    "... evaluating '{}'".format(
                        f"{task_id}-ch{data.metadata.id}",
                    )
                )

                original_lattice = original_data.handle.get_lattice(DaskBackend)
                upsampled_lattice = self._upsample_data(
                    original_lattice,
                    data.handle.get_lattice(DaskBackend),
                )

                if upsampled_lattice.shape != original_lattice.shape:
                    warn_msg = (
                        "Shapes of original {} and upsampled {} arrays "
                        "do not match, skipping to next resolution"
                    )
                    vst_logger.warning(
                        warn_msg.format(
                            original_lattice.shape,
                            upsampled_lattice.shape,
                        )
                    )
                    continue

                error_value = self.error_fn(
                    original_data.handle.get_lattice(DaskBackend),
                    upsampled_lattice,
                )
                errors.append(
                    {
                        "id": data.data_set.metadata.id,
                        "resolution": data.data_set.metadata.resolution,
                        "type": data.data_set.metadata.kind,
                        "data_id": data.metadata.id,
                        "timestamp": f"{datetime.datetime.now()}",
                        "label": self.label,
                        "error_method": self.error_fn.name,
                        "error": float(error_value),
                    }
                )

        if self.output_path is not None:
            if self.output_path.exists():
                with open(self.output_path, "r") as file:
                    old_errors = json.load(file)
                    errors += old_errors
            with open(self.output_path, "w") as file:
                file.write(json.dumps(errors, indent=2))

        if self.output_to_stdout:
            print(json.dumps(errors, indent=2))

        return data_sets


class ErrorEvaluationMultiStep(PostProcessingStep):
    def __init__(
        self,
        error_fn: list[str] = [],
        output_path: Path | None = None,
        output_to_stdout: bool = False,
        label: str = "",
    ):
        self.error_functions = []
        for err in error_fn:
            match err.lower():
                case "mse":
                    self.error_functions.append(MSE())
                case "mae":
                    self.error_functions.append(MAE())
                case "rmse":
                    self.error_functions.append(RMSE())
                case "psnr":
                    self.error_functions.append(PSNR())
                case "ssim":
                    self.error_functions.append(SSIM())
                case "vfm":
                    self.error_functions.append(VFM())
                case "hfen":
                    self.error_functions.append(HFEN())

        self.output_path = output_path
        self.output_to_stdout = output_to_stdout
        self.label = label

    # TODO is from elsewhere
    def calculate_new_chunks(self, channel, factor: float | tuple[float, ...]):
        if isinstance(factor, float):
            return tuple(
                tuple(math.ceil(ax * factor) for ax in axes) for axes in channel.chunks
            )
        elif isinstance(factor, tuple):
            return tuple(
                tuple(math.ceil(ax * factor[idx]) for ax in axes)
                for idx, axes in enumerate(channel.chunks)
            )
        else:
            raise TypeError("Unsupported type for chunk calculation")

    def _upsample_data(self, original: da.Array, data: da.Array):

        zoom = tuple(x / y for x, y in zip(original.shape, data.shape))

        def block_triquintic_zoom(block):
            return scipy.ndimage.zoom(block, zoom=zoom, order=3, mode="reflect")

        return data.map_blocks(
            block_triquintic_zoom,
            dtype=data.dtype,
            chunks=self.calculate_new_chunks(data, zoom),
        )

    async def execute(self, data_sets: list[DataSet]) -> list[DataSet]:
        vst_logger.info("Started 'Error Evaluation Multi' post-processing step")
        resolution_to_data = {}
        for _, group in itertools.groupby(data_sets, lambda x: x.metadata.id):
            resolution_to_data = {d.metadata.resolution: d for d in group}

        if len(resolution_to_data) <= 1:
            return data_sets

        errors = []

        for resolution in range(1, len(resolution_to_data)):
            for original_data, data in zip(
                resolution_to_data[0].flat_channel_iter(),
                resolution_to_data[resolution].flat_channel_iter(),
            ):
                data_set_id = data.data_set.metadata.id
                data_set_resolution = data.data_set.metadata.resolution
                task_id = f"{data_set_id}-{data_set_resolution}"

                original_lattice = original_data.handle.get_lattice(DaskBackend)
                upsampled_lattice = self._upsample_data(
                    original_lattice,
                    data.handle.get_lattice(DaskBackend),
                )

                if upsampled_lattice.shape != original_lattice.shape:
                    warn_msg = (
                        "Shapes of original {} and upsampled {} arrays "
                        "do not match, skipping to next resolution"
                    )
                    vst_logger.warning(
                        warn_msg.format(
                            original_lattice.shape,
                            upsampled_lattice.shape,
                        )
                    )
                    continue

                for error_fn in self.error_functions:
                    vst_logger.info(
                        "... evaluating '{}' with {}".format(
                            f"{task_id}-ch{data.metadata.id}", error_fn.name
                        )
                    )
                    error_value = error_fn(
                        original_lattice,
                        upsampled_lattice,
                    )
                    errors.append(
                        {
                            "id": data.data_set.metadata.id,
                            "resolution": data.data_set.metadata.resolution,
                            "type": data.data_set.metadata.kind,
                            "data_id": data.metadata.id,
                            "timestamp": f"{datetime.datetime.now()}",
                            "label": self.label,
                            "error_method": error_fn.name,
                            "error": float(error_value),
                        }
                    )
                    vst_logger.info(
                        "... evaluating '{}' with {} - DONE".format(
                            f"{task_id}-ch{data.metadata.id}", error_fn.name
                        )
                    )
                    Timer.push_event(
                        "Evaluation of '{}' with {}".format(
                            f"{task_id}-ch{data.metadata.id}", error_fn.name
                        )
                    )

        if self.output_path is not None:
            if self.output_path.exists():
                with open(self.output_path, "r") as file:
                    old_errors = json.load(file)
                    errors += old_errors
            with open(self.output_path, "w") as file:
                file.write(json.dumps(errors, indent=2))

        if self.output_to_stdout:
            print(json.dumps(errors, indent=2))

        return data_sets
