import sys
from ..MPI import Intracomm, COMM_WORLD
from ._core import Executor, Future
from typing import Any, Optional, Tuple, Type, TypeVar, Union
from typing import Callable, Iterable, Iterator, Mapping, Sequence
if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

_T = TypeVar("_T")
_P = ParamSpec("_P")

class MPIPoolExecutor(Executor):
    Future: Any = ...  # _type: Union[Type[Future], Callable[[], Future]]
    def __init__(
        self,
        max_workers: Optional[int] = None,
        initializer: Optional[Callable[..., None]] = None,
        initargs: Tuple = (),
        *,
        python_exe: str = ...,
        python_args: Sequence[str] = ...,
        mpi_info: Union[Mapping[str, str], Iterable[Tuple[str, str]]] = ...,
        globals: Union[Mapping[str, str], Iterable[Tuple[str, str]]] = ...,
        main: bool = True,
        path: Sequence[str] = ...,
        wdir: str = ...,
        env: Union[Mapping[str, str], Iterable[Tuple[str, str]]] = ...,
        **kwargs: Any,
    ) -> None: ...
    def bootup(
        self: _T,
        wait: bool = True,
    ) -> _T: ...
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
        timeout: Optional[float] = None,
        chunksize: int = 1,
        unordered: bool = False,
    ) -> Iterator[_T]: ...
    def starmap(
        self,
        fn: Callable[..., _T],
        iterable: Iterable[Any],
        timeout: Optional[float] = None,
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
        comm: Optional[Intracomm] = COMM_WORLD,
        root: int = 0,
        **kwargs: Any,
    ) -> None: ...
    def __enter__(self) -> Optional[MPIPoolExecutor]: ...
    def __exit__(self, *args: Any) -> Optional[bool]: ...

class ThreadPoolExecutor(MPIPoolExecutor): ...
class ProcessPoolExecutor(MPIPoolExecutor): ...
