# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Management of MPI worker processes."""
# pylint: disable=broad-except
# pylint: disable=too-many-lines
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import os
import sys
import time
import atexit
import weakref
import warnings
import itertools
import threading
import traceback
import collections

from .. import MPI
from ..util import pkl5
from ._base import BrokenExecutor


# ---

_tls = threading.local()


def serialized(function):
    def wrapper(*args, **kwargs):
        with serialized.lock:
            return function(*args, **kwargs)
    if serialized.lock is None:
        return function
    return wrapper


serialized.lock = None  # type: ignore[attr-defined]


def setup_mpi_threads():
    with setup_mpi_threads.lock:
        thread_level = setup_mpi_threads.thread_level
        if thread_level is None:
            thread_level = MPI.Query_thread()
            setup_mpi_threads.thread_level = thread_level
            if thread_level < MPI.THREAD_MULTIPLE:
                serialized.lock = threading.Lock()
    if thread_level < MPI.THREAD_SERIALIZED:
        warnings.warn(
            "the level of thread support in MPI "
            "should be at least MPI_THREAD_SERIALIZED",
            RuntimeWarning, stacklevel=2,
        )


setup_mpi_threads.lock = threading.Lock()  # type: ignore[attr-defined]
setup_mpi_threads.thread_level = None      # type: ignore[attr-defined]


# ---

class RemoteTraceback(Exception):
    pass


def _unwrap_exc(exc, tb):
    exc.__cause__ = RemoteTraceback(tb)
    return exc


class _ExceptionWrapper(Exception):
    def __reduce__(self):
        return _unwrap_exc, self.args


def _wrap_exc(exc, tb):
    exc.__cause__ = None
    exc.__context__ = None
    exc.__traceback__ = None
    return _ExceptionWrapper(exc, tb)


def _format_exc(exc, comm):
    exc_info = (type(exc), exc, exc.__traceback__)
    tb_lines = traceback.format_exception(*exc_info)
    body = "".join(tb_lines)
    host = MPI.Get_processor_name()
    rank = comm.Get_rank()
    size = comm.Get_size()
    info = f"### Worker {rank} of {size} on {host}\n"
    return f'\n{info}"""\n{body}"""'


if sys.version_info >= (3, 11):

    def sys_exception():
        return sys.exception()

else:  # pragma: no cover

    def sys_exception():
        return sys.exc_info()[1]


def os_environ_get(name, default=None):
    varname = f'MPI4PY_FUTURES_{name}'
    if varname not in os.environ:
        oldname = f'MPI4PY_{name}'
        if oldname in os.environ:  # pragma: no cover
            warnings.warn(
                f"environment variable {oldname} is deprecated, use {varname}",
                DeprecationWarning, stacklevel=1,
            )
            return os.environ[oldname]
    return os.environ.get(varname, default)


# ---


BACKOFF = 0.001


def _getopt_backoff(options):
    backoff = options.get('backoff')
    if backoff is None:
        backoff = os_environ_get('BACKOFF', BACKOFF)
    return float(backoff)


class Backoff:

    def __init__(self, seconds=BACKOFF):
        self.tval = 0.0
        self.tmax = max(float(seconds), 0.0)
        self.tmin = self.tmax / (1 << 10)

    def reset(self):
        self.tval = 0.0

    def sleep(self):
        time.sleep(self.tval)
        self.tval = min(self.tmax, max(self.tmin, self.tval * 2))


class TaskQueue(collections.deque):
    put = collections.deque.append
    pop = collections.deque.popleft
    add = collections.deque.appendleft


class WorkerSet(collections.deque):
    add = collections.deque.append
    pop = collections.deque.popleft


THREADS_QUEUES = weakref.WeakKeyDictionary()  # type: weakref.WeakKeyDictionary


def join_threads(threads_queues=THREADS_QUEUES):
    items = list(threads_queues.items())
    for _, queue in items:   # pragma: no cover
        queue.put(None)
    for thread, _ in items:  # pragma: no cover
        thread.join()


