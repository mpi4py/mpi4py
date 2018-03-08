# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Management of MPI worker processes."""
# pylint: disable=missing-docstring

import os
import sys
import time
import atexit
import weakref
import warnings
import itertools
import threading
import collections

from .. import MPI


# ---


def serialized(function):
    if serialized.lock is None:
        return function
    def wrapper(*args, **kwargs):
        with serialized.lock:
            return function(*args, **kwargs)
    return wrapper
serialized.lock = None


def setup_mpi_threads():
    with setup_mpi_threads.lock:
        thread_level = setup_mpi_threads.thread_level
        if thread_level is None:
            thread_level = MPI.Query_thread()
            setup_mpi_threads.thread_level = thread_level
            if thread_level < MPI.THREAD_MULTIPLE:  # pragma: no cover
                serialized.lock = threading.Lock()
    if thread_level < MPI.THREAD_SERIALIZED:  # pragma: no cover
        warnings.warn("The level of thread support in MPI "
                      "should be at least MPI_THREAD_SERIALIZED",
                      RuntimeWarning, 2)
setup_mpi_threads.lock = threading.Lock()
setup_mpi_threads.thread_level = None


# ---


if sys.version_info[0] == 2:     # pragma: no cover
    def sys_exception():
        exc = sys.exc_info()[1]
        return exc
else:                            # pragma: no cover
    def sys_exception():
        exc = sys.exc_info()[1]
        exc.__traceback__ = None
        return exc


# ---


BACKOFF = 0.001


class Backoff(object):

    def __init__(self, seconds=BACKOFF):
        self.tval = 0.0
        self.tmax = max(float(seconds), 0.0)
        self.tmin = self.tmax / (1 << 10)

    def reset(self):
        self.tval = 0.0

    def sleep(self):
        time.sleep(self.tval)
        self.tval = min(self.tmax, max(self.tmin, self.tval * 2))


class Queue(collections.deque):
    put = collections.deque.append
    pop = collections.deque.popleft
    add = collections.deque.appendleft


class Stack(collections.deque):
    put = collections.deque.append
    pop = collections.deque.pop


THREADS_QUEUES = weakref.WeakKeyDictionary()


def join_threads(threads_queues=THREADS_QUEUES):
    items = list(threads_queues.items())
    for _, queue in items:   # pragma: no cover
        queue.put(None)
    for thread, _ in items:  # pragma: no cover
        thread.join()


atexit.register(join_threads)


class Pool(object):

    def __init__(self, executor, manager, *args):
        self.size = None
        self.event = threading.Event()
        self.queue = queue = Queue()
        self.exref = weakref.ref(executor, lambda _, q=queue: q.put(None))

        args = (self,) + args
        kwargs = executor._options  # pylint: disable=protected-access
        thread = threading.Thread(target=manager, args=args, kwargs=kwargs)
        thread.daemon = True
        self.thread = thread

        setup_mpi_threads()
        thread.start()
        THREADS_QUEUES[thread] = queue

    def wait(self):
        self.event.wait()

    def push(self, task):
        self.queue.put(task)

    def done(self):
        self.queue.put(None)

    def join(self):
        self.thread.join()


def setup_pool(pool, num_workers):
    pool.size = num_workers
    pool.event.set()
    return pool.queue


def _manager_thread(pool, **options):
    size = options.pop('max_workers', 1)
    queue = setup_pool(pool, size)

    def worker():
        backoff = Backoff(options.get('backoff', BACKOFF))
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


def _manager_comm(pool, comm, **options):
    size = comm.Get_remote_size()
    workers = Stack(reversed(range(size)))
    queue = setup_pool(pool, size)
    client(comm, 0, workers, queue, **options)


def _manager_spawn(pool, **options):
    pyexe = options.pop('python_exe', None)
    pyargs = options.pop('python_args', None)
    nprocs = options.pop('max_workers', None)
    info = options.pop('mpi_info', None)
    comm = serialized(client_spawn)(pyexe, pyargs, nprocs, info)
    serialized(client_sync)(comm, options)
    _manager_comm(pool, comm, **options)
    serialized(client_close)(comm)


