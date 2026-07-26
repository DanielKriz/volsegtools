from pathlib import Path
from typing import Protocol

import json
import logging

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.data_set import DataSet
from volsegtools.abc.post_processing_step import PostProcessingStep

vst_logger = logging.getLogger("volsegtools")


class SizeReporter(Protocol):
    def report(self, channel, size_in_bytes, label): ...


class StdoutSizeReporter(SizeReporter):
    FLOAT_PRECISION_PADDING = 5
    DOT_CHARACTER_PADDING = 1

    def report(self, channel, size_in_bytes, label):
        print("--------------------------------------------------------------")
        print(
            f"Size Evaluation of '{channel.data_set.metadata.id}"
            f"_ch{channel.metadata.id}"
            f"- Resolution {channel.data_set.metadata.resolution}.'"
            f" with {label}"
        )
        print("--------------------------------------------------------------")

        digit_cnt = (
            len(str(size_in_bytes))
            + self.FLOAT_PRECISION_PADDING
            + self.DOT_CHARACTER_PADDING
        )

        print(
            ("Size in bytes:      {:" + str(digit_cnt) + ".5f}B").format(size_in_bytes)
        )
        print(
            ("Size in mega bytes: {:" + str(digit_cnt) + ".5f}MB").format(
                size_in_bytes / 1_000_000
            )
        )
        print(
            ("Size in giga bytes: {:" + str(digit_cnt) + ".5f}GB").format(
                size_in_bytes / 1_000_000_000
            )
        )


class JSONSizeReporter(SizeReporter):
    def __init__(self, output_path: Path):
        self.output_path = output_path

    def report(self, channel, size_in_bytes, label):
        sizes = []
        if self.output_path.exists():
            # TODO: check that valid JSON
            with Path.open(self.output_path) as file:
                old_sizes = json.load(file)
                sizes += old_sizes

        sizes.append(
            {
                "id": channel.data_set.metadata.id,
                "channel_id": channel.metadata.id,
                "resolution": channel.data_set.metadata.resolution,
                "label": label,
                "size_in_bytes": size_in_bytes,
                "size_in_mega_bytes": size_in_bytes / 1_000_000,
                "size_in_giga_bytes": size_in_bytes / 1_000_000_000,
            }
        )

        with Path.open(self.output_path, "w") as file:
            file.write(json.dumps(sizes, indent=2))


class SizeEvaluationStep(PostProcessingStep):
    # It is safe to ignore this kind of error here, because the reported does
    # not contain any state. Thus, the instance can be shared between calls.
    def __init__(
        self,
        reporter: SizeReporter = StdoutSizeReporter(), # noqa: B008
        label: str = ""
    ):
        self.reporter = reporter
        self.label = label

    async def execute(
        self,
        data_sets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info("Started 'Size Evaluation' post-processing step")

        for ds in data_sets:
            for channel in ds.flat_channel_iter():
                lattice = channel.handle.get_lattice(DaskBackend)
                size_in_bytes = lattice.nbytes
                self.reporter.report(channel, size_in_bytes, self.label)

        return data_sets
