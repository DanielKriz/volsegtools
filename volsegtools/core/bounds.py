import pydantic
from typing import Optional


# TODO: rather use base model...
@pydantic.dataclasses.dataclass
class Bounds:
    # TODO: might be int
    # TODO: this should be generic and accept any class that support some traits
    min: Optional[pydantic.NonNegativeFloat] = 0.0
    max: Optional[pydantic.NonNegativeFloat] = 0.0
