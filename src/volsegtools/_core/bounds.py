
import pydantic


# TODO: rather use base model...
@pydantic.dataclasses.dataclass
class Bounds:
    # TODO: might be int
    # TODO: this should be generic and accept any class that support some traits
    min: pydantic.NonNegativeFloat | None = 0.0
    max: pydantic.NonNegativeFloat | None = 0.0
