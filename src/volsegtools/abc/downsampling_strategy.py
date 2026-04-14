import abc


class DownsamplingStrategy(abc.ABC):
    def execute(self, channel): ...
