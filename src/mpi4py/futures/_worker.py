# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Management of MPI worker processes."""
# pylint: disable=missing-docstring

import os
import sys
import time
import atexit
import weakref
import itertools
import threading
import collections

from .. import MPI


# ---


class Queue(collections.deque):
    put = collections.deque.append
    pop = collections.deque.popleft


class Stack(collections.deque):
    put = collections.deque.append
    pop = collections.deque.pop


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


def serialized(function):
    if serialized.lock is None:
        return function
    def wrapper(*args, **kwargs):
        with serialized.lock:
            return function(*args, **kwargs)
    return wrapper
serialized.lock = None


def setup_mpi_threads():
    thread_level = setup_mpi_threads.thread_level
    if thread_level is None:
        thread_level = MPI.Query_thread()
        setup_mpi_threads.thread_level = thread_level
        if thread_level < MPI.THREAD_MULTIPLE:  # pragma: no cover
            serialized.lock = threading.Lock()
    if thread_level < MPI.THREAD_SERIALIZED:  # pragma: no cover
        from _warnings import warn
        warn("The level of thread support in MPI "
             "should be at least MPI_THREAD_SERIALIZED",
             RuntimeWarning, 2)
setup_mpi_threads.thread_level = None


# ---


def _set_num_workers(executor_ref, event, num_workers):
    # pylint: disable=protected-access
    executor = executor_ref()
    if executor is not None:
        executor._num_workers = num_workers
    del executor
    event.set()


def _manager_thread(executor_ref, event, queue, **options):
    size = options.pop('max_workers', 1)
    _set_num_workers(executor_ref, event, size)

    sleep = time.sleep
    throttle = options.get('throttle', 100e-6)
    assert throttle >= 0

    def worker():
        while True:
            try:
                task = queue.pop()
            except LookupError:
                sleep(throttle)
                continue
            if task is None:
                queue.put(None)
                break
            future, work = task
            if not future.set_running_or_notify_cancel():
                continue
            func, args, kwargs = work
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
            except BaseException:
                exception = sys_exception()
                future.set_exception(exception)

    threads = [threading.Thread(target=worker)
               for _ in range(size - 1)]
    for thread in threads:
        thread.start()
    worker()
    for thread in threads:
        thread.join()
    queue.pop()


def _manager_comm(executor_ref, event, queue, comm, **options):
    size = comm.Get_remote_size()
    pool = Stack(reversed(range(size)))
    _set_num_workers(executor_ref, event, size)
    client(comm, 0, pool, queue, **options)
    serialized(client_close)(comm)


def _manager_spawn(executor_ref, event, queue, **options):
    comm, options = serialized(client_spawn)(**options)
    size = comm.Get_remote_size()
    pool = Stack(reversed(range(size)))
    _set_num_workers(executor_ref, event, size)
    client(comm, 0, pool, queue, **options)
    serialized(client_close)(comm)


THREADS_QUEUES = weakref.WeakKeyDictionary()


def join_threads(threads_queues=THREADS_QUEUES):
    items = list(threads_queues.items())
    for _, queue in items:   # pragma: no cover
        queue.put(None)
    for thread, _ in items:  # pragma: no cover
        thread.join()


atexit.register(join_threads)


class Pool(object):

    def __init__(self, manager_target, executor, *args, **options):
        event, queue = threading.Event(), Queue()
        executor_ref = weakref.ref(executor, lambda _, q=queue: q.put(None))

        setup_mpi_threads()
        thread = threading.Thread(target=manager_target,
                                  args=(executor_ref, event, queue) + args,
                                  kwargs=options)
        thread.daemon = True
        thread.start()
        THREADS_QUEUES[thread] = queue

        self.thread = thread
        self.event = event
        self.queue = queue

    def wait(self):
        self.event.wait()

    def push(self, task):
        self.queue.put(task)

    def done(self):
        self.queue.put(None)

    def join(self):
        self.thread.join()


