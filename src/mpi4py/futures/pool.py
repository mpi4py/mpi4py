# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Implements MPIPoolExecutor."""

import sys
import time
import functools
import itertools
import threading

from ._base import Future
from ._base import Executor
from ._base import as_completed

from . import _core


class MPIPoolExecutor(Executor):
    """MPI-based asynchronous executor."""

    Future = Future

    def __init__(self, max_workers=None,
                 initializer=None, initargs=(), **kwargs):
        """Initialize a new MPIPoolExecutor instance.

        Args:
            max_workers: The maximum number of MPI processes that can be used
                to execute the given calls. If ``None`` or not given then the
                number of worker processes will be determined from the MPI
                universe size attribute if defined, otherwise a single worker
                process will be spawned.
            initializer: An callable used to initialize workers processes.
            initargs: A tuple of arguments to pass to the initializer.

        Keyword Args:
            python_exe: Path to Python executable used to spawn workers.
            python_args: Command line arguments to pass to Python executable.
            mpi_info: Mapping or iterable with ``(key, value)`` pairs.
            globals: Mapping with global variables to set in workers.
            main: If ``False``, do not import ``__main__`` in workers.
            path: List of paths to append to ``sys.path`` in workers.
            wdir: Path to set current working directory in workers.
            env: Environment variables to update ``os.environ`` in workers.
            use_pkl5: If ``True``, use pickle5 out-of-band for communication.

        """
        if max_workers is not None:
            max_workers = int(max_workers)
            if max_workers <= 0:
                raise ValueError("max_workers must be greater than 0")
            kwargs['max_workers'] = max_workers
        if initializer is not None:
            if not callable(initializer):
                raise TypeError("initializer must be a callable")
            kwargs['initializer'] = initializer
            kwargs['initargs'] = tuple(initargs)

        self._options = kwargs
        self._shutdown = False
        self._broken = None
        self._lock = threading.Lock()
        self._pool = None

    _make_pool = staticmethod(_core.WorkerPool)

    def _bootstrap(self):
        if self._pool is None:
            self._pool = self._make_pool(self)

    @property
    def _max_workers(self):
        return self.num_workers

    @property
    def num_workers(self):
        """Number or worker processes."""
        with self._lock:
            if self._broken:
                return 0
            if self._shutdown:
                return 0
            self._bootstrap()
            self._pool.wait()
            return self._pool.size

    def bootup(self, wait=True):
        """Allocate executor resources eagerly.

        Args:
            wait: If ``True`` then bootup will not return until the
                executor resources are ready to process submissions.

        """
        with self._lock:
            if self._shutdown:
                raise RuntimeError("cannot bootup after shutdown")
            self._bootstrap()
            if wait:
                self._pool.wait()
            return self

    def submit(self, fn, *args, **kwargs):
        """Submit a callable to be executed with the given arguments.

        Schedule the callable to be executed as ``fn(*args, **kwargs)`` and
        return a `Future` instance representing the execution of the callable.

        Returns:
            A `Future` representing the given call.

        """
        # pylint: disable=arguments-differ
        with self._lock:
            if self._broken:
                raise _core.BrokenExecutor(self._broken)
            if self._shutdown:
                raise RuntimeError("cannot submit after shutdown")
            self._bootstrap()
            future = self.Future()
            task = (fn, args, kwargs)
            self._pool.push((future, task))
            return future
    if sys.version_info >= (3, 8):  # pragma: no branch
        submit.__text_signature__ = '($self, fn, /, *args, **kwargs)'

    def map(self, fn, *iterables,
            timeout=None, chunksize=1, unordered=False):
        """Return an iterator equivalent to ``map(fn, *iterables)``.

        Args:
            fn: A callable that will take as many arguments as there are
                passed iterables.
            iterables: Iterables yielding positional arguments to be passed to
                the callable.
            timeout: The maximum number of seconds to wait. If ``None``, then
                there is no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being passed to a worker process.
            unordered: If ``True``, yield results out-of-order, as completed.

        Returns:
            An iterator equivalent to built-in ``map(func, *iterables)``
            but the calls may be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If ``fn(*args)`` raises for any values.

        """  # noqa: D402
        return self.starmap(fn, zip(*iterables), timeout, chunksize, unordered)

    def starmap(self, fn, iterable,
                timeout=None, chunksize=1, unordered=False):
        """Return an iterator equivalent to ``itertools.starmap(...)``.

        Args:
            fn: A callable that will take positional argument from iterable.
            iterable: An iterable yielding ``args`` tuples to be used as
                positional arguments to call ``fn(*args)``.
            timeout: The maximum number of seconds to wait. If ``None``, then
                there is no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being passed to a worker process.
            unordered: If ``True``, yield results out-of-order, as completed.

        Returns:
            An iterator equivalent to ``itertools.starmap(fn, iterable)``
            but the calls may be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If ``fn(*args)`` raises for any values.

        """  # noqa: D402
        # pylint: disable=too-many-arguments
        if chunksize < 1:
            raise ValueError("chunksize must be >= 1.")
        if chunksize == 1:
            return _starmap_helper(self.submit, fn, iterable,
                                   timeout, unordered)
        else:
            return _starmap_chunks(self.submit, fn, iterable,
                                   timeout, unordered, chunksize)

    def shutdown(self, wait=True, *, cancel_futures=False):
        """Clean-up the resources associated with the executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If ``True`` then shutdown will not return until all running
                futures have finished executing and the resources used by the
                executor have been reclaimed.
            cancel_futures: If ``True`` then shutdown will cancel all pending
                futures. Futures that are completed or running will not be
                cancelled.

        """
        with self._lock:
            if not self._shutdown:
                self._shutdown = True
                if self._pool is not None:
                    self._pool.done()
            if cancel_futures:
                if self._pool is not None:
                    self._pool.cancel()
            pool = None
            if wait:
                pool = self._pool
                self._pool = None
        if pool is not None:
            pool.join()


