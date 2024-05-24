from typing import Collection
from typing import Callable
from typing import overload
from ._base import Future
from ..typing import T, U, V

__all__: list[str] = [
    'collect',
    'compose',
]

def collect(
    fs: Collection[Future[T]],
) -> Future[list[T]]: ...

@overload
def compose(
    future: Future[T],
    resulthook: None = None,
    excepthook: None = None,
) -> Future[T]: ...

@overload
def compose(
    future: Future[T],
    resulthook: Callable[[T], U],
    excepthook: None = None,
) -> Future[U]: ...

@overload
def compose(
    future: Future[T],
    resulthook: None = None, *,
    excepthook: Callable[[BaseException], BaseException | V],
) -> Future[T | V]: ...

@overload
def compose(
    future: Future[T],
    resulthook: Callable[[T], U],
    excepthook: Callable[[BaseException], BaseException | V],
) -> Future[U | V]: ...
