import weakref
import threading
from ..MPI  import Info, Intracomm, Intercomm
from ._core import Executor, Future
from typing import Any, Optional, Union, Generic, TypeVar
from typing import Callable, Iterable, Iterator, Sequence, Mapping
from typing import List, Tuple, Dict

_T = TypeVar("_T")
_Task = Tuple[Callable[..., _T], Tuple, Dict[str, Any]]
_Item = Tuple[Future[_T], _Task[_T]]
_Info = Union[Info, Mapping[str, str], Iterable[Tuple[str, str]]]

def serialized(function: Callable[..., Any]) -> Callable[..., Any]: ...
def setup_mpi_threads() -> None: ...

class RemoteTraceback(Exception): pass
def sys_exception() -> BaseException: ...
def os_environ_get(name: str, default: Optional[_T] = None) -> Union[str, Optional[_T]]: ...

BACKOFF: float = ...

class Backoff:
    tval: float
    tmax: float
    tmin: float
    def __init__(self, seconds: float = BACKOFF) -> None: ...
    def reset(self) -> None: ...
    def sleep(self) -> None: ...

class TaskQueue(Generic[_T]):
    def put(self, x: _T) -> None: ...
    def pop(self) -> _T: ...
    def add(self, x: _T) -> None: ...

class WorkerSet(Generic[_T]):
    def add(self, x: _T) -> None: ...
    def pop(self) -> _T: ...

_WeakKeyDict = weakref.WeakKeyDictionary
_ThreadQueueMap = _WeakKeyDict[threading.Thread, TaskQueue[Optional[_Item[Any]]]]
THREADS_QUEUES: _ThreadQueueMap = ...
def join_threads(threads_queues: _ThreadQueueMap = ...) -> None: ...

class Pool:
    size: int
    queue: TaskQueue[Optional[_Item[Any]]]
    exref: weakref.ReferenceType[Executor]
    event: threading.Event
    thread: threading.Thread
    def __init__(self,
        executor: Executor,
        manager: Callable[..., None],
        *args: Any,
    ) -> None: ...
    def wait(self) -> None: ...
    def push(self, item: _Item[Any]) -> None: ...
    def done(self) -> None: ...
    def join(self) -> None: ...
    def setup(self, size: int) -> TaskQueue: ...
    def cancel(self, handler: Optional[Callable[[Future], None]] = None) -> None: ...
    def broken(self, message: str) -> None: ...

def initialize(options: Mapping[str, Any]) -> bool: ...
def ThreadPool(executor: Executor) -> Pool: ...
def SplitPool(executor: Executor, comm: Intracomm, root: int) -> Pool: ...
def SpawnPool(executor: Executor) -> Pool: ...
def ServicePool(executor: Executor) -> Pool: ...
def WorkerPool(executor: Executor) -> Pool: ...

SharedPool: Optional[Callable[[Executor], Pool]] = None

class SharedPoolCtx:
    comm: Intercomm
    on_root: Optional[bool]
    counter: Iterator[int]
    workers: WorkerSet[int]
    threads: _ThreadQueueMap
    def __init__(self) -> None: ...
    def __call__(self, executor: Executor) -> Pool: ...
    def __enter__(self) -> Optional[SharedPoolCtx]: ...
    def __exit__(self, *args: Any) -> bool: ...

def barrier(comm: Intercomm) -> None: ...
def bcast_send(comm: Intercomm, data: Any) -> None: ...
def bcast_recv(comm: Intercomm) -> Any: ...

def client_sync(comm: Intercomm, options: Any, full: bool = True) -> None: ...
def client_comm(comm: Intercomm, options: Any) -> Intercomm: ...
def client_init(comm: Intercomm, options: Any) -> bool: ...
def client_exec(comm: Intercomm, options: Any,
                tag: int, worker_set: WorkerSet[int],
                task_queue: TaskQueue[Optional[_Item[Any]]],
                ) -> None: ...
def client_close(comm: Intercomm) -> None: ...

def server_sync(comm: Intercomm, full: bool = True) -> Any: ...
def server_comm(comm: Intercomm, options: Any) -> Intercomm: ...
def server_init(comm: Intercomm) -> bool: ...
def server_exec(comm: Intercomm, options: Any) -> None: ...
def server_close(comm: Intercomm) -> None: ...

def get_comm_world() -> Intracomm: ...
def comm_split(comm: Intracomm, root: int = 0) -> Intercomm: ...

MAIN_RUN_NAME: str = ...
def import_main(mod_name: str,
                mod_path: str,
                init_globals: Optional[Dict[str, Any]],
                run_name: str,
                ) -> None: ...

FLAG_OPT_MAP: Dict[str, str]
def get_python_flags() -> List[str]: ...
def get_max_workers() -> int: ...
def get_spawn_module() -> str: ...
def client_spawn(python_exe: Optional[str] = ...,
                 python_args: Optional[Sequence[str]] = ...,
                 max_workers: Optional[int] = ...,
                 mpi_info: Optional[_Info] = ...,
                 ) -> Intercomm: ...

SERVICE: str = ...
SERVER_HOST: str = ...
SERVER_BIND: str = ...
SERVER_PORT: int = ...
def get_service() -> str: ...
def get_server_host() -> str: ...
def get_server_bind() -> str: ...
def get_server_port() -> int: ...
_Address = Tuple[Optional[str], Optional[int]]
def client_lookup(address: _Address): ...
def server_publish(address: _Address, mpi_port: str) -> None: ...
def client_connect(service: Union[str, _Address],
                   mpi_info: Optional[_Info] = ...,
                   ) -> Intercomm: ...
def server_accept(service: Union[str, _Address],
                  mpi_info: Optional[_Info] = ...,
                  root: int = ...,
                  comm: Intracomm = ...,
                  ) -> Intercomm: ...

def server_main_comm(comm: Intercomm, full: bool = True) -> None: ...
def server_main_split(comm: Intracomm, root: int) -> None: ...
def server_main_spawn() -> None: ...
def server_main_service() -> None: ...
def server_main() -> None: ...