def _manager_service(pool, **options):
    service = options.pop('service', None)
    info = options.pop('mpi_info', None)
    comm = serialized(client_connect)(service, info)
    serialized(client_sync)(comm, options)
    _manager_comm(pool, comm, **options)
    serialized(client_close)(comm)


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
    # pylint: disable=protected-access
    if SharedPool is not None:
        return SharedPool(executor)
    if 'service' in executor._options:
        return ServicePool(executor)
    else:
        return SpawnPool(executor)


# ---


def get_comm_world():
    return MPI.COMM_WORLD


def comm_split(comm, root=0):
    assert not comm.Is_inter()
    assert comm.Get_size() > 1
    assert 0 <= root < comm.Get_size()
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


def _manager_split(pool, comm, root, **options):
    comm = serialized(comm_split)(comm, root)
    _manager_comm(pool, comm, **options)
    serialized(client_close)(comm)


def SplitPool(executor, comm, root):
    # pylint: disable=invalid-name
    return Pool(executor, _manager_split, comm, root)


def server_main_split(comm, root, **options):
    comm = comm_split(comm, root)
    server(comm, **options)
    server_close(comm)


# ---

SharedPool = None  # pylint: disable=invalid-name


def _set_shared_pool(obj):
    # pylint: disable=invalid-name
    # pylint: disable=global-statement
    global SharedPool
    SharedPool = obj


def _manager_shared(pool, comm, tag, workers, **options):
    # pylint: disable=too-many-arguments
    if tag == 0:
        serialized(client_sync)(comm, options)
    size = comm.Get_remote_size()
    queue = setup_pool(pool, size)
    client(comm, tag, workers, queue, **options)


class SharedPoolCtx(object):
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.comm = MPI.COMM_NULL
        self.on_root = None
        self.counter = None
        self.workers = None
        self.threads = weakref.WeakKeyDictionary()

    def __call__(self, executor):
        assert SharedPool is self
        if self.comm != MPI.COMM_NULL and self.on_root:
            tag = next(self.counter)
            args = (self.comm, tag, self.workers)
            pool = Pool(executor, _manager_shared, *args)
        else:
            pool = Pool(executor, _manager_thread)
        del THREADS_QUEUES[pool.thread]
        self.threads[pool.thread] = pool.queue
        return pool

    def __enter__(self):
        assert SharedPool is None
        self.on_root = MPI.COMM_WORLD.Get_rank() == 0
        if MPI.COMM_WORLD.Get_size() >= 2:
            self.comm = comm_split(MPI.COMM_WORLD, root=0)
            if self.on_root:
                size = self.comm.Get_remote_size()
                self.counter = itertools.count(0)
                self.workers = Stack(reversed(range(size)))
        _set_shared_pool(self)
        return self if self.on_root else None

    def __exit__(self, *args):
        assert SharedPool is self
        if self.on_root:
            join_threads(self.threads)
        if self.comm != MPI.COMM_NULL:
            if self.on_root:
                if next(self.counter) == 0:
                    client_sync(self.comm, dict(main=False))
                client_close(self.comm)
            else:
                options = server_sync(self.comm)
                server(self.comm, **options)
                server_close(self.comm)
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


def barrier(comm):
    assert comm.Is_inter()
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


def client_sync(comm, options):
    assert comm.Is_inter()
    assert comm.Get_size() == 1
    barrier(comm)
    data = _sync_get_data(options)
    if MPI.VERSION >= 2:
        comm.bcast(data, MPI.ROOT)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        size = comm.Get_remote_size()
        MPI.Request.Waitall([
            comm.issend(data, pid, tag)
            for pid in range(size)])


