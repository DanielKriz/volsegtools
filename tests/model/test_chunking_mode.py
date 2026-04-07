import pytest

from volsegtools import ChunkingMode


@pytest.mark.parametrize(
    "kind, value",
    [
        (ChunkingMode.AUTO, 1),
        (ChunkingMode.NONE, 2),
        (ChunkingMode.CUSTOM, 3),
    ],
)
def test_assert_correct_chunking_mode_values(kind, value):
    assert kind.value == value
