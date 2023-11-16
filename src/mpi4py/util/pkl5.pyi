import sys
from typing import Any
from typing import Iterable, Sequence
from typing import overload
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from .. import MPI
from ..MPI import (
    ROOT as ROOT,
    PROC_NULL as PROC_NULL,
    ANY_SOURCE as ANY_SOURCE,
    ANY_TAG as ANY_TAG,
    Status as Status,
    Pickle as Pickle,
)
from ..typing import Buffer

pickle: Pickle = ...

class _BigMPI:
    blocksize: int = ...
    cache: dict[int, MPI.Datatype] = ...
    def __init__(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *exc: object) -> None: ...
    def __call__(self, buf: Buffer) -> tuple[Buffer, int, MPI.Datatype]: ...

_bigmpi: _BigMPI = ...

class Request(tuple[MPI.Request, ...]):
    @overload
    def __new__(cls, request: MPI.Request | None = None) -> Request: ...
    @overload
    def __new__(cls, request: Iterable[MPI.Request]) -> Request: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __bool__(self) -> bool: ...
    def Free(self) -> None: ...
    def cancel(self) -> None: ...
    def get_status(
        self,
        status: Status | None = None,
    ) -> bool: ...
    def test(
        self,
        status: Status | None = None,
    ) -> tuple[bool, Any | None]: ...
    def wait(
        self,
        status: Status | None = None,
    ) -> Any: ...
    @classmethod
    def get_status_all(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> bool: ...
    @classmethod
    def testall(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> tuple[bool, list[Any] | None]: ...
    @classmethod
    def waitall(
        cls,
        requests: Sequence[Request],
        statuses: list[Status] | None = None,
    ) -> list[Any]: ...

class Message(tuple[MPI.Message, ...]):
    @overload
    def __new__(cls, message: MPI.Message | None = None) -> Message: ...
    @overload
    def __new__(cls, message: Iterable[MPI.Message]) -> Message: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __bool__(self) -> bool: ...
    def recv(self, status: Status | None = None) -> Any: ...
    def irecv(self) -> Request: ...
    @classmethod
    def probe(
        cls,
        comm: MPI.Comm,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Status | None = None,
    ) -> Message: ...
    @classmethod
    def iprobe(
        cls,
        comm: MPI.Comm,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Status | None = None,
    ) -> Message | None: ...

class Comm(MPI.Comm):
    def send(self, obj: Any, dest: int, tag: int = 0) -> None: ...
    def bsend(self, obj: Any, dest: int, tag: int = 0) -> None: ...
    def ssend(self, obj: Any, dest: int, tag: int = 0) -> None: ...
    def isend(self, obj: Any, dest: int, tag: int = 0) -> Request: ...  # type: ignore[override]
    def ibsend(self, obj: Any, dest: int, tag: int = 0) -> Request: ...  # type: ignore[override]
    def issend(self, obj: Any, dest: int, tag: int = 0) -> Request: ...  # type: ignore[override]
    def recv(
        self,
        buf: Buffer | None = None,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Status | None = None,
    ) -> Any: ...
    def irecv(  # type: ignore[override]
        self,
        buf: Buffer | None = None,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
    ) -> Request: ...
    def sendrecv(
        self,
        sendobj: Any,
        dest: int,
        sendtag: int = 0,
        recvbuf: Buffer | None = None,
        source: int = ANY_SOURCE,
        recvtag: int = ANY_TAG,
        status: Status | None = None,
    ) -> Any: ...
    def mprobe(  # type: ignore[override]
        self,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Status | None = None,
    ) -> Message: ...
    def improbe(  # type: ignore[override]
        self,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Status | None = None,
    ) -> Message | None: ...
    def bcast(
        self,
        obj: Any,
        root: int = 0,
    ) -> Any: ...
    def gather(
        self,
        sendobj: Any,
        root: int = 0,
    ) -> list[Any] | None: ...
    def scatter(
        self,
        sendobj: Sequence[Any] | None,
        root: int = 0,
    ) -> Any: ...
    def allgather(
        self,
        sendobj: Any,
    ) -> list[Any]: ...
    def alltoall(
        self,
        sendobj: Sequence[Any],
    ) -> list[Any]: ...

class Intracomm(Comm, MPI.Intracomm): ...
class Intercomm(Comm, MPI.Intercomm): ...
