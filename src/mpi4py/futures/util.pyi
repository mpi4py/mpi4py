from typing import TypeVar
from typing import Collection
from typing import Callable
from typing import overload
from ._base import Future

__all__: list[str] = [
    'collect',
    'compose',
]

_T = TypeVar("_T")
_U = TypeVar("_U")
_V = TypeVar("_V")

def collect(
    fs: Collection[Future[_T]],
) -> Future[list[_T]]: ...

@overload
def compose(
    future: Future[_T],
    resulthook: None = None,
    excepthook: None = None,
) -> Future[_T]: ...

@overload
def compose(
    future: Future[_T],
    resulthook: Callable[[_T], _U] = ...,
    excepthook: None = None,
) -> Future[_U]: ...

@overload
def compose(
    future: Future[_T],
    resulthook: None = None,
    excepthook: Callable[[BaseException], BaseException | _V] = ...,
) -> Future[_T | _V]: ...

@overload
def compose(
    future: Future[_T],
    resulthook: Callable[[_T], _U] = ...,
    excepthook: Callable[[BaseException], BaseException | _V] = ...,
) -> Future[_U | _V]: ...
