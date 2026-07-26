from typing import Protocol

import numpy as np


class ConvolutionKernel(Protocol):
    def as_ndarray(self) -> np.ndarray: ...

    @property
    def size(self) -> int: ...