def ThreadPool(executor, **options):
    # pylint: disable=invalid-name
    return Pool(_manager_thread, executor, **options)


def CommPool(executor, comm, **options):
    # pylint: disable=invalid-name
    return Pool(_manager_comm, executor, comm, **options)


def SpawnPool(executor, **options):
    # pylint: disable=invalid-name
    return Pool(_manager_spawn, executor, **options)


WorkerPool = SpawnPool  # pylint: disable=invalid-name


# ---


SharedPool = None  # pylint: disable=invalid-name


def _set_shared_pool(obj):
    # pylint: disable=invalid-name
    # pylint: disable=global-statement
    global WorkerPool
    global SharedPool
    if obj is not None:
        WorkerPool = obj
        SharedPool = obj
    else:
        WorkerPool = SpawnPool
        SharedPool = None


def _manager_shared(executor_ref, event, queue,
                    comm, tag, pool, **options):
    # pylint: disable=too-many-arguments
    if tag == 0:
        options = serialized(client_sync)(comm, options)
    size = comm.Get_remote_size()
    _set_num_workers(executor_ref, event, size)
    client(comm, tag, pool, queue, **options)


class SharedPoolCtx(object):
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.comm = MPI.COMM_NULL
        self.on_root = None
        self.counter = None
        self.workers = None
        self.threads = weakref.WeakKeyDictionary()

    def __call__(self, executor, **options):
        assert SharedPool is self
        tag = next(self.counter)
        if self.comm != MPI.COMM_NULL and self.on_root:
            args = (self.comm, tag, self.workers)
            pool = Pool(_manager_shared, executor, *args, **options)
        else:
            pool = Pool(_manager_thread, executor, **options)
        del THREADS_QUEUES[pool.thread]
        self.threads[pool.thread] = pool.queue
        return pool

    def __enter__(self):
        assert SharedPool is None
        self.on_root = MPI.COMM_WORLD.Get_rank() == 0
        self.counter = itertools.count(0)
        if MPI.COMM_WORLD.Get_size() >= 2:
            self.comm = split(MPI.COMM_WORLD, root=0)
            if self.on_root:
                size = self.comm.Get_remote_size()
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
    sleep = time.sleep
    throttle = 100e-6
    try:
        request = comm.Ibarrier()
        while not request.Test():
            sleep(throttle)
    except NotImplementedError:  # pragma: no cover
        buf = [None, 0, MPI.BYTE]
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        sendreqs, recvreqs = [], []
        for pid in range(comm.Get_remote_size()):
            recvreqs.append(comm.Irecv(buf, pid, tag))
            sendreqs.append(comm.Issend(buf, pid, tag))
        while not MPI.Request.Testall(recvreqs):
            sleep(throttle)
        MPI.Request.Waitall(sendreqs)


def client_sync(comm, options):
    assert comm.Is_inter()
    assert comm.Get_size() == 1
    barrier(comm)
    data = _sync_get_data(options)
    if MPI.ROOT != MPI.PROC_NULL:
        comm.bcast(data, MPI.ROOT)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        size = comm.Get_remote_size()
        MPI.Request.Waitall([
            comm.issend(data, pid, tag)
            for pid in range(size)])
    return options


