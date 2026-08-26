from numpy.typing import DTypeLike

import numpy as np
import pydantic

AxesOrderTuple = tuple[int, int, int]
AxesTuple = tuple[DTypeLike, DTypeLike, DTypeLike]


@pydantic.dataclasses.dataclass(frozen=True, slots=True)
class AxisValues:
    """Representation of values on cartesian axes.

    It is used for type-checked readable assignment of some arbitrary value to
    axes. It might represent cell size or lattice dimensions.
    """

    x: float = 0
    y: float = 0
    z: float = 0

    def to_tuple(self, dtype: DTypeLike = float) -> AxesTuple:
        """Transforms current axes values to a typed tuple.

        Some libraries require tuple as their input, instead of doing manual
        transformation users should use this method.

        Parameters
        ----------
        dtype: DTypeLike, optional
            The datatype to which values of axes should be casted.

        Returns
        -------
        AxesTuple:
            The tuple containing values of this axes value instance casted to
            dtype.
        """
        dtype = np.dtype(dtype)
        return (dtype.type(self.x), dtype.type(self.y), dtype.type(self.z))


def create_reorder_permutation(
    current_order: AxesOrderTuple, required_order: AxesOrderTuple = (0, 1, 2)
):
    """Creates reordering permutation for lattice transposition.

    If it is required to reorder some lattice this functions makes it easier
    to create the required tuple.

    Parameters
    ----------
    current_order: AxesOrderTuple
        The current axes order of the lattice.
    required_order: AxesOrderTuple, optional
        Desired axes order of the lattice.

    Returns
    -------
    AxesOrderTuple:
        The permutation of the axes order that should be used for transposition
        of the lattice in the current order to the desired one.
    """
    return tuple(current_order.index(ax) for ax in required_order)
