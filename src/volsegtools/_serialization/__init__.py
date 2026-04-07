"""
Contains classes and functions related to the serialization of downsampled data.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .bcif_serializer import BCIFSerializer

__all__ = [
    "BCIFSerializer",
]
