import abc
from typing import Any

from numpy.typing import ArrayLike


class DataHandle(abc.ABC):
    @abc.abstractmethod
    def access(self) -> ArrayLike:
        raise NotImplementedError()

    @abc.abstractmethod
    def unwrap(self, target: str) -> ArrayLike:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def metadata(self) -> Any:
        raise NotImplementedError();

    @metadata.setter
    @abc.abstractmethod
    def metadata(self, new_metadata: Any) -> None:
        raise NotImplementedError();
