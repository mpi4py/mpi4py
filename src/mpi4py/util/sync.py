# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Synchronization utilities."""
import array as _array
import time as _time
from .. import MPI


__all__ = [
    "Sequential",
    "Counter",
    "Mutex",
    "Condition",
    "Semaphore",
]


class Sequential:
    """Sequential execution."""

    def __init__(self, comm, tag=0):
        """Initialize sequential execution.

        Args:
            comm: Intracommunicator context.
            tag: Tag for point-to-point communication.

        """
        self.comm = comm
        self.tag = int(tag)

    def __enter__(self):
        """Enter sequential execution."""
        self.begin()
        return self

    def __exit__(self, *exc):
        """Exit sequential execution."""
        self.end()

    def begin(self):
        """Begin sequential execution."""
        comm = self.comm
        size = comm.Get_size()
        if size == 1:
            return
        rank = comm.Get_rank()
        buf = (bytearray(), 0, MPI.BYTE)
        tag = self.tag
        if rank != 0:
            comm.Recv(buf, rank - 1, tag)

    def end(self):
        """End sequential execution."""
        comm = self.comm
        size = comm.Get_size()
        if size == 1:
            return
        rank = comm.Get_rank()
        buf = (bytearray(), 0, MPI.BYTE)
        tag = self.tag
        if rank != size - 1:
            comm.Send(buf, rank + 1, tag)


class Counter:
    """Global counter."""

    def __init__(
        self,
        start=0,
        step=1,
        *,
        typecode='i',
        comm=MPI.COMM_SELF,
        info=MPI.INFO_NULL,
        root=0,
    ):
        """Initialize global counter.

        Args:
            start: Start value.
            step: Increment value.
            typecode: Type code as defined in the `array` module.
            comm: Intracommunicator context.
            info: Info object for RMA context creation.
            root: Process rank holding the counter memory.

        """
        # pylint: disable=too-many-arguments
        datatype = MPI.Datatype.fromcode(typecode)
        typechar = datatype.typechar
        rank = comm.Get_rank()
        count = 1 if rank == root else 0
        unitsize = datatype.Get_size()
        window = MPI.Win.Allocate(count * unitsize, unitsize, info, comm)
        self._start = start
        self._step = step
        self._window = window
        self._typechar = typechar
        self._location = (root, 0)
        self._comm = comm

        init = _array.array(typechar, [start] * count)
        window.Lock(rank, MPI.LOCK_SHARED)
        window.Accumulate(init, rank, op=MPI.REPLACE)
        window.Unlock(rank)
        comm.Barrier()

    def __iter__(self):
        """Implement ``iter(self)``."""
        return self

    def __next__(self):
        """Implement ``next(self)``."""
        return self.next()

    def next(self, incr=None):
        """Return current value and increment.

        Args:
            incr: Increment value.

        Returns:
            The counter value before incrementing.

        """
        if not self._window:
            raise RuntimeError("counter already freed")

        window = self._window
        typechar = self._typechar
        root, disp = self._location

        incr = incr if incr is not None else self._step
        incr = _array.array(typechar, [incr])
        prev = _array.array(typechar, [0])
        op = MPI.SUM if incr[0] != 0 else MPI.NO_OP
        window.Lock(root, MPI.LOCK_SHARED)
        window.Fetch_and_op(incr, prev, root, disp, op)
        window.Unlock(root)
        return prev[0]

    def free(self):
        """Free counter resources."""
        window = self._window
        self._window = MPI.WIN_NULL
        self._comm = MPI.COMM_NULL
        window.free()