if hasattr(threading, '_register_atexit'):
    threading._register_atexit(join_threads)
else:  # pragma: no cover
    atexit.register(join_threads)


class Pool:

    def __init__(self, executor, manager, *args):
        self.size = None
        self.event = threading.Event()
        self.queue = queue = TaskQueue()
        self.exref = weakref.ref(executor, lambda _, q=queue: q.put(None))

        args = (self, executor._options, *args)
        thread = threading.Thread(target=manager, args=args)
        self.thread = thread

        setup_mpi_threads()
        thread.daemon = not hasattr(threading, '_register_atexit')
        thread.start()
        THREADS_QUEUES[thread] = queue

    def wait(self):
        self.event.wait()

    def push(self, item):
        self.queue.put(item)

    def done(self):
        self.queue.put(None)

    def join(self):
        self.thread.join()

    def setup(self, size):
        self.size = size
        self.event.set()
        return self.queue

    def cancel(self, handler=None):
        queue = self.queue
        while True:
            try:
                item = queue.pop()
            except LookupError:
                break
            if item is None:
                queue.put(None)
                break
            future, task = item
            if handler:
                handler(future)
            else:
                future.cancel()
                future.set_running_or_notify_cancel()
            del future, task, item

    def broken(self, message):
        lock = None
        executor = self.exref()
        if executor is not None:
            executor._broken = message
            if not executor._shutdown:
                lock = executor._lock

        def handler(future):
            if future.set_running_or_notify_cancel():
                exception = BrokenExecutor(message)
                future.set_exception(exception)

        self.event.set()
        if lock:
            lock.acquire()
        try:
            self.cancel(handler)
        finally:
            if lock:
                lock.release()


def initialize(options):
    initializer = options.pop('initializer', None)
    initargs = options.pop('initargs', ())
    initkwargs = options.pop('initkwargs', {})
    if initializer is not None:
        try:
            initializer(*initargs, **initkwargs)
        except BaseException:
            return False
        else:
            return True
    return True


def _manager_thread(pool, options):
    size = options.pop('max_workers', 1)
    queue = pool.setup(size)
    threads = collections.deque()
    max_threads = size - 1

    def init():
        if not initialize(options):
            pool.broken("initializer failed")
            return False
        return True

    def adjust():
        if len(threads) < max_threads:
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

    def execute(future, task):
        func, args, kwargs = task
        result = exception = None
        try:
            result = func(*args, **kwargs)
            future.set_result(result)
        except BaseException:
            exception = sys_exception()
            future.set_exception(exception)
        del result, exception
        del func, args, kwargs
        del future, task

    def finalize():
        for thread in threads:
            thread.join()
        queue.pop()

    def worker():
        backoff = Backoff(_getopt_backoff(options))
        if not init():
            queue.put(None)
            return
        while True:
            try:
                item = queue.pop()
                backoff.reset()
            except LookupError:
                backoff.sleep()
                continue
            if item is None:
                queue.put(None)
                break
            future, task = item
            if future.set_running_or_notify_cancel():
                if queue:
                    adjust()
                execute(future, task)
            del future, task, item

    worker()
    finalize()


def _manager_comm(pool, options, comm, sync=True):
    assert comm != MPI.COMM_NULL  # noqa: S101
    assert comm.Is_inter()        # noqa: S101
    assert comm.Get_size() == 1   # noqa: S101
    comm = client_sync(comm, options, sync)
    if not client_init(comm, options):
        pool.broken("initializer failed")
        client_stop(comm)
        return
    size = comm.Get_remote_size()
    queue = pool.setup(size)
    workers = WorkerSet(range(size))
    client_exec(comm, options, 0, workers, queue)
    client_stop(comm)


def _manager_spawn(pool, options):
    pyexe = options.pop('python_exe', None)
    pyargs = options.pop('python_args', None)
    nprocs = options.pop('max_workers', None)
    info = options.pop('mpi_info', None)
    comm = serialized(client_spawn)(pyexe, pyargs, nprocs, info)
    _manager_comm(pool, options, comm)