def client(comm, tag, worker_pool, task_queue, **options):
    # pylint: disable=too-many-locals
    assert comm.Is_inter()
    assert comm.Get_size() == 1
    assert tag >= 0

    backoff = Backoff(options.get('backoff', BACKOFF))

    status = MPI.Status()
    comm_recv = serialized(comm.recv)
    comm_isend = serialized(comm.issend)
    comm_iprobe = serialized(comm.iprobe)
    request_free = serialized(MPI.Request.Free)

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
        worker_pool.put(pid)

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
            pid = worker_pool.pop()
        except LookupError:  # pragma: no cover
            task_queue.add(item)
            return False

        future, task = item
        if not future.set_running_or_notify_cancel():
            worker_pool.put(pid)
            return False

        try:
            request = comm_isend(task, pid, tag)
            pending[pid] = (future, request)
        except BaseException:
            worker_pool.put(pid)
            future.set_exception(sys_exception())
        return None

    while True:
        if task_queue and worker_pool:
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
    assert comm.Is_inter()
    MPI.Request.Waitall([
        comm.issend(None, dest=pid, tag=0)
        for pid in range(comm.Get_remote_size())])
    try:
        comm.Disconnect()
    except NotImplementedError:  # pragma: no cover
        comm.Free()


def server_sync(comm):
    assert comm.Is_inter()
    assert comm.Get_remote_size() == 1
    barrier(comm)
    if MPI.VERSION >= 2:
        data = comm.bcast(None, 0)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        data = comm.recv(None, 0, tag)
    options = _sync_set_data(data)
    return options


def server(comm, **options):
    assert comm.Is_inter()
    assert comm.Get_remote_size() == 1

    backoff = Backoff(options.get('backoff', BACKOFF))

    status = MPI.Status()
    comm_recv = comm.recv
    comm_isend = comm.issend
    comm_iprobe = comm.iprobe
    request_test = MPI.Request.Test

    def recv():
        pid, tag = MPI.ANY_SOURCE, MPI.ANY_TAG
        backoff.reset()
        while not comm_iprobe(pid, tag, status):
            backoff.sleep()
        pid, tag = status.source, status.tag
        try:
            task = comm_recv(None, pid, tag, status)
        except BaseException:
            task = sys_exception()
        return task

    def call(task):
        if isinstance(task, BaseException):
            return (None, task)
        func, args, kwargs = task
        try:
            result = func(*args, **kwargs)
            return (result, None)
        except BaseException:
            return (None, sys_exception())

    def send(task):
        pid, tag = status.source, status.tag
        try:
            request = comm_isend(task, pid, tag)
        except BaseException:
            task = (None, sys_exception())
            request = comm_isend(task, pid, tag)
        backoff.reset()
        while not request_test(request):
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


def import_main(mod_name, mod_path, init_globals, run_name):
    # pylint: disable=protected-access
    import types
    import runpy

    module = types.ModuleType(run_name)
    if init_globals is not None:
        module.__dict__.update(init_globals)
        module.__name__ = run_name

    class TempModulePatch(runpy._TempModule):
        # pylint: disable=too-few-public-methods
        def __init__(self, mod_name):
            # pylint: disable=no-member
            super(TempModulePatch, self).__init__(mod_name)
            assert self.module.__name__ == run_name
            self.module = module

    TempModule = runpy._TempModule  # pylint: disable=invalid-name
    runpy._TempModule = TempModulePatch
    import_main.sentinel = (mod_name, mod_path)
    try:
        main_module = sys.modules['__main__']
        sys.modules['__main__'] = sys.modules[run_name] = module
        if mod_name:  # pragma: no cover
            runpy.run_module(mod_name, run_name=run_name, alter_sys=True)
        elif mod_path:  # pragma: no branch
            runpy.run_path(mod_path, run_name=run_name)
        sys.modules['__main__'] = sys.modules[run_name] = module
    except:  # pragma: no cover
        sys.modules['__main__'] = main_module
        raise
    finally:
        del import_main.sentinel
        runpy._TempModule = TempModule


MAIN_RUN_NAME = '__worker__'


def _sync_get_data(options):
    main = sys.modules['__main__']
    sys.modules.setdefault(MAIN_RUN_NAME, main)
    import_main_module = options.pop('main', True)

    data = options.copy()
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


