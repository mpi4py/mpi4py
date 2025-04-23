from typing import Callable, Collection, overload

from ..typing import T, U, V
from ._base import Future

__all__: list[str] = [
    "collect",
    "compose",
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
    resulthook: None = None,
    *,
    excepthook: Callable[[BaseException], BaseException | V],
) -> Future[T | V]: ...
@overload
def compose(
    future: Future[T],
    resulthook: Callable[[T], U],
    excepthook: Callable[[BaseException], BaseException | V],
) -> Future[U | V]: ...
