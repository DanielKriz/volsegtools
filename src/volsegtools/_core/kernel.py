from typing import Protocol

import numpy as np


class ConvolutionKernel(Protocol):
    """Protocol for kernel that should be used for convolution."""

    def as_ndarray(self) -> np.ndarray:
        """Transforms internal representation to numpy array.

        Most APIs are based on numpy and this adaptor makes it possible to
        use them.

        Returns
        -------
        np.ndarray:
            Representation of the kernel as numpy array.
        """
        ...

    @property
    def size(self) -> int:
        """Returns the one-dimensional size of the kernel.

        It is expected that each kernel should be 3D and usually these kernels
        have same size in each dimension.

        Additionally the size should be odd.

        Returns
        -------
        int:
            Size of the kernel in one dimension.
        """
        ...
