import pytest

from volsegtools import LatticeKind


@pytest.mark.parametrize(
    "kind, value",
    [
        (LatticeKind.VOLUME, 1),
        (LatticeKind.SEGMENTATION, 2),
    ],
)
def test_assert_correct_lattice_kind_values(kind, value):
    assert kind.value == value