class Mutex:
    """Mutual exclusion."""

    def __init__(
        self,
        *,
        recursive=False,
        comm=MPI.COMM_SELF,
        info=MPI.INFO_NULL,
    ):
        """Initialize mutex object.

        Args:
            comm: Intracommunicator context.
            recursive: Whether to allow recursive acquisition.
            info: Info object for RMA context creation.

        """
        null_rank, tail_rank = MPI.PROC_NULL, 0

        rank = comm.Get_rank()
        count = 3 if rank == tail_rank else 2
        unitsize = MPI.INT.Get_size()
        window = MPI.Win.Allocate(count * unitsize, unitsize, info, comm)
        self._recursive = bool(recursive)
        self._window = window
        self._comm = comm

        init = [False, null_rank, null_rank][:count]
        init = _array.array('i', init)
        window.Lock(rank, MPI.LOCK_SHARED)
        window.Accumulate(init, rank, op=MPI.REPLACE)
        window.Unlock(rank)
        comm.Barrier()

    def _acquire(self, blocking=True):
        null_rank, tail_rank = MPI.PROC_NULL, 0
        lock_id, next_id, tail_id = (0, 1, 2)

        window = self._window
        self_rank = window.group_rank
        window.Lock_all()

        rank = _array.array('i', [self_rank])
        null = _array.array('i', [null_rank])
        prev = _array.array('i', [null_rank])
        window.Accumulate(null, self_rank, next_id, MPI.REPLACE)
        if blocking:
            window.Fetch_and_op(rank, prev, tail_rank, tail_id, MPI.REPLACE)
        else:
            window.Compare_and_swap(rank, null, prev, tail_rank, tail_id)
        window.Flush(tail_rank)
        locked = int(prev[0] == null_rank)
        if blocking and not locked:
            # Add ourselves to the waiting queue
            window.Accumulate(rank, prev[0], next_id, MPI.REPLACE)
            # Spin until we are given the lock
            locked = self._spinloop(lock_id, 0)

        # Set the local lock flag
        flag = _array.array('i', [locked])
        window.Accumulate(flag, self_rank, lock_id, MPI.REPLACE)

        window.Unlock_all()
        return bool(locked)

    def _release(self):
        null_rank, tail_rank = MPI.PROC_NULL, 0
        lock_id, next_id, tail_id = (0, 1, 2)

        window = self._window
        self_rank = window.group_rank
        window.Lock_all()

        rank = _array.array('i', [self_rank])
        null = _array.array('i', [null_rank])
        prev = _array.array('i', [null_rank])
        window.Compare_and_swap(null, rank, prev, tail_rank, tail_id)
        window.Flush(tail_rank)
        if prev[0] != rank[0]:
            # Spin until the next process notify us
            next_rank = self._spinloop(next_id, null_rank)
            # Pass the lock over to the next process
            true = _array.array('i', [True])
            window.Accumulate(true, next_rank, lock_id, MPI.REPLACE)

        # Set the local lock flag
        false = _array.array('i', [False])
        window.Accumulate(false, self_rank, lock_id, MPI.REPLACE)

        window.Unlock_all()

    def _count_fetch_and_op(self, value, op):
        lock_id = 0
        window = self._window
        self_rank = window.group_rank
        incr = _array.array('i', [value])
        prev = _array.array('i', [0])
        window.Lock(self_rank, MPI.LOCK_SHARED)
        window.Fetch_and_op(incr, prev, self_rank, lock_id, op)
        window.Unlock(self_rank)
        return prev[0]

    def _acquire_restore(self, state):
        self._acquire()
        if self._recursive:
            self._count_fetch_and_op(state, MPI.REPLACE)

    def _release_save(self):
        state = None
        if self._recursive:
            state = self._count_fetch_and_op(0, MPI.NO_OP)
        self._release()
        return state

    def _spinloop(self, index, sentinel):
        window = self._window
        return _rma_spinloop(window, 'i', index, sentinel)

    def __enter__(self):
        """Acquire mutex."""
        self.acquire()
        return self

    def __exit__(self, *exc):
        """Release mutex."""
        self.release()

    def acquire(self, blocking=True):
        """Acquire mutex, blocking or non-blocking.

        Args:
            blocking: If `True`, block until the mutex is held.

        Returns:
            `True` if the mutex is held, `False` otherwise.

        """
        if not self._window:
            raise RuntimeError("mutex already freed")
        if self.locked():
            if self._recursive:
                self._count_fetch_and_op(+1, MPI.SUM)
                return True
            raise RuntimeError("cannot acquire already held mutex")
        return self._acquire(blocking)

    def release(self):
        """Release mutex."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        if not self.locked():
            raise RuntimeError("cannot release unheld mutex")
        if self._recursive:
            if self._count_fetch_and_op(-1, MPI.SUM) > 1:
                return
        self._release()

    def locked(self):
        """Return whether the mutex is held."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        lock_id = 0
        memory = memoryview(self._window).cast('i')
        return bool(memory[lock_id])

    def count(self):
        """Return the recursion count."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        return self._count_fetch_and_op(0, MPI.NO_OP)

    def free(self):
        """Free mutex resources."""
        if self._window:
            if self.locked():
                self._release()
        window = self._window
        self._window = MPI.WIN_NULL
        self._comm = MPI.COMM_NULL
        window.free()


class Condition:
    """Condition variable."""

    def __init__(
        self,
        mutex=None,
        *,
        recursive=True,
        comm=MPI.COMM_SELF,
        info=MPI.INFO_NULL,
    ):
        """Initialize condition variable.

        Args:
            mutex: Mutual exclusion object.
            recursive: Whether to allow recursive acquisition.
            comm: Intracommunicator context.
            info: Info object for RMA context creation.

        """
        if mutex is None:
            self._mutex = Mutex(recursive=recursive, comm=comm, info=info)
            self._mutex_free = self._mutex.free
        else:
            self._mutex = mutex
            self._mutex_free = lambda: None
            comm = mutex._comm  # pylint disable=protected-access

        null_rank, tail_rank = MPI.PROC_NULL, 0

        rank = comm.Get_rank()
        count = 3 if rank == tail_rank else 2
        unitsize = MPI.INT.Get_size()
        window = MPI.Win.Allocate(count * unitsize, unitsize, info, comm)
        self._window = window
        self._comm = comm

        init = [0, null_rank, null_rank][:count]
        init = _array.array('i', init)
        window.Lock(rank, MPI.LOCK_SHARED)
        window.Accumulate(init, rank, op=MPI.REPLACE)
        window.Unlock(rank)
        comm.Barrier()

    def _enqueue(self, process):
        null_rank, tail_rank = MPI.PROC_NULL, 0
        next_id, tail_id = (1, 2)
        window = self._window

        rank = _array.array('i', [process])
        prev = _array.array('i', [null_rank])
        next = _array.array('i', [process])  # pylint: disable=W0622

        window.Lock_all()
        window.Fetch_and_op(rank, prev, tail_rank, tail_id, MPI.REPLACE)
        window.Flush(tail_rank)
        if prev[0] != null_rank:
            window.Fetch_and_op(rank, next, prev[0], next_id, MPI.REPLACE)
            window.Flush(prev[0])
        window.Accumulate(next, rank[0], next_id, MPI.REPLACE)
        window.Unlock_all()

    def _dequeue(self, maxnumprocs):
        null_rank, tail_rank = MPI.PROC_NULL, 0
        next_id, tail_id = (1, 2)
        window = self._window

        null = _array.array('i', [null_rank])
        prev = _array.array('i', [null_rank])
        next = _array.array('i', [null_rank])  # pylint: disable=W0622

        processes = []
        maxnumprocs = max(0, min(maxnumprocs, window.group_size))
        window.Lock_all()
        window.Fetch_and_op(null, prev, tail_rank, tail_id, MPI.NO_OP)
        window.Flush(tail_rank)
        if prev[0] != null_rank:
            empty = False
            window.Fetch_and_op(null, next, prev[0], next_id, MPI.NO_OP)
            window.Flush(prev[0])
            while len(processes) < maxnumprocs and not empty:
                rank = next[0]
                processes.append(rank)
                window.Fetch_and_op(null, next, rank, next_id, MPI.NO_OP)
                window.Flush(rank)
                empty = processes[0] == next[0]
            if not empty:
                window.Accumulate(next, prev[0], next_id, MPI.REPLACE)
            else:
                window.Accumulate(null, tail_rank, tail_id, MPI.REPLACE)
        window.Unlock_all()
        return processes

    def _sleep(self):
        flag_id = 0
        window = self._window
        window.Lock_all()
        _rma_spinloop(window, 'i', flag_id, 0, reset=True)
        window.Unlock_all()

    def _wakeup(self, processes):
        flag_id = 0
        window = self._window
        flag = _array.array('i', [1])
        window.Lock_all()
        for rank in processes:
            window.Accumulate(flag, rank, flag_id, MPI.REPLACE)
        window.Unlock_all()

    def _release_save(self):
        # pylint: disable=protected-access
        return self._mutex._release_save()

    def _acquire_restore(self, state):
        # pylint: disable=protected-access
        self._mutex._acquire_restore(state)

    def _mutex_reset(self):
        # pylint: disable=protected-access
        if self._mutex._window:
            if self._mutex.locked():
                self._mutex._release()

    def __enter__(self):
        """Acquire the underlying mutex."""
        self.acquire()
        return self

    def __exit__(self, *exc):
        """Release the underlying mutex."""
        self.release()

    def acquire(self, blocking=True):
        """Acquire the underlying mutex."""
        if not self._window:
            raise RuntimeError("condition already freed")
        return self._mutex.acquire(blocking)

    def release(self):
        """Release the underlying mutex."""
        if not self._window:
            raise RuntimeError("condition already freed")
        self._mutex.release()

    def locked(self):
        """Return whether the underlying mutex is held."""
        return self._mutex.locked()

    def wait(self):
        """Wait until notified by another process.

        Returns:
            Always `True`.

        """
        if not self._window:
            raise RuntimeError("condition already freed")
        if not self.locked():
            raise RuntimeError("cannot wait on unheld mutex")
        self._enqueue(self._window.group_rank)
        state = self._release_save()
        self._sleep()
        self._acquire_restore(state)
        return True

    def wait_for(self, predicate):
        """Wait until a predicate evaluates to `True`.

        Args:
            predicate: callable returning a boolean.

        Returns:
            The result of predicate once it evaluates to `True`.

        """
        result = predicate()
        while not result:
            self.wait()
            result = predicate()
        return result

    def notify(self, n=1):
        """Wake up one or more processes waiting on this condition.

        Args:
            n: Maximum number of processes to wake up.

        Returns:
            The actual number of processes woken up.

        """
        if not self._window:
            raise RuntimeError("condition already freed")
        if not self.locked():
            raise RuntimeError("cannot notify on unheld mutex")
        processes = self._dequeue(n)
        numprocs = len(processes)
        self._wakeup(processes)
        return numprocs

    def notify_all(self):
        """Wake up all processes waiting on this condition.

        Returns:
            The actual number of processes woken up.

        """
        return self.notify((1 << 31) - 1)

    def free(self):
        """Free condition resources."""
        self._mutex_reset()
        self._mutex_free()
        window = self._window
        self._window = MPI.WIN_NULL
        self._comm = MPI.COMM_NULL
        window.free()


class Semaphore:
    """Semaphore object."""

    def __init__(
        self,
        value=1,
        *,
        bounded=True,
        comm=MPI.COMM_SELF,
        info=MPI.INFO_NULL,
    ):
        """Initialize semaphore object.

        Args:
            value: Initial value for internal counter.
            bounded: Bound internal counter to initial value.
            comm: Intracommunicator context.
            info: Info object for RMA context creation.

        """
        if value < 0:
            raise ValueError("initial value must be non-negative")
        self._bounded = bool(bounded)
        self._counter = Counter(value, comm=comm, info=info)
        self._condvar = Condition(recursive=False, comm=comm, info=info)
        self._comm = comm

    def __enter__(self):
        """Acquire semaphore."""
        self.acquire()
        return self

    def __exit__(self, *exc):
        """Release semaphore."""
        self.release()

    def acquire(self, blocking=True):
        """Acquire semaphore, decrementing the internal counter by one.

        Args:
            blocking: If `True`, block until the semaphore is acquired.

        Returns:
            `True` if the semaphore is acquired, `False` otherwise.

        """
        with self._condvar:
            while self._counter.next(0) == 0:
                if not blocking:
                    return False
                self._condvar.wait()
            self._counter.next(-1)
            return True

    def release(self, n=1):
        """Release semaphore, incrementing the internal counter by one or more.

        Args:
            n: Increment for the internal counter.

        """
        if n < 1:
            raise ValueError('increment must be one or more')
        with self._condvar:
            if self._bounded:
                # pylint: disable=protected-access
                current = self._counter.next(0)
                initial = self._counter._start
                if current + n > initial:
                    raise ValueError("semaphore released too many times")
            self._counter.next(n)
            self._condvar.notify(n)

    def free(self):
        """Free semaphore resources."""
        self._counter.free()
        self._condvar.free()
        self._comm = MPI.COMM_NULL


_BACKOFF_DELAY_MAX = 1 / 1024
_BACKOFF_DELAY_MIN = _BACKOFF_DELAY_MAX / 1024
_BACKOFF_DELAY_INIT = 0.0
_BACKOFF_DELAY_RATIO = 2.0


def _new_backoff(
    delay_max=_BACKOFF_DELAY_MAX,
    delay_min=_BACKOFF_DELAY_MIN,
    delay_init=_BACKOFF_DELAY_INIT,
    delay_ratio=_BACKOFF_DELAY_RATIO,
):
    def backoff_iterator():
        delay = delay_init
        while True:
            _time.sleep(delay)
            delay = min(delay_max, max(delay_min, delay * delay_ratio))
            yield
    backoff = backoff_iterator()
    return lambda: next(backoff)


def _rma_progress(window):
    window.Flush(window.group_rank)


def _rma_spinloop(
    window, typecode, index, sentinel, reset=False,
    backoff=None, progress=None,
):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    memory = memoryview(window).cast(typecode)
    backoff = backoff or _new_backoff()
    progress = progress or _rma_progress
    window.Sync()
    while memory[index] == sentinel:
        backoff()
        progress(window)
        window.Sync()
    value = memory[index]
    if reset:
        memory[index] = sentinel
    return value
