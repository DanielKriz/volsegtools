from typing import Annotated

import enum

import pydantic


class UnitKind(enum.IntEnum):
    """ """

    UNKNOWN = 0
    MICRO_METER = 1
    ANGSTROM = 2


Unit = Annotated[
    UnitKind,
    pydantic.PlainSerializer(
        lambda v: v.name.lower(),
        return_type=str,
    ),
]


def unit_from_str(string):
    match string:
        case "um" | "μm" | "micro":
            return UnitKind.MICRO_METER
        case "angstrom" | "Å":
            return UnitKind.ANGSTROM
        case _:
            return UnitKind.UNKNOWN


def to_angstrom(micrometers):
    return micrometers * 10000


def to_micrometer(angstroms):
    return angstroms / 10000


def to_bytes(megabytes: int):
    return megabytes * 10**6
