import pydantic


@pydantic.dataclasses.dataclass(frozen=True, slots=True)
class AxisValues:
    x: float = 0
    y: float = 0
    z: float = 0
