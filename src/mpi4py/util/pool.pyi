import sys
from typing import (
    Any,
    Generic,
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
from ..typing import S, T

__all__: list[str] = [
    "Pool",
    "ThreadPool",
    "AsyncResult",
    "ApplyResult",
    "MapResult",
]

class Pool:
    Executor: type[futures.MPIPoolExecutor]
    executor: futures.Executor
    def __init__(
        self,
        processes: int | None = None,
        initializer: Callable[..., object] | None = None,
        initargs: Iterable[Any] = (),
        **kwargs: Any,
    ) -> None: ...
    def apply(
        self,
        func: Callable[..., T],
        args: Iterable[Any] = (),
        kwds: Mapping[str, Any] = {},
    ) -> T: ...
    def apply_async(
        self,
        func: Callable[..., T],
        args: Iterable[Any] = (),
        kwds: Mapping[str, Any] = {},
        callback: Callable[[T], object] | None = None,
        error_callback: Callable[[BaseException], object] | None = None,
    ) -> AsyncResult[T]: ...
    def map(
        self,
        func: Callable[[S], T],
        iterable: Iterable[S],
        chunksize: int | None = None,
    ) -> list[T]: ...
    def map_async(
        self,
        func: Callable[[S], T],
        iterable: Iterable[S],
        chunksize: int | None = None,
        callback: Callable[[T], None] | None = None,
        error_callback: Callable[[BaseException], None] | None = None,
    ) -> MapResult[T]: ...
    def imap(
        self,
        func: Callable[[S], T],
        iterable: Iterable[S],
        chunksize: int = 1,
    ) -> Iterator[T]: ...
    def imap_unordered(
        self,
        func: Callable[[S], T],
        iterable: Iterable[S],
        chunksize: int = 1,
    ) -> Iterator[T]: ...
    def starmap(
        self,
        func: Callable[..., T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int | None = None,
    ) -> list[T]: ...
    def starmap_async(
        self,
        func: Callable[..., T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int | None = None,
        callback: Callable[[T], None] | None = None,
        error_callback: Callable[[BaseException], None] | None = None,
    ) -> MapResult[T]: ...
    def istarmap(
        self,
        func: Callable[..., T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int = 1,
    ) -> Iterator[T]: ...
    def istarmap_unordered(
        self,
        func: Callable[..., T],
        iterable: Iterable[Iterable[Any]],
        chunksize: int = 1,
    ) -> Iterator[T]: ...
    def close(self) -> None: ...
    def terminate(self) -> None: ...
    def join(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *args: object) -> None: ...

class ThreadPool(Pool):
    Executor: type[futures.ThreadPoolExecutor]

class AsyncResult(Generic[T]):
    future: futures.Future[T]
    def __init__(
        self,
        future: futures.Future[T],
        callback: Callable[[T], None] | None = None,
        error_callback: Callable[[BaseException], None] | None = None,
    ) -> None: ...
    def get(self, timeout: float | None = None) -> T: ...
    def wait(self, timeout: float | None = None) -> None: ...
    def ready(self) -> bool: ...
    def successful(self) -> bool: ...

class ApplyResult(AsyncResult[T]): ...

class MapResult(AsyncResult[list[T]]): ...
