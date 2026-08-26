import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "str_value, bytes_count",
    [
        ("1", 1),
        ("1b", 1),
        ("1kb", 1_000),
        ("1mb", 1_000_000),
        ("1gb", 1_000_000_000),
        ("1tb", 1_000_000_000_000),
        ("1kib", 1_024),
        ("1mib", 1_024**2),
        ("1gib", 1_024**3),
        ("1tib", 1_024**4),
    ],
)
def test_bytes_from_suffix(str_value, bytes_count):
    assert vst.Bytes(str_value) == bytes_count


@pytest.mark.parametrize(
    "str_value, bytes_count",
    [
        ("1", 1),
        ("1b", 1),
        ("1kb", 1_000),
        ("1mb", 1_000_000),
        ("1gb", 1_000_000_000),
        ("1tb", 1_000_000_000_000),
        ("1kib", 1_024),
        ("1mib", 1_024**2),
        ("1gib", 1_024**3),
        ("1tib", 1_024**4),
    ],
)
def test_bytes_count_construction(str_value, bytes_count):
    assert vst.Bytes(bytes_count) == vst.Bytes(str_value)


@pytest.mark.parametrize(
    "str_value, bytes_count",
    [
        ("1", 1),
        ("1b", 1),
        ("1kb", 1_000),
        ("1mb", 1_000_000),
        ("1gb", 1_000_000_000),
        ("1tb", 1_000_000_000_000),
        ("1kib", 1_024),
        ("1mib", 1_024**2),
        ("1gib", 1_024**3),
        ("1tib", 1_024**4),
    ],
)
def test_bytes_count_parse_from_suffix(str_value, bytes_count):
    assert vst.Bytes.parse(str_value) == bytes_count


@pytest.mark.parametrize(
    "bytes_count",
    [
        1,
        1,
        1_000,
        1_000_000,
        1_000_000_000,
        1_000_000_000_000,
        1_024,
        1_024**2,
        1_024**3,
        1_024**4,
    ],
)
def test_bytes_count_parse_from_count(bytes_count):
    assert vst.Bytes.parse(bytes_count) == bytes_count
