import dataclasses

from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


# TODO: rather use pydantic
@dataclasses.dataclass
class Vector3:
    x: float = 0
    y: float = 0
    z: float = 0

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.is_instance_schema(cls)