def _manager_service(pool, options):
    service = options.pop('service', None)
    info = options.pop('mpi_info', None)
    comm = serialized(client_connect)(service, info)
    _manager_comm(pool, options, comm)


def ThreadPool(executor):
    # pylint: disable=invalid-name
    return Pool(executor, _manager_thread)


def SpawnPool(executor):
    # pylint: disable=invalid-name
    return Pool(executor, _manager_spawn)


def ServicePool(executor):
    # pylint: disable=invalid-name
    return Pool(executor, _manager_service)


def WorkerPool(executor):
    # pylint: disable=invalid-name
    if SharedPool is not None:
        return SharedPool(executor)
    if 'service' in executor._options:
        return ServicePool(executor)
    return SpawnPool(executor)


# ---

SharedPool = None  # pylint: disable=invalid-name


def _set_shared_pool(obj):
    # pylint: disable=global-statement
    global SharedPool
    SharedPool = obj


class SharedPoolCtx:

    def __init__(self):
        self.lock = threading.Lock()
        self.comm = MPI.COMM_NULL
        self.intracomm = MPI.COMM_NULL
        self.on_root = None
        self.counter = None
        self.workers = None
        self.threads = weakref.WeakKeyDictionary()

    def __reduce__(self):
        return 'SharedPool'

    def _initialize_remote(self):
        barrier(self.intracomm)
        server_init(self.comm)

    def _initialize(self, options, tag):
        if tag == 0:
            self.comm = client_sync(self.comm, options)
            return client_init(self.comm, options)
        if options.get('initializer') is None:
            return True
        task = (self._initialize_remote, (), {})
        reqs = isendtoall(self.comm, task, tag)
        waitall(self.comm, reqs, poll=True)
        success = client_init(self.comm, options)
        recvfromall(self.comm, tag)
        return success

    def _manager(self, pool, options):
        if self.counter is None:
            options['max_workers'] = 1
            set_comm_server(MPI.COMM_SELF)
            _manager_thread(pool, options)
            return
        with self.lock:
            tag = next(self.counter)
            if not self._initialize(options, tag):
                pool.broken("initializer failed")
                return
        comm = self.comm
        size = comm.Get_remote_size()
        queue = pool.setup(size)
        client_exec(comm, options, tag, self.workers, queue)

    def __call__(self, executor):
        assert SharedPool is self  # noqa: S101
        with self.lock:
            pool = Pool(executor, self._manager)
            del THREADS_QUEUES[pool.thread]
            self.threads[pool.thread] = pool.queue
        return pool

    def __enter__(self):
        assert SharedPool is None  # noqa: S101
        comm, root = MPI.COMM_WORLD, 0
        self.on_root = comm.Get_rank() == root
        self.comm, self.intracomm = comm_split(comm, root)
        if self.comm != MPI.COMM_NULL and self.on_root:
            size = self.comm.Get_remote_size()
            self.counter = itertools.count(0)
            self.workers = WorkerSet(range(size))
        _set_shared_pool(self)
        return self if self.on_root else None

    def __exit__(self, *args):
        assert SharedPool is self  # noqa: S101
        if self.on_root:
            join_threads(self.threads)
        if self.comm != MPI.COMM_NULL:
            comm = self.comm
            if self.on_root:
                if next(self.counter) == 0:
                    options = {'main': False}
                    self._initialize(options, 0)
                client_stop(comm)
            else:
                intracomm = self.intracomm
                set_comm_server(intracomm)
                server_main_comm(comm)
                intracomm.Free()
        if not self.on_root:
            join_threads(self.threads)
        _set_shared_pool(None)
        self.comm = MPI.COMM_NULL
        self.intracomm = MPI.COMM_NULL
        self.on_root = None
        self.counter = None
        self.workers = None
        self.threads.clear()
        return False


# ---


