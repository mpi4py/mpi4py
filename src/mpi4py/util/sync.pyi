import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from ..MPI import (
    Info,
    INFO_NULL,
    Intracomm,
)

__all__: list[str] = [
    "Sequential",
    "Counter",
    "Mutex",
    "RMutex",
]

class Sequential:
    comm: Intracomm
    tag: int
    def __init__(
        self,
        comm: Intracomm,
        tag: int = 0,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *exc: object) -> None: ...
    def begin(self) -> None: ...
    def end(self) -> None: ...

class Counter:
    def __init__(
        self,
        comm: Intracomm,
        start: int = 0,
        step: int = 1,
        typecode: str = 'i',
        root: int = 0,
        info: Info = INFO_NULL,
    ) -> None: ...
    def __iter__(self) -> Self: ...
    def __next__(self) -> int: ...
    def next(self, incr: int | None = None) -> int: ...
    def free(self) -> None: ...

class Mutex:
    def __init__(
        self,
        comm: Intracomm,
        info: Info = INFO_NULL,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *exc: object) -> None: ...
    def acquire(self, blocking: bool = True) -> bool: ...
    def release(self) -> None: ...
    def locked(self) -> bool: ...
    def free(self) -> None: ...

class RMutex:
    def __init__(
        self,
        comm: Intracomm,
        info: Info = INFO_NULL,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *exc: object) -> None: ...
    def acquire(self, blocking: bool = True) -> bool: ...
    def release(self) -> None: ...
    def locked(self) -> bool: ...
    def count(self) -> int: ...
    def free(self) -> None: ...
