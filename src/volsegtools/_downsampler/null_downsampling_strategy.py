import volsegtools as vst

class NullDownsamplingStrategy(vst.abc.DownsamplingStrategy):
    def execute(self, _):
        vst.logger.info("Using the 'Null' downsampling strategy")
        yield from []
