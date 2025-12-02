import dataclasses

# TODO: rather use pydantic
@dataclasses.dataclass
class Vector3:
    x: float = 0
    y: float = 0
    z: float = 0
