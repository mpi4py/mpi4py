from .. import MPI
from ..MPI import ANY_SOURCE, ANY_TAG
from ..MPI import Status, Datatype
from typing import Any, Literal, Optional
from typing import Callable, Iterable, Sequence
from typing import Dict, List, Tuple
from typing import overload

Buffer = Any

class Pickle:
    PROTOCOL: int = ...
    THRESHOLD: int = ...
    def __init__(self,
        dumps: Callable[[Any, int], bytes] = ...,
        loads: Callable[[Buffer], Any] = ...,
        protocol: Optional[int] = ...,
    ) -> None: ...
    def dumps(self, obj: Any) -> Tuple[bytes, List[Buffer]]: ...
    def loads(self, data: Buffer, bufs: Iterable[Buffer]): ...

pickle: Pickle = ...

class _BigMPI:
    blocksize: int = ...
    cache: Dict[int, Datatype] = ...
    def __init__(self) -> None: ...
    def __enter__(self) -> _BigMPI: ...
    def __exit__(self, *exc: Any) -> None: ...
    def __call__(self, buf: Buffer) -> Tuple[Buffer, int, Datatype]: ...

_bigmpi: _BigMPI = ...

class Request(Tuple[MPI.Request, ...]):
    @overload
    def __new__(cls, request: Optional[MPI.Request] = None) -> Request: ...
    @overload
    def __new__(cls, request: Iterable[MPI.Request]) -> Request: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __bool__(self) -> bool: ...
    def Free(self) -> None: ...
    def cancel(self) -> None: ...
    def get_status(self, status: Optional[Status] = None) -> bool: ...
    def test(self, status: Optional[Status] = None) -> Tuple[bool, Optional[Any]]: ...
    def wait(self, status: Optional[Status] = None) -> Any: ...
    @classmethod
    def testall(cls, requests: Sequence[Request], statuses: Optional[List[Status]] = None) -> Tuple[bool, Optional[List[Any]]]: ...
    @classmethod
    def waitall(cls, requests: Sequence[Request], statuses: Optional[List[Status]] = None) -> List[Any]: ...

class Message(Tuple[MPI.Message, ...]):
    @overload
    def __new__(cls, message: Optional[MPI.Message] = None) -> Message: ...
    @overload
    def __new__(cls, message: Iterable[MPI.Message]) -> Message: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __bool__(self) -> bool: ...
    def recv(self, status: Optional[Status] = None) -> Any: ...
    def irecv(self) -> Request: ...
    @classmethod
    def probe(
        cls,
        comm: MPI.Comm,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Optional[Status] = None,
    ) -> Message: ...
    @classmethod
    def iprobe(
        cls,
        comm: MPI.Comm,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Optional[Status] = None,
    ) -> Optional[Message]: ...

class Comm(MPI.Comm):
    def send(self, obj: Any, dest: int, tag: int = 0) -> None: ...
    def bsend(self, obj: Any, dest: int, tag: int = 0) -> None: ...
    def ssend(self, obj: Any, dest: int, tag: int = 0) -> None: ...
    def isend(self, obj: Any, dest: int, tag: int = 0) -> Request: ...  # type: ignore[override]
    def ibsend(self, obj: Any, dest: int, tag: int = 0) -> Request: ...  # type: ignore[override]
    def issend(self, obj: Any, dest: int, tag: int = 0) -> Request: ...  # type: ignore[override]
    def recv(
        self,
        buf: Optional[Buffer] = None,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Optional[Status] = None,
    ) -> Any: ...
    def irecv(  # type: ignore[override]
        self,
        buf: Optional[Buffer] = None,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
    ) -> Request: ...
    def sendrecv(
        self,
        sendobj: Any,
        dest: int,
        sendtag: int = 0,
        recvbuf: Optional[Buffer] = None,
        source: int = ANY_SOURCE,
        recvtag: int = ANY_TAG,
        status: Optional[Status] = None,
    ) -> Any: ...
    def mprobe(  # type: ignore[override]
        self,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Optional[Status] = None,
    ) -> Message: ...
    def improbe(  # type: ignore[override]
        self,
        source: int = ANY_SOURCE,
        tag: int = ANY_TAG,
        status: Optional[Status] = None,
    ) -> Optional[Message]: ...
    def bcast(
        self,
        obj: Any,
        root: int = 0,
    ) -> Any: ...

class Intracomm(Comm, MPI.Intracomm): ...
class Intercomm(Comm, MPI.Intercomm): ...
