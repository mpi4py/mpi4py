import sys
from typing import Any, Generic
from typing import Callable, Iterable, Iterator, Sequence, Mapping
if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
import weakref
import threading
from ..MPI  import Info, Intracomm, Intercomm, Request
from ._base import Executor, Future
from ..typing import T

_Task: TypeAlias = tuple[Callable[..., T], tuple[Any, ...], dict[str, Any]]
_Item: TypeAlias = tuple[Future[T], _Task[T]]
_Info: TypeAlias = Info | Mapping[str, str] | Iterable[tuple[str, str]]

def serialized(function: Callable[..., Any]) -> Callable[..., Any]: ...
def setup_mpi_threads() -> None: ...

class RemoteTraceback(Exception): ...
def sys_exception() -> BaseException: ...
def os_environ_get(name: str, default: T | None = ...) -> str | T | None: ...

BACKOFF: float = ...

class Backoff:
    tval: float
    tmax: float
    tmin: float
    def __init__(self, seconds: float = BACKOFF) -> None: ...
    def reset(self) -> None: ...
    def sleep(self) -> None: ...

class TaskQueue(Generic[T]):
    def put(self, x: T, /) -> None: ...
    def pop(self) -> T: ...
    def add(self, x: T, /) -> None: ...

class WorkerSet(Generic[T]):
    def add(self, x: T, /) -> None: ...
    def pop(self) -> T: ...

_WeakKeyDict: TypeAlias = weakref.WeakKeyDictionary
_ThreadQueueMap: TypeAlias = _WeakKeyDict[threading.Thread, TaskQueue[_Item[Any] | None]]
THREADS_QUEUES: _ThreadQueueMap = ...
def join_threads(threads_queues: _ThreadQueueMap = ...) -> None: ...

class Pool:
    size: int
    queue: TaskQueue[_Item[Any] | None]
    exref: weakref.ReferenceType[Executor]
    event: threading.Event
    thread: threading.Thread
    def __init__(
        self,
        executor: Executor,
        manager: Callable[..., None],
        *args: Any,
    ) -> None: ...
    def wait(self) -> None: ...
    def push(self, item: _Item[Any]) -> None: ...
    def done(self) -> None: ...
    def join(self) -> None: ...
    def setup(self, size: int) -> TaskQueue[_Item[Any] | None]: ...
    def cancel(
        self,
        handler: Callable[[Future[Any]], None] | None = ...,
    ) -> None: ...
    def broken(self, message: str) -> None: ...

def initialize(options: Mapping[str, Any]) -> bool: ...
def ThreadPool(executor: Executor) -> Pool: ...
def SpawnPool(executor: Executor) -> Pool: ...
def ServicePool(executor: Executor) -> Pool: ...
def WorkerPool(executor: Executor) -> Pool: ...

SharedPool: Callable[[Executor], Pool] | None = ...

class SharedPoolCtx:
    comm: Intercomm
    on_root: bool | None
    counter: Iterator[int]
    workers: WorkerSet[int]
    threads: _ThreadQueueMap
    def __init__(self) -> None: ...
    def __call__(self, executor: Executor) -> Pool: ...
    def __enter__(self) -> Self | None: ...
    def __exit__(self, *args: object) -> bool: ...

def comm_split(comm: Intracomm, root: int) -> tuple[Intercomm, Intracomm]: ...

def barrier(comm: Intercomm) -> None: ...
def bcast_send(comm: Intercomm, data: Any) -> None: ...
def bcast_recv(comm: Intercomm) -> Any: ...
def isendtoall(comm: Intercomm, data: Any, tag: int = 0) -> list[Request]: ...
def waitall(comm: Intercomm, requests: Sequence[Request], poll: bool = False) -> list[Any]: ...
def sendtoall(comm: Intercomm, data: Any, tag: int = 0) -> None: ...
def recvfromall(comm: Intercomm, tag: int = 0) -> list[Any]: ...
def disconnect(comm: Intercomm) -> None: ...

def client_sync(
    comm: Intercomm,
    options: Mapping[str, Any],
    sync: bool = ...,
) -> Intercomm: ...
def client_init(
    comm: Intercomm,
    options: Mapping[str, Any],
) -> bool: ...
def client_exec(
    comm: Intercomm,
    options: Mapping[str, Any],
    tag: int,
    worker_set: WorkerSet[int],
    task_queue: TaskQueue[_Item[Any] | None],
) -> None: ...
def client_stop(
    comm: Intercomm,
) -> None: ...

def server_sync(
    comm: Intercomm,
    sync: bool = ...,
) -> tuple[Intercomm, dict[str, Any]]: ...
def server_init(
    comm: Intercomm,
) -> bool: ...
def server_exec(
    comm: Intercomm,
    options: Mapping[str, Any],
) -> None: ...
def server_stop(
    comm: Intercomm,
) -> None: ...

MAIN_RUN_NAME: str = ...
def import_main(
    mod_name: str,
    mod_path: str,
    init_globals: dict[str, Any] | None,
    run_name: str,
) -> None: ...

FLAG_OPT_MAP: dict[str, str]
def get_python_flags() -> list[str]: ...
def get_max_workers() -> int: ...
def get_spawn_module() -> str: ...
def client_spawn(
    python_exe: str | None = ...,
    python_args: Sequence[str] | None = ...,
    max_workers: int | None = ...,
    mpi_info: _Info | None = ...,
) -> Intercomm: ...

SERVICE: str = ...
SERVER_HOST: str = ...
SERVER_BIND: str = ...
SERVER_PORT: int = ...
def get_service() -> str: ...
def get_server_host() -> str: ...
def get_server_bind() -> str: ...
def get_server_port() -> int: ...
_Address: TypeAlias = tuple[str | None, int | None]
def client_lookup(address: _Address) -> str: ...
def server_publish(address: _Address, mpi_port: str) -> None: ...
def client_connect(
    service: str | _Address,
    mpi_info: _Info | None = ...,
) -> Intercomm: ...
def server_accept(
    service: str | _Address,
    mpi_info: _Info | None = ...,
    comm: Intracomm = ...,
    root: int = ...,
) -> Intercomm: ...

def get_comm_server() -> Intracomm: ...
def set_comm_server(intracomm: Intracomm) -> None: ...
def server_main_comm(comm: Intercomm, sync: bool = ...) -> None: ...
def server_main_spawn() -> None: ...
def server_main_service() -> None: ...
def server_main() -> None: ...
