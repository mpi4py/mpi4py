import sys
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from typing import (
    Any,
    ParamSpec,
    TypeAlias,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ..MPI import COMM_WORLD, Intracomm
from ..typing import T
from ._base import Executor, Future

_P = ParamSpec("_P")

class MPIPoolExecutor(Executor):
    Future: TypeAlias = Future
    def __init__(
        self,
        max_workers: int | None = None,
        initializer: Callable[..., object] | None = None,
        initargs: Iterable[Any] = (),
        *,
        python_exe: str = ...,
        python_args: Sequence[str] = ...,
        mpi_info: Mapping[str, str] | Iterable[tuple[str, str]] = ...,
        globals: Mapping[str, str] | Iterable[tuple[str, str]] = ...,  # noqa: A002
        main: bool = True,
        path: Sequence[str] = ...,
        wdir: str = ...,
        env: Mapping[str, str] | Iterable[tuple[str, str]] = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def num_workers(self) -> int: ...
    def bootup(
        self,
        wait: bool = True,
    ) -> Self: ...
    def submit(
        self,
        fn: Callable[_P, T],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Future[T]: ...
    def map(
        self,
        fn: Callable[..., T],
        *iterables: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1,
        buffersize: int | None = None,
        unordered: bool = False,
    ) -> Iterator[T]: ...
    def starmap(
        self,
        fn: Callable[..., T],
        iterable: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1,
        buffersize: int | None = None,
        unordered: bool = False,
    ) -> Iterator[T]: ...
    def shutdown(
        self,
        wait: bool = True,
        *,
        cancel_futures: bool = False,
    ) -> None: ...

class MPICommExecutor:
    def __init__(
        self,
        comm: Intracomm | None = COMM_WORLD,
        root: int = 0,
        **kwargs: Any,
    ) -> None: ...
    def __enter__(self) -> Self | None: ...
    def __exit__(self, *args: object) -> bool | None: ...

class ThreadPoolExecutor(MPIPoolExecutor): ...
class ProcessPoolExecutor(MPIPoolExecutor): ...

def get_comm_workers() -> Intracomm: ...
