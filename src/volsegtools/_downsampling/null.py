from collections.abc import Iterator

import logging

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools.abc import DownsamplingStrategy, TData

vst_logger = logging.getLogger("volsegtools")


class Null(DownsamplingStrategy[TData]):
    def execute(
        self,
        data: TData,
        context: PipelineContext
    ) -> Iterator[TData]:
        vst_logger.info("Using the 'Null' downsampling strategy")
        yield from []
