"""
Contains abstract interface to core classes that are used in the processing pipeline.
"""

from volsegtools._core.computation_backend import ComputationBackend
from volsegtools._core.kernel import ConvolutionKernel

from .bundler import Bundler
from .converter import Converter
from .downsampling_strategy import DownsamplingStrategy
from .post_conversion_step import PostConversionStep
from .post_processing_step import PostProcessingStep
from .processing_pipeline import ProcessingPipeline
from .serializer import Serializer

__all__ = [
    "Bundler",
    "ComputationBackend",
    "Converter",
    "ConvolutionKernel",
    "DownsamplingStrategy",
    "PostConversionStep",
    "PostProcessingStep",
    "ProcessingPipeline",
    "Serializer",
]