def _starmap_helper(submit, function, iterable, timeout, unordered):
    if timeout is not None:
        timer = getattr(time, 'monotonic', time.time)
        end_time = timeout + timer()

    futures = [submit(function, *args) for args in iterable]
    if unordered:
        futures = set(futures)

    def result(future, timeout=None):
        try:
            try:
                return future.result(timeout)
            finally:
                future.cancel()
        finally:
            del future

    def result_iterator():
        try:
            if unordered:
                if timeout is None:
                    iterator = as_completed(futures)
                else:
                    iterator = as_completed(futures, end_time - timer())
                for future in iterator:
                    futures.remove(future)
                    future = [future]
                    yield result(future.pop())
            else:
                futures.reverse()
                if timeout is None:
                    while futures:
                        yield result(futures.pop())
                else:
                    while futures:
                        yield result(futures.pop(), end_time - timer())
        finally:
            while futures:
                futures.pop().cancel()
    return result_iterator()


def _apply_chunks(function, chunk):
    return [function(*args) for args in chunk]


def _build_chunks(chunksize, iterable):
    iterable = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(iterable, chunksize))
        if not chunk:
            return
        yield (chunk,)


def _chain_from_iterable_of_lists(iterable):
    for item in iterable:
        item.reverse()
        while item:
            yield item.pop()


def _starmap_chunks(submit, function, iterable,
                    timeout, unordered, chunksize):
    # pylint: disable=too-many-arguments
    function = functools.partial(_apply_chunks, function)
    iterable = _build_chunks(chunksize, iterable)
    result = _starmap_helper(submit, function, iterable,
                             timeout, unordered)
    return _chain_from_iterable_of_lists(result)


class MPICommExecutor:
    """Context manager for `MPIPoolExecutor`.

    This context manager splits a MPI (intra)communicator in two
    disjoint sets: a single master process and the remaining worker
    processes. These sets are then connected through an intercommunicator.
    The target of the ``with`` statement is assigned either an
    `MPIPoolExecutor` instance (at the master) or ``None`` (at the workers).

    Example::

        with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
            if executor is not None: # master process
                executor.submit(...)
                executor.map(...)
    """

    def __init__(self, comm=None, root=0, **kwargs):
        """Initialize a new MPICommExecutor instance.

        Args:
            comm: MPI (intra)communicator.
            root: Designated master process.

        Raises:
            ValueError: If the communicator has wrong kind or
               the root value is not in the expected range.

        """
        if comm is None:
            comm = _core.MPI.COMM_WORLD
        if comm.Is_inter():
            raise ValueError("expecting an intracommunicator")
        if root < 0 or root >= comm.Get_size():
            raise ValueError("expecting root in range(comm.size)")
        if _core.SharedPool is not None:
            comm = _core.MPI.COMM_WORLD
            root = comm.Get_rank()

        self._comm = comm
        self._root = root
        self._options = kwargs
        self._executor = None

    def __enter__(self):
        """Return `MPIPoolExecutor` instance at the root."""
        if self._executor is not None:
            raise RuntimeError("__enter__")

        comm = self._comm
        root = self._root
        options = self._options
        executor = None

        if comm.Get_rank() == root:
            executor = MPIPoolExecutor(**options)
        _core._comm_executor_helper(executor, comm, root)

        self._executor = executor
        return executor

    def __exit__(self, *args):
        """Shutdown `MPIPoolExecutor` instance at the root."""
        executor = self._executor
        self._executor = None

        if executor is not None:
            executor.shutdown(wait=True)
            return False
        else:
            return True


class ThreadPoolExecutor(MPIPoolExecutor):
    """`MPIPoolExecutor` subclass using a pool of threads."""

    _make_pool = staticmethod(_core.ThreadPool)


class ProcessPoolExecutor(MPIPoolExecutor):
    """`MPIPoolExecutor` subclass using a pool of processes."""

    _make_pool = staticmethod(_core.SpawnPool)


def get_comm_workers():
    """Access an intracommunicator grouping MPI worker processes."""
    return _core.get_comm_server()
