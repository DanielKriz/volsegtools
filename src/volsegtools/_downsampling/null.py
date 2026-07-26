import logging

from volsegtools.abc import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class Null(DownsamplingStrategy):
    def execute(self, _):
        vst_logger.info("Using the 'Null' downsampling strategy")
        yield from []
