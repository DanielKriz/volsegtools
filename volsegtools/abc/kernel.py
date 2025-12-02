import numpy as np

import abc

class ConvolutionKernel(abc.ABC):
    @abc.abstractmethod
    def as_ndarray(self) -> np.ndarray:
        ...
