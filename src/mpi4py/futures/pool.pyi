import sys
from typing import Any
from typing import Callable, Iterable, Iterator, Mapping, Sequence
if sys.version_info >= (3, 10):
    from typing import ParamSpec
    from typing import TypeAlias
else:
    from typing_extensions import ParamSpec
    from typing_extensions import TypeAlias
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from ..MPI import Intracomm, COMM_WORLD
from ._base import Executor, Future
from ..typing import T

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
        globals: Mapping[str, str] | Iterable[tuple[str, str]] = ...,
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
    if sys.version_info >= (3, 9):
        def submit(
            self,
            __fn: Callable[_P, T],
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Future[T]: ...
    else:
        def submit(
            self,
            fn: Callable[_P, T],
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Future[T]: ...
    def map(
        self,
        fn: Callable[..., T],
        *iterables: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1,
        unordered: bool = False,
    ) -> Iterator[T]: ...
    def starmap(
        self,
        fn: Callable[..., T],
        iterable: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1,
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
