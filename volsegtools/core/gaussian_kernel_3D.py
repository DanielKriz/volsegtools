import numpy as np

from volsegtools.abc import ConvolutionKernel

class Gaussian3DKernel(ConvolutionKernel):
    """Generate a 3D Gaussian kernel."""

    def __init__(self, size: int, sigma: float):
        ax = np.linspace(-(size // 2), size // 2, size)
        xx, yy, zz = np.meshgrid(ax, ax, ax, indexing='ij')
        kernel = np.exp(-(xx**2 + yy**2 + zz**2) / (2. * sigma**2))
        self._kernel_lattice =  kernel / np.sum(kernel)
    
    def as_ndarray(self) -> np.ndarray:
        return self._kernel_lattice

