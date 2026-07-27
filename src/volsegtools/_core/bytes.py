from typing import Self

import re

class Bytes(int):
    VALUE_PATTERN = re.compile(
        r"^\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>[kmgt]?i?b)?\s*$",
        re.IGNORECASE,
    )

    MULTIPLIERS_MAP = {
        None: 1,
        "b": 1,
        "kb": 1_000,
        "mb": 1_000_000,
        "gb": 1_000_000_000,
        "tb": 1_000_000_000_000,
        "kib": 1_024,
        "mib": 1_024**2,
        "gib": 1_024**3,
        "tib": 1_024**4,
    }

    def __new__(cls, value: int | str) -> Self:
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Bytes count cannnot be negative")
            return int.__new__(cls, value)

        match = cls.VALUE_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError(f"Invalid byte size: {value}")

        number = float(match.group("value"))
        unit = match.group("unit")
        normalized_unit = unit.lower() if unit else None

        byte_count = number * cls.MULTIPLIERS_MAP[normalized_unit]

        return int.__new__(cls, int(byte_count))

    @classmethod
    def parse(cls, value: int | str) -> Self:
        return cls(value)
