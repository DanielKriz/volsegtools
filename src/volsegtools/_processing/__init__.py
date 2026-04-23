"""
Contains classes and functions related to high-level processing.

It serves as an aggregate of all other processing steps.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .processing_pipeline import ProcessingPipeline
from .processing_pipeline_builder import ProcessingPipelineBuilder, create_builder

__all__ = [
    "ProcessingPipeline",
    "ProcessingPipelineBuilder",
    "create_builder",
]