def comm_split(comm, root):
    if comm.Get_size() == 1:
        comm = MPI.Intercomm(MPI.COMM_NULL)
        intracomm = MPI.Intracomm(MPI.COMM_NULL)
        return comm, intracomm
    rank = comm.Get_rank()
    if MPI.Get_version() >= (2, 2):
        allgroup = comm.Get_group()
        if rank == root:
            group = allgroup.Incl([root])
        else:
            group = allgroup.Excl([root])
        allgroup.Free()
        intracomm = comm.Create(group)
        group.Free()
    else:  # pragma: no cover
        color = 0 if rank == root else 1
        intracomm = comm.Split(color, key=0)

    if rank == root:
        local_leader = 0
        remote_leader = 0 if root else 1
    else:
        local_leader = 0
        remote_leader = root
    intercomm = intracomm.Create_intercomm(
        local_leader, comm, remote_leader, tag=0)
    if rank == root:
        intracomm.Free()
    return intercomm, intracomm


# ---


def _comm_executor_helper(executor, comm, root):

    def _manager(pool, options, comm, root):
        if comm.Get_size() == 1:
            options['max_workers'] = 1
            set_comm_server(MPI.COMM_SELF)
            _manager_thread(pool, options)
            return
        comm, _ = serialized(comm_split)(comm, root)
        _manager_comm(pool, options, comm, sync=False)

    if comm.Get_rank() == root:
        if SharedPool is not None:
            pool = SharedPool(executor)
        else:
            pool = Pool(executor, _manager, comm, root)
        executor._pool = pool
    else:
        comm, intracomm = comm_split(comm, root)
        set_comm_server(intracomm)
        server_main_comm(comm, sync=False)
        intracomm.Free()


# ---


def _getenv_use_pkl5():
    value = os_environ_get('USE_PKL5')
    if value is None:
        return None
    if value.lower() in ('false', 'no', 'off', 'n', '0'):
        return False
    if value.lower() in ('true', 'yes', 'on', 'y', '1'):
        return True
    warnings.warn(
        f"environment variable MPI4PY_FUTURES_USE_PKL5: "
        f"unexpected value {value!r}",
        RuntimeWarning, stacklevel=1,
    )
    return False


def _setopt_use_pkl5(options):
    use_pkl5 = options.get('use_pkl5')
    if use_pkl5 is None:
        use_pkl5 = _getenv_use_pkl5()
    if use_pkl5 is not None:
        options['use_pkl5'] = use_pkl5


def _get_comm(comm, options):
    use_pkl5 = options.pop('use_pkl5', None)
    if use_pkl5:
        return pkl5.Intercomm(comm)
    return comm


def _get_request(comm):
    use_pkl5 = isinstance(comm, pkl5.Comm)
    if use_pkl5:
        return pkl5.Request
    return MPI.Request


# ---


def barrier(comm):
    try:
        request = comm.Ibarrier()
        backoff = Backoff()
        while not request.Test():
            backoff.sleep()
    except (NotImplementedError, MPI.Exception):  # pragma: no cover
        buf = [None, 0, MPI.BYTE]
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        sendreqs, recvreqs = [], []
        if comm.Is_inter():
            size = comm.Get_remote_size()
        else:
            size = comm.Get_size()
        for pid in range(size):
            recvreqs.append(comm.Irecv(buf, pid, tag))
            sendreqs.append(comm.Issend(buf, pid, tag))
        backoff = Backoff()
        while not MPI.Request.Testall(recvreqs):
            backoff.sleep()
        MPI.Request.Waitall(sendreqs)


def bcast_send(comm, data):
    if MPI.VERSION >= 2:
        comm.bcast(data, MPI.ROOT)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        sendtoall(comm, data, tag)


def bcast_recv(comm):
    if MPI.VERSION >= 2:
        data = comm.bcast(None, 0)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        data = comm.recv(None, 0, tag)
    return data


def isendtoall(comm, data, tag=0):
    size = comm.Get_remote_size()
    return [comm.issend(data, pid, tag) for pid in range(size)]