def client(comm, tag, worker_pool, task_queue, **options):
    # pylint: disable=too-many-locals
    assert comm.Is_inter()
    assert comm.Get_size() == 1
    assert tag >= 0

    status = MPI.Status()
    comm_recv = serialized(comm.recv)
    comm_isend = serialized(comm.issend)
    comm_iprobe = serialized(comm.iprobe)
    request_free = serialized(MPI.Request.Free)

    sleep = time.sleep
    throttle = options.get('throttle', 100e-6)
    assert throttle >= 0

    pending = {}

    def iprobe():
        pid = MPI.ANY_SOURCE
        return comm_iprobe(pid, tag, status)

    def probe():
        pid = MPI.ANY_SOURCE
        while not comm_iprobe(pid, tag, status):
            sleep(throttle)

    def recv():
        pid = status.source
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
        try:
            pid = worker_pool.pop()
        except IndexError:  # pragma: no cover
            return None

        task = task_queue.pop()
        if task is None:
            worker_pool.put(pid)
            return True

        future, work = task
        if not future.set_running_or_notify_cancel():
            worker_pool.put(pid)
            return None

        try:
            request = comm_isend(work, pid, tag)
            pending[pid] = (future, request)
        except BaseException:
            worker_pool.put(pid)
            future.set_exception(sys_exception())

    while True:
        idle = True
        if worker_pool and task_queue:
            idle = False
            stop = send()
            if stop:
                break
        if pending and iprobe():
            idle = False
            recv()
        if idle:
            sleep(throttle)
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
    if MPI.ROOT != MPI.PROC_NULL:
        data = comm.bcast(None, 0)
    else:  # pragma: no cover
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)
        data = comm.recv(None, 0, tag)
    options = _sync_set_data(data)
    return options


def server(comm, **options):
    assert comm.Is_inter()
    assert comm.Get_remote_size() == 1

    status = MPI.Status()
    comm_recv = comm.recv
    comm_isend = comm.issend
    comm_iprobe = comm.iprobe
    request_test = MPI.Request.Test

    sleep = time.sleep
    throttle = options.get('throttle', 100e-6)
    assert throttle >= 0

    def recv():
        pid, tag = MPI.ANY_SOURCE, MPI.ANY_TAG
        while not comm_iprobe(pid, tag, status):
            sleep(throttle)
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
        while not request_test(request):
            sleep(throttle)

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


def get_world():
    return MPI.COMM_WORLD


def split(comm, root=0):
    assert not comm.Is_inter()
    assert comm.Get_size() > 1
    assert 0 <= root < comm.Get_size()
    rank = comm.Get_rank()

    mpi22 = MPI.Get_version() >= (2, 2)
    if mpi22:  # pragma: no branch
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
    import_main.info = (mod_name, mod_path)
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
        del import_main.info
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


def _sys_flags():
    flag_opt_map = {
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
    args = []
    for flag, opt in flag_opt_map.items():
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


# ---


def client_spawn_abort(main_name, main_path):  # pragma: no cover
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


def client_spawn_max_workers():
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
                 mpi_info=None,
                 **options):
    if hasattr(import_main, 'info'):  # pragma: no cover
        client_spawn_abort(*import_main.info)
    if python_exe is None:
        python_exe = sys.executable
    if python_args is None:
        python_args = []
    if max_workers is None:
        max_workers = client_spawn_max_workers()
    if mpi_info is None:
        mpi_info = dict(soft='1:{}'.format(max_workers))

    args = _sys_flags() + list(python_args)
    args.extend(['-m', __package__ + '._spawn'])
    info = MPI.Info.Create()
    info.update(mpi_info)
    comm = MPI.COMM_SELF.Spawn(python_exe, args, max_workers, info)
    info.Free()
    options = client_sync(comm, options)
    return comm, options


def server_spawn():
    comm = MPI.Comm.Get_parent()
    assert comm != MPI.COMM_NULL
    options = server_sync(comm)
    server(comm, **options)
    server_close(comm)


# ---


def client_connect(service=__package__, **options):  # pragma: no cover
    port = MPI.Lookup_name(service)
    info = MPI.INFO_NULL
    comm = MPI.COMM_SELF.Connect(port, info, root=0)
    options = client_sync(comm, options)
    return comm, options


def server_connect(service=__package__):  # pragma: no cover
    port = None
    if MPI.COMM_WORLD.Get_rank() == 0:
        port = MPI.Open_port()
        MPI.Publish_name(service, port)
    info = MPI.INFO_NULL
    comm = MPI.COMM_WORLD.Accept(port, info, root=0)
    if MPI.COMM_WORLD.Get_rank() == 0:
        MPI.Unpublish_name(service, port)
        MPI.Close_port(port)
    options = server_sync(comm)
    server(comm, **options)
    server_close(comm)


# ---
