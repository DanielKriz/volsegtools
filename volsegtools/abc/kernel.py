import abc

import numpy as np


class ConvolutionKernel(abc.ABC):
    @abc.abstractmethod
    def as_ndarray(self) -> np.ndarray:
        ...