def waitall(comm, requests, poll=False):
    if poll:
        request_testall = _get_request(comm).testall
        backoff = Backoff()
        while True:
            done, objs = request_testall(requests)
            if done:
                return objs
            backoff.sleep()
    else:
        request_waitall = _get_request(comm).waitall
        return request_waitall(requests)


def sendtoall(comm, data, tag=0):
    requests = isendtoall(comm, data, tag)
    waitall(comm, requests)


def recvfromall(comm, tag=0):
    size = comm.Get_remote_size()
    return [comm.recv(None, pid, tag) for pid in range(size)]


def disconnect(comm):
    try:
        comm.Disconnect()
    except NotImplementedError:  # pragma: no cover
        comm.Free()


# ---


def client_sync(comm, options, sync=True):
    serialized(barrier)(comm)
    _setopt_use_pkl5(options)
    if sync:
        options = _sync_get_data(options)
    serialized(bcast_send)(comm, options)
    comm = _get_comm(comm, options)
    return comm


def client_init(comm, options):
    serialized(bcast_send)(comm, _init_get_data(options))
    sbuf = bytearray([False])
    rbuf = bytearray([False])
    serialized(comm.Allreduce)(sbuf, rbuf, op=MPI.LAND)
    success = bool(rbuf[0])
    return success


def client_exec(comm, options, tag, worker_set, task_queue):
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    backoff = Backoff(_getopt_backoff(options))

    status = MPI.Status()
    comm_recv = serialized(comm.recv)
    comm_isend = serialized(comm.issend)
    comm_iprobe = serialized(comm.iprobe)
    request_free = serialized(_get_request(comm).Free)

    pending = {}

    def iprobe():
        pid = MPI.ANY_SOURCE
        return comm_iprobe(pid, tag, status)

    def probe():
        pid = MPI.ANY_SOURCE
        backoff.reset()
        while not comm_iprobe(pid, tag, status):
            backoff.sleep()

    def recv():
        pid = MPI.ANY_SOURCE
        try:
            task = comm_recv(None, pid, tag, status)
        except BaseException:
            task = (None, sys_exception())
        pid = status.source
        worker_set.add(pid)

        future, request = pending.pop(pid)
        request_free(request)
        result, exception = task
        if exception is None:
            future.set_result(result)
        else:
            future.set_exception(exception)

        del result, exception
        del future, task

    def send():
        try:
            pid = worker_set.pop()
        except LookupError:  # pragma: no cover
            return False

        try:
            item = task_queue.pop()
        except LookupError:  # pragma: no cover
            worker_set.add(pid)
            return False

        if item is None:
            worker_set.add(pid)
            return True

        future, task = item
        if not future.set_running_or_notify_cancel():
            worker_set.add(pid)
            return False

        try:
            request = comm_isend(task, pid, tag)
            pending[pid] = (future, request)
        except BaseException:
            worker_set.add(pid)
            future.set_exception(sys_exception())

        del future, task, item
        return None

    while True:
        if task_queue and worker_set:
            backoff.reset()
            stop = send()
            if stop:
                break
        if pending and iprobe():
            backoff.reset()
            recv()
        backoff.sleep()
    while pending:
        probe()
        recv()


def client_stop(comm):
    serialized(sendtoall)(comm, None)
    serialized(disconnect)(comm)


def server_sync(comm, sync=True):
    barrier(comm)
    options = bcast_recv(comm)
    if sync:
        options = _sync_set_data(options)
    comm = _get_comm(comm, options)
    return comm, options


def server_init(comm):
    options = bcast_recv(comm)
    success = initialize(options)
    sbuf = bytearray([success])
    rbuf = bytearray([True])
    comm.Allreduce(sbuf, rbuf, op=MPI.LAND)
    return success


