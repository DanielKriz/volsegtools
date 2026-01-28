import numpy as np
import pytest

from volsegtools.model import LazyDataReference


def test_lazy_ref_from_np_arr():
    arr = np.arange(10)
    ref = LazyDataReference(arr)
