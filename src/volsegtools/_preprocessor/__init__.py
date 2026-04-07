"""
Contains classes and functions related to high-level processing.

It serves as an aggregate of all other processing steps.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .preprocessor import Preprocessor
from .preprocessor_builder import PreprocessorBuilder

__all__ = [
    "Preprocessor",
    "PreprocessorBuilder",
]
