from typing import Annotated

import pydantic


@pydantic.dataclasses.dataclass(frozen=True, slots=True)
class AxisValues:
    x: float = 0
    y: float = 0
    z: float = 0

    def to_tuple(self, dtype=float):
        return (dtype(self.x), dtype(self.y), dtype(self.z))


def _axis_values_as_int(values: AxisValues) -> dict[str, int]:
    return {
        "x": int(values.x),
        "y": int(values.y),
        "z": int(values.z),
    }


AxisValuesAsInt = Annotated[
    AxisValues,
    pydantic.PlainSerializer(_axis_values_as_int, return_type=dict[str, int]),
]


def create_reorder_permutation(current_order, required_order=(0, 1, 2)):
    return tuple(current_order.index(ax) for ax in required_order)
