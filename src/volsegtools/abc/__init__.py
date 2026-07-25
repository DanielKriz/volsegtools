"""
Contains abstract interface to core classes that are used in the processing pipeline.
"""

from .bundler import Bundler
from .converter import Converter
from .downsampling_strategy import DownsamplingStrategy
from .serializer import Serializer
from .processing_pipeline import ProcessingPipeline
from .post_conversion_step import PostConversionStep
from .post_processing_step import PostProcessingStep

from volsegtools._core.kernel import ConvolutionKernel
from volsegtools._core.computation_backend import ComputationBackend

__all__ = [
    "Bundler",
    "Converter",
    "DownsamplingStrategy",
    "Serializer",
    "ProcessingPipeline",
    "PostProcessingStep",
    "PostConversionStep",
    "ConvolutionKernel",
    "ComputationBackend",
]
