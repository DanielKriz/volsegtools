import pytest

from volsegtools import DataKind


@pytest.mark.parametrize(
    "kind, value",
    [
        (DataKind.VOLUME, 1),
        (DataKind.SEGMENTATION_VOLUME, 2),
        (DataKind.SEGMENTATION_MASK, 3),
        (DataKind.SEGMENTATION_MESH, 4),
    ],
)
def test_correct_data_kind_values(kind, value):
    assert kind.value == value