def server_exec(comm, options):
    backoff = Backoff(_getopt_backoff(options))

    status = MPI.Status()
    comm_recv = comm.recv
    comm_isend = comm.issend
    comm_iprobe = comm.iprobe
    request_test = _get_request(comm).test

    def exception():
        exc = sys_exception()
        tb = _format_exc(exc, comm)
        return _wrap_exc(exc, tb)

    def recv():
        pid, tag = MPI.ANY_SOURCE, MPI.ANY_TAG
        backoff.reset()
        while not comm_iprobe(pid, tag, status):
            backoff.sleep()
        pid, tag = status.source, status.tag
        try:
            task = comm_recv(None, pid, tag, status)
        except BaseException:
            task = exception()
        return task

    def call(task):
        if isinstance(task, BaseException):
            return (None, task)
        func, args, kwargs = task
        try:
            result = func(*args, **kwargs)
        except BaseException:
            return (None, exception())
        else:
            return (result, None)

    def send(task):
        pid, tag = status.source, status.tag
        try:
            request = comm_isend(task, pid, tag)
        except BaseException:
            task = (None, exception())
            request = comm_isend(task, pid, tag)
        backoff.reset()
        while not request_test(request)[0]:
            backoff.sleep()

    while True:
        task = recv()
        if task is None:
            break
        task = call(task)
        send(task)


def server_stop(comm):
    disconnect(comm)


# ---

MAIN_RUN_NAME = '__worker__'


def import_main(mod_name, mod_path, init_globals, run_name):
    import types
    import runpy

    module = types.ModuleType(run_name)
    if init_globals is not None:
        module.__dict__.update(init_globals)
        module.__name__ = run_name

    class TempModulePatch(runpy._TempModule):
        # pylint: disable=too-few-public-methods
        def __init__(self, mod_name):
            super().__init__(mod_name)
            self.module = module

    TempModule = runpy._TempModule  # pylint: disable=invalid-name
    runpy._TempModule = TempModulePatch
    import_main.sentinel = (mod_name, mod_path)
    main_module = sys.modules['__main__']
    try:
        sys.modules['__main__'] = sys.modules[run_name] = module
        if mod_name:  # pragma: no cover
            runpy.run_module(mod_name, run_name=run_name, alter_sys=True)
        elif mod_path:  # pragma: no branch
            safe_path = getattr(sys.flags, 'safe_path', sys.flags.isolated)
            if not safe_path:  # pragma: no branch
                sys.path[0] = os.path.realpath(os.path.dirname(mod_path))
            runpy.run_path(mod_path, run_name=run_name)
        sys.modules['__main__'] = sys.modules[run_name] = module
    except BaseException:  # pragma: no cover
        sys.modules['__main__'] = main_module
        raise
    finally:
        del import_main.sentinel
        runpy._TempModule = TempModule


def _sync_get_data(options):
    main = sys.modules['__main__']
    sys.modules.setdefault(MAIN_RUN_NAME, main)
    import_main_module = options.pop('main', True)

    data = options.copy()
    data.pop('initializer', None)
    data.pop('initargs', None)
    data.pop('initkwargs', None)

    if import_main_module:
        spec = getattr(main, '__spec__', None)
        name = getattr(spec, 'name', None)
        path = getattr(main, '__file__', None)
        if name is not None:  # pragma: no cover
            data['@main:mod_name'] = name
        if path is not None:  # pragma: no branch
            data['@main:mod_path'] = path

    return data


def _sync_set_data(data):
    if 'path' in data:
        sys.path.extend(data.pop('path'))
    if 'wdir' in data:
        os.chdir(data.pop('wdir'))
    if 'env' in data:
        os.environ.update(data.pop('env'))

    mod_name = data.pop('@main:mod_name', None)
    mod_path = data.pop('@main:mod_path', None)
    mod_glbs = data.pop('globals', None)
    import_main(mod_name, mod_path, mod_glbs, MAIN_RUN_NAME)

    return data


def _init_get_data(options):
    keys = ('initializer', 'initargs', 'initkwargs')
    vals = (None, (), {})
    data = {k: options.pop(k, v) for k, v in zip(keys, vals)}
    return data


# ---


