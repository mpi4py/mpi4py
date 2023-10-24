import sys
from typing import (
    Any,
    Generic,
    TypeVar,
)
from typing import (
    Callable,
    Mapping,
    Iterable,
    Iterator,
)
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from .. import futures

__all__: list[str] = [
    "Pool",
    "ThreadPool",
    "AsyncResult",
    "ApplyResult",
    "MapResult",
]

_S = TypeVar("_S")
_T = TypeVar("_T")

class Pool:
    Executor: type[futures.MPIPoolExecutor]
    executor: futures.Executor
    def __init__(
        self,
        processes: int | None = None,
        initializer: Callable[..., None] | None = None,
        initargs: Iterable[Any] = (),
        **kwargs: Any,
    ) -> None: ...
    def apply(
        self,
        func: Callable[..., _T],
        args: Iterable[Any] = (),
        kwds: Mapping[str, Any] = {},
    ) -> _T: ...
    def apply_async(
        self,
        func: Callable[..., _T],
        args: Iterable[Any] = (),
        kwds: Mapping[str, Any] = {},
        callback: Callable[[_T], object] | None = None,
        error_callback: Callable[[BaseException], object] | None = None,
    ) -> AsyncResult[_T]: ...
    def map(
        self,
        func: Callable[[_S], _T],
        iterable: Iterable[_S],
        chunksize: int | None = None,
    ) -> list[_T]: ...
    def map_async(
        self,
        func: Callable[[_S], _T],
        iterable: Iterable[_S],
        chunksize: int | None = None,
        callback: Callable[[_T], None] | None = None,
        error_callback: Callable[[BaseException], None] | None = None,
    ) -> MapResult[_T]: ...
    def imap(
        self,
        func: Callable[[_S], _T],
        iterable: Iterable[_S],
        chunksize: int = 1,
    ) -> Iterator[_T]: ...
    def imap_unordered(
        self,
        func: Callable[[_S], _T],
        iterable: Iterable[_S],
        chunksize: int = 1,
    ) -> Iterator[_T]: ...
    def starmap(
        self,
        func: Callable[..., _T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int | None = None,
    ) -> list[_T]: ...
    def starmap_async(
        self,
        func: Callable[..., _T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int | None = None,
        callback: Callable[[_T], None] | None = None,
        error_callback: Callable[[BaseException], None] | None = None,
    ) -> MapResult[_T]: ...
    def istarmap(
        self,
        func: Callable[..., _T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int = 1,
    ) -> Iterator[_T]: ...
    def istarmap_unordered(
        self,
        func: Callable[..., _T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int = 1,
    ) -> Iterator[_T]: ...
    def close(self) -> None: ...
    def terminate(self) -> None: ...
    def join(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *args: object) -> None: ...

class ThreadPool(Pool):
    Executor: type[futures.ThreadPoolExecutor]

class AsyncResult(Generic[_T]):
    future: futures.Future[_T]
    def __init__(
        self,
        future: futures.Future[_T],
        callback: Callable[[_T], None] | None = None,
        error_callback: Callable[[BaseException], None] | None = None,
    ) -> None: ...
    def get(self, timeout: float | None = None) -> _T: ...
    def wait(self, timeout: float | None = None) -> None: ...
    def ready(self) -> bool: ...
    def successful(self) -> bool: ...

class ApplyResult(AsyncResult[_T]): ...

class MapResult(AsyncResult[list[_T]]): ...
