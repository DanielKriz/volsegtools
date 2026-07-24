import volsegtools as vst

class Null(vst.abc.DownsamplingStrategy):
    def execute(self, _):
        vst.logger.info("Using the 'Null' downsampling strategy")
        yield from []