def _check_recursive_spawn():  # pragma: no cover
    if not hasattr(import_main, 'sentinel'):
        return
    main_name, main_path = import_main.sentinel
    main_info = "\n"
    if main_name is not None:
        main_info += f"    main name: {main_name!r}\n"
    if main_path is not None:
        main_info += f"    main path: {main_path!r}\n"
    main_info += "\n"
    sys.stderr.write("""
    The main script or module attempted to spawn new MPI worker processes.
    This probably means that you have forgotten to use the proper idiom in
    your main script or module:

        if __name__ == '__main__':
            ...

    This error is unrecoverable. The MPI execution environment had to be
    aborted. The name/path of the offending main script/module follows:
    """ + main_info)
    sys.stderr.flush()
    time.sleep(1)
    MPI.COMM_WORLD.Abort(1)


FLAG_OPT_MAP = {
    'debug': 'd',
    'inspect': 'i',
    'interactive': 'i',
    'optimize': 'O',
    'dont_write_bytecode': 'B',
    'no_user_site': 's',
    'no_site': 'S',
    'ignore_environment': 'E',
    'verbose': 'v',
    'bytes_warning': 'b',
    'quiet': 'q',
    'hash_randomization': 'R',
    'isolated': 'I',
    # 'dev_mode': 'Xdev',
    # 'utf8_mode': 'Xutf8',
    # 'warn_default_encoding': 'Xwarn_default_encoding',
    'safe_path': 'P',
    # 'int_max_str_digits': 'Xint_max_str_digits=0'
}


def get_python_flags():
    args = []
    for flag, opt in FLAG_OPT_MAP.items():
        val = getattr(sys.flags, flag, 0)
        val = val if opt[0] != 'i' else 0
        val = val if opt[0] != 'Q' else min(val, 1)
        if val > 0:
            args.append('-' + opt * val)
    for opt in sys.warnoptions:  # pragma: no cover
        args.append('-W' + opt)
    sys_xoptions = getattr(sys, '_xoptions', {})
    for opt, val in sys_xoptions.items():  # pragma: no cover
        args.append('-X' + opt if val is True else
                    '-X' + opt + '=' + val)
    return args


def get_max_workers():
    max_workers = os_environ_get('MAX_WORKERS')
    if max_workers is not None:
        return int(max_workers)
    if MPI.UNIVERSE_SIZE != MPI.KEYVAL_INVALID:  # pragma: no branch
        universe_size = MPI.COMM_WORLD.Get_attr(MPI.UNIVERSE_SIZE)
        if universe_size is not None:  # pragma: no cover
            world_size = MPI.COMM_WORLD.Get_size()
            return max(universe_size - world_size, 1)
    return 1


def get_spawn_module():
    return __spec__.parent + '.server'


def client_spawn(
    python_exe=None,
    python_args=None,
    max_workers=None,
    mpi_info=None,
):
    _check_recursive_spawn()
    if python_exe is None:
        python_exe = sys.executable
    if python_args is None:
        python_args = []
    if max_workers is None:
        max_workers = get_max_workers()
    if mpi_info is None:
        mpi_info = {'soft': f'1:{max_workers}'}

    args = get_python_flags() + list(python_args)
    args.extend(['-m', get_spawn_module()])
    info = MPI.Info.Create()
    info.update(mpi_info)
    comm = MPI.COMM_SELF.Spawn(python_exe, args, max_workers, info)
    info.Free()
    return comm


# ---


SERVICE = __spec__.parent
SERVER_HOST = 'localhost'
SERVER_BIND = ''
SERVER_PORT = 31415


def get_service():
    return os_environ_get('SERVICE', SERVICE)


def get_server_host():
    return os_environ_get('SERVER_HOST', SERVER_HOST)


def get_server_bind():
    return os_environ_get('SERVER_BIND', SERVER_BIND)


def get_server_port():
    return int(os_environ_get('SERVER_PORT', SERVER_PORT))


