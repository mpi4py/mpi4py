# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Implements MPIPoolExecutor."""

import time
import functools
import itertools
import threading

from . import Future
from . import Executor
from . import as_completed

from . import _worker


class MPIPoolExecutor(Executor):
    """MPI-based asynchronous executor."""

    def __init__(self, max_workers=None, **kwargs):
        """Initialize a new MPIPoolExecutor instance.

        Args:
            max_workers: The maximum number of MPI processes that can be used
                to execute the given calls. If ``None`` or not given then the
                number of worker processes will be determined from the MPI
                universe size attribute if defined, otherwise a single worker
                process will be spawned.

        Keyword Args:
            python_exe: Path to Python executable used to spawn workers.
            python_args: Command line arguments to pass to Python executable.
            mpi_info: Dict or iterable with ``(key, value)`` pairs.
            main: If ``False``, do not import ``__main__`` in workers.
            path: List of paths to append to ``sys.path`` in workers.
            wdir: Path to set current working directory in workers.
            env: Environment variables to update ``os.environ`` in workers.
        """
        if max_workers is not None:
            max_workers = int(max_workers)
            if max_workers <= 0:
                raise ValueError("max_workers must be greater than 0")
            kwargs['max_workers'] = max_workers

        self._options = kwargs
        self._num_workers = None
        self._shutdown = False
        self._lock = threading.Lock()
        self._pool = None

    def _bootstrap(self):
        if self._pool is None:
            self._pool = _worker.WorkerPool(self, **self._options)

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
        with self._lock:
            if self._shutdown:
                raise RuntimeError("cannot submit after shutdown")
            self._bootstrap()
            future = Future()
            work = (fn, args, kwargs)
            self._pool.push((future, work))
            return future

    def map(self, fn, *iterables, **kwargs):
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

        Keyword Args:
            unordered: If ``True``, yield results out-of-order, as completed.

        Returns:
            An iterator equivalent to built-in ``map(func, *iterables)``
            but the calls may be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If ``fn(*args)`` raises for any values.
        """
        iterable = getattr(itertools, 'izip', zip)(*iterables)
        return self.starmap(fn, iterable, **kwargs)

    def starmap(self, fn, iterable, timeout=None, chunksize=1, **kwargs):
        """Return an iterator equivalent to ``itertools.starmap(...)``.

        Args:
            fn: A callable that will take positional argument from iterable.
            iterable: An iterable yielding ``args`` tuples to be used as
                positional arguments to call ``fn(*args)``.
            timeout: The maximum number of seconds to wait. If ``None``, then
                there is no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being passed to a worker process.

        Keyword Args:
            unordered: If ``True``, yield results out-of-order, as completed.

        Returns:
            An iterator equivalent to ``itertools.starmap(fn, iterable)``
            but the calls may be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If ``fn(*args)`` raises for any values.

        """
        unordered = kwargs.pop('unordered', False)
        if chunksize < 1:
            raise ValueError("chunksize must be >= 1.")
        if chunksize == 1:
            return _starmap_helper(self.submit, fn, iterable,
                                   timeout, unordered)
        else:
            return _starmap_chunks(self.submit, fn, iterable,
                                   timeout, chunksize, unordered)

    def shutdown(self, wait=True):
        """Clean-up the resources associated with the executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If ``True`` then shutdown will not return until all running
                futures have finished executing and the resources used by the
                executor have been reclaimed.

        """
        with self._lock:
            if not self._shutdown:
                self._shutdown = True
                if self._pool is not None:
                    self._pool.done()
        if wait:
            if self._pool is not None:
                self._pool.join()
                self._pool = None


def _starmap_helper(submit, function, iterable, timeout, unordered):
    if timeout is not None:
        timer = time.time
        end_time = timeout + timer()

    futures = [submit(function, *args) for args in iterable]

    def result_iterator():  # pylint: disable=missing-docstring
        try:
            if unordered:
                if timeout is None:
                    for future in as_completed(futures):
                        yield future.result()
                else:
                    for future in as_completed(futures, end_time - timer()):
                        yield future.result()
            else:
                if timeout is None:
                    for future in futures:
                        yield future.result()
                else:
                    for future in futures:
                        yield future.result(end_time - timer())
        except:
            for future in futures:
                future.cancel()
            raise
    return result_iterator()


def _apply_chunks(function, chunk):
    return [function(*args) for args in chunk]


def _build_chunks(chunksize, iterable):
    while True:
        chunk = tuple(itertools.islice(iterable, chunksize))
        if not chunk:
            return
        yield (chunk,)


def _starmap_chunks(submit, function, iterable,
                    timeout, chunksize, unordered):
    # pylint: disable=too-many-arguments
    function = functools.partial(_apply_chunks, function)
    iterable = _build_chunks(chunksize, iterable)
    result = _starmap_helper(submit, function, iterable,
                             timeout, unordered)
    return itertools.chain.from_iterable(result)


class MPICommExecutor(object):
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

    # pylint: disable=too-few-public-methods

    def __init__(self, comm=None, root=0):
        """Initialize a new MPICommExecutor instance.

        Args:
            comm: MPI (intra)communicator.
            root: Designated master process.

        Raises:
            ValueError: If the communicator has wrong kind or
               the root value is not in the expected range.
        """
        if comm is None:
            comm = _worker.get_world()
        if comm.Is_inter():
            raise ValueError("Expecting an intracommunicator")
        if root < 0 or root >= comm.Get_size():
            raise ValueError("Expecting root in range(comm.size)")

        self._comm = comm
        self._root = root
        self._executor = None

    def __enter__(self):
        """Return `MPIPoolExecutor` instance at the root."""
        # pylint: disable=protected-access
        if self._executor is not None:
            raise RuntimeError("__enter__")

        if _worker.SharedPool:
            assert self._root == 0
            executor = MPIPoolExecutor()
            executor._pool = _worker.SharedPool(executor)
        elif self._comm.Get_size() == 1:
            executor = MPIPoolExecutor()
            executor._pool = _worker.ThreadPool(executor)
        elif self._comm.Get_rank() == self._root:
            executor = MPIPoolExecutor()
            comm = _worker.split(self._comm, self._root)
            executor._pool = _worker.CommPool(executor, comm)
        else:
            executor = None
            comm = _worker.split(self._comm, self._root)
            _worker.server(comm)
            _worker.server_close(comm)

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
