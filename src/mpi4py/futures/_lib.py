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
from ._core import BrokenExecutor


# ---


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
            RuntimeWarning, 2,
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


def sys_exception():
    return sys.exc_info()[1]


def os_environ_get(name, default=None):
    varname = f'MPI4PY_FUTURES_{name}'
    if varname not in os.environ:
        oldname = f'MPI4PY_{name}'
        if oldname in os.environ:  # pragma: no cover
            warnings.warn(
                f"environment variable {oldname} is deprecated, use {varname}",
                DeprecationWarning,
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


try:
    threading._register_atexit(join_threads)  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover
    atexit.register(join_threads)


class Pool:

    def __init__(self, executor, manager, *args):
        self.size = None
        self.event = threading.Event()
        self.queue = queue = TaskQueue()
        self.exref = weakref.ref(executor, lambda _, q=queue: q.put(None))

        args = (self, executor._options) + args
        thread = threading.Thread(target=manager, args=args)
        self.thread = thread

        setup_mpi_threads()
        try:
            threading._register_atexit
        except AttributeError:  # pragma: no cover
            thread.daemon = True
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
            future, _ = item
            if handler:
                handler(future)
            else:
                future.cancel()
            del item, future

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
            return True
        except BaseException:
            return False
    return True


def _manager_thread(pool, options):
    size = options.pop('max_workers', 1)
    queue = pool.setup(size)

    def init():
        if not initialize(options):
            pool.broken("initializer failed")
            return False
        return True

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
            if not future.set_running_or_notify_cancel():
                continue
            func, args, kwargs = task
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
            except BaseException:
                exception = sys_exception()
                future.set_exception(exception)
            del item, future

    threads = [threading.Thread(target=worker) for _ in range(size - 1)]
    for thread in threads:
        thread.start()
    worker()
    for thread in threads:
        thread.join()
    queue.pop()


def _manager_comm(pool, options, comm, full=True):
    assert comm != MPI.COMM_NULL  # noqa: S101
    assert comm.Is_inter()        # noqa: S101
    assert comm.Get_size() == 1   # noqa: S101
    serialized(client_sync)(comm, options, full)
    comm = client_comm(comm, options)
    if not client_init(comm, options):
        pool.broken("initializer failed")
        serialized(client_close)(comm)
        return
    size = comm.Get_remote_size()
    queue = pool.setup(size)
    workers = WorkerSet(range(size))
    client_exec(comm, options, 0, workers, queue)
    serialized(client_close)(comm)


def _manager_split(pool, options, comm, root):
    comm = serialized(comm_split)(comm, root)
    _manager_comm(pool, options, comm, full=False)


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


def SplitPool(executor, comm, root):
    # pylint: disable=invalid-name
    return Pool(executor, _manager_split, comm, root)


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
    else:
        return SpawnPool(executor)


# ---

SharedPool = None  # pylint: disable=invalid-name


def _set_shared_pool(obj):
    # pylint: disable=invalid-name
    # pylint: disable=global-statement
    global SharedPool
    SharedPool = obj


def _manager_shared(pool, options, comm, tag, workers):
    if tag == 0:
        comm = MPI.Intercomm(comm)
        serialized(client_sync)(comm, options)
        comm = client_comm(comm, options)
    if tag == 0:
        if not client_init(comm, options):
            pool.broken("initializer failed")
            return
    if tag >= 1:
        if options.get('initializer') is not None:
            pool.broken("cannot run initializer")
            return
    size = comm.Get_remote_size()
    queue = pool.setup(size)
    client_exec(comm, options, tag, workers, queue)


class SharedPoolCtx:

    def __init__(self):
        self.comm = MPI.COMM_NULL
        self.on_root = None
        self.counter = None
        self.workers = None
        self.threads = weakref.WeakKeyDictionary()

    def __call__(self, executor):
        assert SharedPool is self  # noqa: S101
        if self.comm != MPI.COMM_NULL and self.on_root:
            tag = next(self.counter)
            if tag == 0:
                options = executor._options
                self.comm = client_comm(self.comm, options)
            manager = _manager_shared
            args = (self.comm, tag, self.workers)
        else:
            manager, args = _manager_thread, ()
        pool = Pool(executor, manager, *args)
        del THREADS_QUEUES[pool.thread]
        self.threads[pool.thread] = pool.queue
        return pool

    def __enter__(self):
        assert SharedPool is None  # noqa: S101
        self.on_root = MPI.COMM_WORLD.Get_rank() == 0
        if MPI.COMM_WORLD.Get_size() >= 2:
            self.comm = comm_split(MPI.COMM_WORLD, root=0)
            if self.on_root:
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
                    options = dict(main=False)
                    client_sync(comm, options)
                    comm = client_comm(comm, options)
                    client_init(comm, options)
                client_close(comm)
            else:
                options = server_sync(comm)
                comm = server_comm(comm, options)
                server_init(comm)
                server_exec(comm, options)
                server_close(comm)
        if not self.on_root:
            join_threads(self.threads)
        _set_shared_pool(None)
        self.comm = MPI.COMM_NULL
        self.on_root = None
        self.counter = None
        self.workers = None
        self.threads.clear()
        return False


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
        f"unexpected value {repr(value)}",
        RuntimeWarning,
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


def _get_mpi(comm):
    use_pkl5 = isinstance(comm, pkl5.Comm)
    if use_pkl5:
        return pkl5
    return MPI


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
        for pid in range(comm.Get_remote_size()):
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
        size = comm.Get_remote_size()
        _get_mpi(comm).Request.waitall([
            comm.issend(data, pid, tag)
            for pid in range(size)])


def bcast_recv(comm):
    if MPI.VERSION >= 2:
        data = comm.bcast(None, 0)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        data = comm.recv(None, 0, tag)
    return data


# ---


def client_sync(comm, options, full=True):
    barrier(comm)
    _setopt_use_pkl5(options)
    if full:
        options = _sync_get_data(options)
    bcast_send(comm, options)


def client_comm(comm, options):
    return _get_comm(comm, options)


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
    request_free = serialized(_get_mpi(comm).Request.Free)

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

    def send():
        item = task_queue.pop()
        if item is None:
            return True

        try:
            pid = worker_set.pop()
        except LookupError:  # pragma: no cover
            task_queue.add(item)
            return False

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


def client_close(comm):
    _get_mpi(comm).Request.waitall([
        comm.issend(None, dest=pid, tag=0)
        for pid in range(comm.Get_remote_size())])
    try:
        comm.Disconnect()
    except NotImplementedError:  # pragma: no cover
        comm.Free()


def server_sync(comm, full=True):
    barrier(comm)
    options = bcast_recv(comm)
    if full:
        options = _sync_set_data(options)
    return options


def server_comm(comm, options):
    return _get_comm(comm, options)


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
    request_test = _get_mpi(comm).Request.test

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
            return (result, None)
        except BaseException:
            return (None, exception())

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


def server_close(comm):
    try:
        comm.Disconnect()
    except NotImplementedError:  # pragma: no cover
        comm.Free()


# ---


def get_comm_world():
    return MPI.COMM_WORLD


def comm_split(comm, root=0):
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
    intracomm.Free()
    return intercomm


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
            assert self.module.__name__ == run_name  # noqa: S101
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
    data = dict((k, options.pop(k, v)) for k, v in zip(keys, vals))
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


def client_spawn(python_exe=None,
                 python_args=None,
                 max_workers=None,
                 mpi_info=None):
    _check_recursive_spawn()
    if python_exe is None:
        python_exe = sys.executable
    if python_args is None:
        python_args = []
    if max_workers is None:
        max_workers = get_max_workers()
    if mpi_info is None:
        mpi_info = dict(soft=f'1:{max_workers}')

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


def server_accept(service, mpi_info=None,
                  root=0, comm=MPI.COMM_WORLD):
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


def server_main_comm(comm, full=True):
    assert comm != MPI.COMM_NULL        # noqa: S101
    assert comm.Is_inter()              # noqa: S101
    assert comm.Get_remote_size() == 1  # noqa: S101
    options = server_sync(comm, full)
    comm = server_comm(comm, options)
    server_init(comm)
    server_exec(comm, options)
    server_close(comm)


def server_main_split(comm, root):
    comm = comm_split(comm, root)
    server_main_comm(comm, full=False)


def server_main_spawn():
    comm = MPI.Comm.Get_parent()
    server_main_comm(comm)


def server_main_service():
    from getopt import getopt
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
