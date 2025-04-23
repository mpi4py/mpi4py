# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""`multiprocessing.pool` interface via `mpi4py.futures`."""

import functools as _functools
import operator as _operator
import os as _os
import threading as _threading
import warnings as _warnings
import weakref as _weakref

from .. import futures as _futures

__all__ = [
    "Pool",
    "ThreadPool",
    "AsyncResult",
    "ApplyResult",
    "MapResult",
]


class Pool:
    """Pool using MPI processes as workers."""

    Executor = _futures.MPIPoolExecutor

    def __init__(
        self,
        processes=None,
        initializer=None,
        initargs=(),
        **kwargs,
    ):
        """Initialize a new Pool instance.

        Args:
            processes: Number of worker processes.
            initializer: An callable used to initialize workers processes.
            initargs: A tuple of arguments to pass to the initializer.

        .. note::

           Additional keyword arguments are passed down to the
           `MPIPoolExecutor` constructor.

        .. warning::

           The *maxtasksperchild* and *context* arguments of
           `multiprocessing.pool.Pool` are not supported.  Specifying
           *maxtasksperchild* or *context* with a value other than `None` will
           issue a warning of category `UserWarning`.

        """
        if processes is not None:
            if processes < 1:
                raise ValueError("number of processes must be at least 1")
        if initializer is not None:
            if not callable(initializer):
                raise TypeError("initializer must be a callable")
        for name in ("maxtasksperchild", "context"):
            if kwargs.pop(name, None) is not None:
                message = f"argument {name!r} is not supported"
                _warnings.warn(message, stacklevel=2)

        self.executor = self.Executor(
            processes,
            initializer=initializer,
            initargs=initargs,
            **kwargs,
        )

    def apply(
        self,
        func,
        args=(),
        kwds={},  # noqa: B006
    ):
        """Call *func* with arguments *args* and keyword arguments *kwds*.

        Equivalent to ``func(*args, **kwds)``.
        """
        # pylint: disable=dangerous-default-value
        future = self.executor.submit(func, *args, **kwds)
        return future.result()

    def apply_async(
        self,
        func,
        args=(),
        kwds={},  # noqa: B006
        callback=None,
        error_callback=None,
    ):
        """Asynchronous version of `apply()` returning `ApplyResult`."""
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        # pylint: disable=dangerous-default-value
        future = self.executor.submit(func, *args, **kwds)
        return ApplyResult(future, callback, error_callback)

    def map(
        self,
        func,
        iterable,
        chunksize=None,
    ):
        """Apply *func* to each element in *iterable*.

        Equivalent to ``list(map(func, iterable))``.

        Block until all results are ready and return them in a `list`.

        The *iterable* is choped into a number of chunks which are submitted as
        separate tasks. The (approximate) size of these chunks can be specified
        by setting *chunksize* to a positive integer.

        Consider using `imap()` or `imap_unordered()` with explicit *chunksize*
        for better efficiency.

        """
        iterable, chunksize = _chunksize(self, iterable, chunksize)
        return list(self.imap(func, iterable, chunksize=chunksize))

    def map_async(
        self,
        func,
        iterable,
        chunksize=None,
        callback=None,
        error_callback=None,
    ):
        """Asynchronous version of `map()` returning `MapResult`."""
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        iterable, chunksize = _chunksize(self, iterable, chunksize)
        result_iterator = self.imap(func, iterable, chunksize=chunksize)
        future = _async_executor(self).submit(list, result_iterator)
        return MapResult(future, callback, error_callback)

    def imap(
        self,
        func,
        iterable,
        chunksize=1,
    ):
        """Like `map()` but return an `iterator`.

        Equivalent to ``map(func, iterable)``.

        """
        return self.executor.map(func, iterable, chunksize=chunksize)

    def imap_unordered(
        self,
        func,
        iterable,
        chunksize=1,
    ):
        """Like `imap()` but ordering of results is arbitrary."""
        return self.executor.map(
            func, iterable, chunksize=chunksize, unordered=True
        )

    def starmap(
        self,
        func,
        iterable,
        chunksize=None,
    ):
        """Apply *func* to each argument tuple in *iterable*.

        Equivalent to ``list(itertools.starmap(func, iterable))``.

        Block until all results are ready and return them in a `list`.

        The *iterable* is choped into a number of chunks which are submitted as
        separate tasks. The (approximate) size of these chunks can be specified
        by setting *chunksize* to a positive integer.

        Consider using `istarmap()` or `istarmap_unordered()` with explicit
        *chunksize* for better efficiency.

        """
        iterable, chunksize = _chunksize(self, iterable, chunksize)
        return list(self.istarmap(func, iterable, chunksize=chunksize))

    def starmap_async(
        self,
        func,
        iterable,
        chunksize=None,
        callback=None,
        error_callback=None,
    ):
        """Asynchronous version of `starmap()` returning `MapResult`."""
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        iterable, chunksize = _chunksize(self, iterable, chunksize)
        result_iterator = self.istarmap(func, iterable, chunksize=chunksize)
        future = _async_executor(self).submit(list, result_iterator)
        return MapResult(future, callback, error_callback)

    def istarmap(
        self,
        func,
        iterable,
        chunksize=1,
    ):
        """Like `starmap()` but return an `iterator`.

        Equivalent to ``itertools.starmap(func, iterable)``.

        """
        return self.executor.starmap(
            func,
            iterable,
            chunksize=chunksize,
        )

    def istarmap_unordered(
        self,
        func,
        iterable,
        chunksize=1,
    ):
        """Like `istarmap()` but ordering of results is arbitrary."""
        return self.executor.starmap(
            func,
            iterable,
            chunksize=chunksize,
            unordered=True,
        )

    def close(self):
        """Prevent any more tasks from being submitted to the pool."""
        self.executor.shutdown(wait=False)

    def terminate(self):
        """Stop the worker processes without completing pending tasks."""
        self.executor.shutdown(wait=False, cancel_futures=True)

    def join(self):
        """Wait for the worker processes to exit."""
        self.executor.shutdown(wait=True)
        _async_executor_shutdown(self)

    def __enter__(self):
        """Return pool."""
        return self

    def __exit__(self, *args):
        """Close pool."""
        self.close()


