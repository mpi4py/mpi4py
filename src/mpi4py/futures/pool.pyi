import sys
from ..MPI import Intracomm, COMM_WORLD
from ._base import Executor, Future  # noqa: F401
from typing import Any, TypeVar
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

_T = TypeVar("_T")
_P = ParamSpec("_P")

class MPIPoolExecutor(Executor):
    Future: TypeAlias = Future  # noqa: F811
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
    def bootup(
        self,
        wait: bool = True,
    ) -> Self: ...
    if sys.version_info >= (3, 9):
        def submit(
            self,
            __fn: Callable[_P, _T],
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Future[_T]: ...
    elif sys.version_info >= (3, 8):
        def submit(  # type: ignore[override]
            self,
            __fn: Callable[_P, _T],
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Future[_T]: ...
    else:
        def submit(
            self,
            fn: Callable[_P, _T],
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> Future[_T]: ...
    def map(
        self,
        fn: Callable[..., _T],
        *iterables: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1,
        unordered: bool = False,
    ) -> Iterator[_T]: ...
    def starmap(
        self,
        fn: Callable[..., _T],
        iterable: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1,
        unordered: bool = False,
    ) -> Iterator[_T]: ...
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
    def __exit__(self, *args: Any) -> bool | None: ...

class ThreadPoolExecutor(MPIPoolExecutor): ...
class ProcessPoolExecutor(MPIPoolExecutor): ...
