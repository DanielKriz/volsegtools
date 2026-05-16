import json
from pathlib import Path
from typing import List, Protocol
import logging

from volsegtools._model.data_set import DataSet
from volsegtools._model.dask_backend import DaskBackend
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
            "Size Evaluation of '{}_ch{} - Resolution {}.' with {}".format(
                channel.data_set.metadata.id,
                channel.metadata.id,
                channel.data_set.metadata.resolution,
                label,
            )
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
            with open(self.output_path, "r") as file:
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

        with open(self.output_path, "w") as file:
            file.write(json.dumps(sizes, indent=2))


class SizeEvaluationStep(PostProcessingStep):
    def __init__(self, reporter: SizeReporter = StdoutSizeReporter(), label: str = ""):
        self.reporter = reporter
        self.label = label

    async def execute(self, data_sets: List[DataSet]) -> List[DataSet]:
        vst_logger.info("Started 'Size Evaluation' post-processing step")

        for ds in data_sets:
            for channel in ds.flat_channel_iter():
                lattice = channel.handle.get_lattice(DaskBackend)
                size_in_bytes = lattice.nbytes
                self.reporter.report(channel, size_in_bytes, self.label)

        return data_sets
