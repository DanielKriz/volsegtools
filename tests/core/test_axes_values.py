import numpy as np
import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "params, expected",
    [
        ([], (0, 0, 0)),
        ([1], (1, 0, 0)),
        ([1, 2], (1, 2, 0)),
        ([1, 2, 3], (1, 2, 3)),
    ],
)
def test_axes_values_dedicated_constructors(params, expected):
    values = vst.AxisValues(*params)
    assert values.x == expected[0]
    assert values.y == expected[1]
    assert values.z == expected[2]


@pytest.mark.parametrize(
    "builtin_dtype, numpy_dtype",
    [
        (float, np.float64),
        (int, np.int64),
    ],
)
def test_to_tuple_changes_type_to_np_type(builtin_dtype, numpy_dtype):
    values = vst.AxisValues(1, 2, 3.14)
    tupled = values.to_tuple(dtype=builtin_dtype)

    assert type(tupled[0]) == numpy_dtype
    assert type(tupled[1]) == numpy_dtype
    assert type(tupled[2]) == numpy_dtype


@pytest.mark.parametrize(
    "dtype",
    [
        np.int64,
        np.float64,
    ],
)
def test_to_tuple_changes_type(dtype):
    values = vst.AxisValues(1, 2, 3.14)
    tupled = values.to_tuple(dtype=dtype)

    assert type(tupled[0]) == dtype
    assert type(tupled[1]) == dtype
    assert type(tupled[2]) == dtype


@pytest.mark.parametrize(
    "expected, dtype",
    [
        ((1, 2, 3.14), np.float64),
        ((1, 2, 3), np.int64),
    ],
)
def test_to_tuple_changes_values(expected, dtype):
    values = vst.AxisValues(1, 2, 3.14)
    tupled = values.to_tuple(dtype=dtype)

    assert tupled == expected