# ---


def check_recursive_spawn():  # pragma: no cover
    if not hasattr(import_main, 'sentinel'):
        return
    main_name, main_path = import_main.sentinel
    main_info = "\n"
    if main_name is not None:
        main_info += "    main name: '{}'\n".format(main_name)
    if main_path is not None:
        main_info += "    main path: '{}'\n".format(main_path)
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
    # Python 3
    'inspect': 'i',
    'interactive': 'i',
    'debug': 'd',
    'optimize': 'O',
    'no_user_site': 's',
    'no_site': 'S',
    'isolated': 'I',
    'ignore_environment': 'E',
    'dont_write_bytecode': 'B',
    'hash_randomization': 'R',
    'verbose': 'v',
    'quiet': 'q',
    'bytes_warning': 'b',
    # Python 2
    'division_warning': 'Qwarn',
    'division_new': 'Qnew',
    'py3k_warning': '3',
    'tabcheck': 't',
    'unicode': 'U',
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
    if 'MPI4PY_MAX_WORKERS' in os.environ:
        return int(os.environ['MPI4PY_MAX_WORKERS'])
    if MPI.UNIVERSE_SIZE != MPI.KEYVAL_INVALID:  # pragma: no branch
        universe_size = MPI.COMM_WORLD.Get_attr(MPI.UNIVERSE_SIZE)
        if universe_size is not None:  # pragma: no cover
            world_size = MPI.COMM_WORLD.Get_size()
            return max(universe_size - world_size, 1)
    return 1


def client_spawn(python_exe=None,
                 python_args=None,
                 max_workers=None,
                 mpi_info=None):
    check_recursive_spawn()
    if python_exe is None:
        python_exe = sys.executable
    if python_args is None:
        python_args = []
    if max_workers is None:
        max_workers = get_max_workers()
    if mpi_info is None:
        mpi_info = dict(soft='1:{}'.format(max_workers))

    args = get_python_flags() + list(python_args)
    args.extend(['-m', __package__ + '.server'])
    info = MPI.Info.Create()
    info.update(mpi_info)
    comm = MPI.COMM_SELF.Spawn(python_exe, args, max_workers, info)
    info.Free()
    return comm


# ---


SERVICE = __package__
SERVER_HOST = 'localhost'
SERVER_BIND = ''
SERVER_PORT = 31415


def get_service():
    return os.environ.get('MPI4PY_SERVICE', SERVICE)


def get_server_host():
    return os.environ.get('MPI4PY_SERVER_HOST', SERVER_HOST)


def get_server_bind():
    return os.environ.get('MPI4PY_SERVER_BIND', SERVER_BIND)


def get_server_port():
    return int(os.environ.get('MPI4PY_SERVER_PORT', SERVER_PORT))


def client_lookup(address):
    from socket import socket
    host, port = address
    host = host or get_server_host()
    port = port or get_server_port()
    address = (host, int(port))
    sock = socket()
    sock.connect(address)
    try:
        fdes = sock.fileno()  # pylint: disable=no-member
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
        fdes = sock.fileno()  # pylint: disable=no-member
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
    assert not comm.Is_inter()
    assert 0 <= root < comm.Get_size()

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


def server_main_comm(comm):
    assert comm != MPI.COMM_NULL
    options = server_sync(comm)
    server(comm, **options)
    server_close(comm)


def server_main_spawn():
    comm = MPI.Comm.Get_parent()
    server_main_comm(comm)


def server_main_accept():
    from getopt import getopt
    longopts = ['bind=', 'port=', 'service=', 'info=']
    optlist, _ = getopt(sys.argv[1:], '', longopts)
    options = {opt[2:]: val for opt, val in optlist}

    if 'bind' in options or 'port' in options:
        bind = options.get('bind') or get_server_bind()
        port = options.get('port') or get_server_port()
        service = (bind, int(port))
    else:
        service = options.get('service') or get_service()
    info = options.get('info', '').split(',')
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
            server_main_accept()
    except:
        set_abort_status(1)
        raise


# ---
