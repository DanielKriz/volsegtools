"""
Contains classes and functions related to high-level processing.

It serves as an aggregate of all other processing steps.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .processing_pipeline import ProcessingPipeline
from .processing_pipeline_builder import ProcessingPipelineBuilder, create_builder
from .smoothing_step import SmoothingStep
from .error_evaluation_step import ErrorEvaluationStep, ErrorEvaluationMultiStep
from .size_evaluation_step import (
    SizeEvaluationStep,
    JSONSizeReporter,
    StdoutSizeReporter,
)

from .dask_backend import DaskBackend
from .numpy_backend import NumPyBackend
from .mesh_backend import MeshBackend

__all__ = [
    "ProcessingPipeline",
    "ProcessingPipelineBuilder",
    "create_builder",
    "SmoothingStep",
    "ErrorEvaluationStep",
    "ErrorEvaluationMultiStep",
    "SizeEvaluationStep",
    "JSONSizeReporter",
    "StdoutSizeReporter",

    "DaskBackend",
    "NumPyBackend",
    "MeshBackend",
]