def client_lookup(address):
    from socket import socket
    host, port = address
    host = host or get_server_host()
    port = port or get_server_port()
    address = (host, int(port))
    sock = socket()
    sock.connect(address)
    try:
        fdes = sock.fileno()
        peer = MPI.Comm.Join(fdes)
    finally:
        sock.close()
    mpi_port = peer.recv(None, 0)
    peer.Disconnect()
    return mpi_port


def server_publish(address, mpi_port):
    from socket import socket
    from socket import SOL_SOCKET, SO_REUSEADDR
    host, port = address
    host = host or get_server_bind()
    port = port or get_server_port()
    address = (host, int(port))
    serversock = socket()
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(address)
    serversock.listen(0)
    try:
        sock = serversock.accept()[0]
    finally:
        serversock.close()
    try:
        fdes = sock.fileno()
        peer = MPI.Comm.Join(fdes)
    finally:
        sock.close()
    peer.send(mpi_port, 0)
    peer.Disconnect()


def client_connect(service, mpi_info=None):
    info = MPI.INFO_NULL
    if mpi_info:
        info = MPI.Info.Create()
        info.update(mpi_info)
    if not isinstance(service, (list, tuple)):
        service = service or get_service()
        port = MPI.Lookup_name(service, info)
    else:
        port = client_lookup(service)

    comm = MPI.COMM_SELF.Connect(port, info, root=0)
    if info != MPI.INFO_NULL:
        info.Free()
    return comm


def server_accept(
    service,
    mpi_info=None,
    comm=MPI.COMM_WORLD,
    root=0,
):
    info = MPI.INFO_NULL
    if comm.Get_rank() == root:
        if mpi_info:
            info = MPI.Info.Create()
            info.update(mpi_info)
    port = None
    if comm.Get_rank() == root:
        port = MPI.Open_port(info)
    if comm.Get_rank() == root:
        if not isinstance(service, (list, tuple)):
            service = service or get_service()
            MPI.Publish_name(service, port, info)
        else:
            server_publish(service, port)
            service = None

    comm = comm.Accept(port, info, root)
    if port is not None:
        if service is not None:
            MPI.Unpublish_name(service, port, info)
        MPI.Close_port(port)
    if info != MPI.INFO_NULL:
        info.Free()
    return comm


# ---

def get_comm_server():
    try:
        return _tls.comm_server
    except AttributeError:
        raise RuntimeError(
            "communicator is not accessible"
        ) from None


def set_comm_server(intracomm):
    _tls.comm_server = intracomm


def server_main_comm(comm, sync=True):
    assert comm != MPI.COMM_NULL        # noqa: S101
    assert comm.Is_inter()              # noqa: S101
    assert comm.Get_remote_size() == 1  # noqa: S101
    comm, options = server_sync(comm, sync)
    server_init(comm)
    server_exec(comm, options)
    server_stop(comm)


def server_main_spawn():
    comm = MPI.Comm.Get_parent()
    set_comm_server(MPI.COMM_WORLD)
    server_main_comm(comm)


def server_main_service():
    from getopt import getopt  # pylint: disable=deprecated-module
    longopts = ['bind=', 'port=', 'service=', 'info=']
    optlist, _ = getopt(sys.argv[1:], '', longopts)
    optdict = {opt[2:]: val for opt, val in optlist}

    if 'bind' in optdict or 'port' in optdict:
        bind = optdict.get('bind') or get_server_bind()
        port = optdict.get('port') or get_server_port()
        service = (bind, int(port))
    else:
        service = optdict.get('service') or get_service()
    info = optdict.get('info', '').split(',')
    info = dict(k_v.split('=', 1) for k_v in info if k_v)

    comm = server_accept(service, info)
    set_comm_server(MPI.COMM_WORLD)
    server_main_comm(comm)


def server_main():
    from ..run import set_abort_status
    try:
        comm = MPI.Comm.Get_parent()
        if comm != MPI.COMM_NULL:
            server_main_spawn()
        else:
            server_main_service()
    except BaseException:
        set_abort_status(1)
        raise


# ---