class ThreadPool(Pool):
    """Pool using threads as workers."""

    Executor = _futures.ThreadPoolExecutor


class AsyncResult:
    """Asynchronous result."""

    def __init__(self, future, callback=None, error_callback=None):
        """Wrap a future object and register callbacks."""
        self.future = future
        self._event = _threading.Event()
        done_cb = _functools.partial(
            _async_future_callback,
            event=self._event,
            callback=callback,
            error_callback=error_callback,
        )
        self.future.add_done_callback(done_cb)

    def get(self, timeout=None):
        """Return the result when it arrives.

        If *timeout* is not `None` and the result does not arrive within
        *timeout* seconds then raise `TimeoutError`.

        If the remote call raised an exception then that exception will be
        reraised.

        """
        self.wait(timeout)
        if not self.ready():
            raise TimeoutError
        try:
            return self.future.result()
        except _futures.CancelledError:
            raise TimeoutError from None

    def wait(self, timeout=None):
        """Wait until the result is available or *timeout* seconds pass."""
        self._event.wait(timeout)

    def ready(self):
        """Return whether the call has completed."""
        return self._event.is_set()

    def successful(self):
        """Return whether the call completed without raising an exception.

        If the result is not ready then raise `ValueError`.

        """
        if not self.ready():
            raise ValueError(f"{self!r} not ready")
        try:
            return self.future.exception() is None
        except _futures.CancelledError:
            return False


class ApplyResult(AsyncResult):
    """Result type of `apply_async()`."""


class MapResult(AsyncResult):
    """Result type of `map_async()` and `starmap_async()`."""


def _chunksize(pool, iterable, chunksize):
    if chunksize is None:
        chunksize = 1
        num_workers = getattr(pool.executor, "_max_workers", 0)
        if num_workers > 0:  # pragma: no branch
            num_tasks = _operator.length_hint(iterable)
            if num_tasks == 0:
                iterable = list(iterable)
                num_tasks = len(iterable)
            if num_tasks > 0:
                quot, rem = divmod(num_tasks, num_workers * 4)
                chunksize = quot + bool(rem)
    return iterable, chunksize


def _async_future_callback(future, event, callback, error_callback):
    assert future.done()  # noqa: S101
    try:
        exception = future.exception()
    except _futures.CancelledError:
        exception = TimeoutError()
    try:
        if exception is not None:
            if error_callback is not None:
                error_callback(exception)
        else:
            if callback is not None:
                callback(future.result())
    finally:
        event.set()


_cpu_count = getattr(_os, "process_cpu_count", _os.cpu_count)

_async_executor_lock = _threading.Lock()

_async_executor_cache = _weakref.WeakKeyDictionary()
# type: _weakref.WeakKeyDictionary[Pool, _futures.ThreadPoolExecutor]


def _async_get_max_workers(pool):
    max_workers = getattr(pool, "_async_max_workers", 0)
    return max_workers or min(4, _cpu_count() or 1)


def _async_executor(pool):
    with _async_executor_lock:
        executor = _async_executor_cache.get(pool)
        if executor is None:
            max_workers = _async_get_max_workers(pool)
            executor = _futures.ThreadPoolExecutor(max_workers)
            _async_executor_cache[pool] = executor
    return executor


def _async_executor_shutdown(pool, wait=True):
    with _async_executor_lock:
        executor = _async_executor_cache.pop(pool, None)
    if executor is not None:
        executor.shutdown(wait=wait)
