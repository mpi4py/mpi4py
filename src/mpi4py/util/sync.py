# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Synchronization utilities."""

import array as _array
import time as _time

from .. import MPI

__all__ = [
    "Sequential",
    "Value",
    "Counter",
    "Mutex",
    "Condition",
    "Semaphore",
    "Event",
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


class Value:
    """Global value."""

    def __init__(
        self,
        typecode,
        value=0,
        *,
        comm=MPI.COMM_SELF,
        info=MPI.INFO_NULL,
        root=0,
    ):
        """Initialize global value.

        Args:
            typecode: Type code as defined in the `array` module.
            value: Initial value.
            comm: Intracommunicator context.
            info: Info object for RMA context creation.
            root: Process rank holding the value memory.

        """
        tcharmap = str.maketrans({"F": "Zf", "D": "Zd"})
        typecode = typecode.translate(tcharmap)
        datatype = MPI.Datatype.fromcode(typecode)
        typecode = datatype.typechar.translate(tcharmap)
        if typecode not in set(_array.typecodes) | set(tcharmap.values()):
            raise ValueError(f"unsupported typecode {typecode!r}")
        rank = comm.Get_rank()
        count = 1 if rank == root else 0
        unitsize = datatype.Get_size()
        init = _new_array(typecode, [value] * count)

        window = MPI.Win.Allocate(count * unitsize, unitsize, info, comm)
        self._window = window
        self._typecode = typecode
        self._location = (root, 0)
        self._comm = comm

        window.Lock(rank, MPI.LOCK_SHARED)
        window.Accumulate(init, rank, op=MPI.REPLACE)
        window.Unlock(rank)
        comm.Barrier()

    value = property(doc="Value.")

    @value.getter
    def value(self):
        """Get value."""
        return self.get()

    @value.setter
    def value(self, value):
        """Set value."""
        self.set(value)

    typecode = property(doc="Typecode.")

    @typecode.getter
    def typecode(self):
        """Get typecode."""
        return self._typecode

    def compare_and_swap(self, value, compare):
        """Compare-and-swap.

        Args:
            value: The value to swap with.
            compare: The value to compare with.

        Returns:
            The current value before comparing/swapping.

        """
        if not self._window:
            raise RuntimeError("value already freed")

        window = self._window
        typecode = self._typecode
        root, disp = self._location

        newval = _new_array(typecode, [value])
        cmpval = _new_array(typecode, [compare])
        oldval = _new_array(typecode, [0])
        window.Lock(root, MPI.LOCK_SHARED)
        window.Compare_and_swap(newval, cmpval, oldval, root, disp)
        window.Unlock(root)
        return oldval[0]

    def accumulate(self, value, op):
        """Accumulate.

        Args:
            value: The value to operate with.
            op: The MPI operation to perform.

        """
        if not self._window:
            raise RuntimeError("value already freed")

        window = self._window
        typecode = self._typecode
        root, disp = self._location

        newval = _new_array(typecode, [value])
        window.Lock(root, MPI.LOCK_SHARED)
        window.Accumulate(newval, root, disp, op)
        window.Unlock(root)

    def fetch_and_op(self, value, op):
        """Fetch-and-op.

        Args:
            value: The value to operate with.
            op: The MPI operation to perform.

        Returns:
            The value before operating.

        """
        if not self._window:
            raise RuntimeError("value already freed")

        window = self._window
        typecode = self._typecode
        root, disp = self._location

        newval = _new_array(typecode, [value])
        oldval = _new_array(typecode, [0])
        window.Lock(root, MPI.LOCK_SHARED)
        window.Fetch_and_op(newval, oldval, root, disp, op)
        window.Unlock(root)
        return oldval[0]

    def fetch_and_set(self, value):
        """Fetch-and-set.

        Args:
            value: The value to set.

        Returns:
            The value before setting.

        """
        return self.fetch_and_op(value, MPI.REPLACE)

    def fetch_and_add(self, value):
        """Fetch-and-add.

        Args:
            value: The value to add.

        Returns:
            The value before adding.

        """
        return self.fetch_and_op(value, MPI.SUM)

    def get(self):
        """Get value."""
        return self.fetch_and_op(0, MPI.NO_OP)

    def set(self, value):
        """Set value."""
        self.accumulate(value, MPI.REPLACE)

    def add(self, value):
        """Add value."""
        self.accumulate(value, MPI.SUM)

    def free(self):
        """Free value resources."""
        window = self._window
        self._window = MPI.WIN_NULL
        self._comm = MPI.COMM_NULL
        window.free()


class Counter:
    """Global counter."""

    def __init__(
        self,
        start=0,
        step=1,
        *,
        typecode="i",
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
        self._value = Value(typecode, start, comm=comm, info=info, root=root)
        self._start = start
        self._step = step

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
        return self._value.fetch_and_add(
            incr if incr is not None else self._step
        )

    def reset(self, init=None):
        """Return current value and reset to start value.

        Args:
            init: Start value.

        Returns:
            The counter value before resetting.

        """
        return self._value.fetch_and_set(
            init if init is not None else self._start
        )

    def free(self):
        """Free counter resources."""
        self._value.free()


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
        init = _array.array("i", init)
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

        rank = _array.array("i", [self_rank])
        null = _array.array("i", [null_rank])
        prev = _array.array("i", [null_rank])
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
        flag = _array.array("i", [locked])
        window.Accumulate(flag, self_rank, lock_id, MPI.REPLACE)

        window.Unlock_all()
        return bool(locked)

    def _release(self):
        null_rank, tail_rank = MPI.PROC_NULL, 0
        lock_id, next_id, tail_id = (0, 1, 2)

        window = self._window
        self_rank = window.group_rank
        window.Lock_all()

        rank = _array.array("i", [self_rank])
        null = _array.array("i", [null_rank])
        prev = _array.array("i", [null_rank])
        window.Compare_and_swap(null, rank, prev, tail_rank, tail_id)
        window.Flush(tail_rank)
        if prev[0] != rank[0]:
            # Spin until the next process notify us
            next_rank = self._spinloop(next_id, null_rank)
            # Pass the lock over to the next process
            true = _array.array("i", [True])
            window.Accumulate(true, next_rank, lock_id, MPI.REPLACE)

        # Set the local lock flag
        false = _array.array("i", [False])
        window.Accumulate(false, self_rank, lock_id, MPI.REPLACE)

        window.Unlock_all()

    def _owned(self):
        lock_id = 0
        memory = memoryview(self._window).cast("i")
        return bool(memory[lock_id])

    def _locked(self):
        null_rank, tail_rank = MPI.PROC_NULL, 0
        tail_id = 2
        window = self._window
        zero = _array.array("i", [0])
        prev = _array.array("i", [null_rank])
        window.Lock(tail_rank, MPI.LOCK_SHARED)
        window.Fetch_and_op(zero, prev, tail_rank, tail_id, MPI.NO_OP)
        window.Unlock(tail_rank)
        return prev[0] != null_rank

    def _count_fetch_and_op(self, value, op):
        lock_id = 0
        window = self._window
        self_rank = window.group_rank
        incr = _array.array("i", [value])
        prev = _array.array("i", [0])
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

    def _spinloop(self, index, value):
        window = self._window
        return _rma_spinloop(window, "i", index, value)

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
        if self._owned():
            if self._recursive:
                self._count_fetch_and_op(+1, MPI.SUM)
                return True
            raise RuntimeError("cannot acquire already held mutex")
        return self._acquire(blocking)

    def release(self):
        """Release mutex."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        if not self._owned():
            raise RuntimeError("cannot release unheld mutex")
        if self._recursive:
            if self._count_fetch_and_op(-1, MPI.SUM) > 1:
                return
        self._release()

    def owned(self):
        """Return whether the mutex is held by the caller process."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        return self._owned()

    def locked(self):
        """Return whether the mutex is held by any process."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        return self._owned() or self._locked()

    def count(self):
        """Return the recursion count."""
        if not self._window:
            raise RuntimeError("mutex already freed")
        return self._count_fetch_and_op(0, MPI.NO_OP)

    def free(self):
        """Free mutex resources."""
        if self._window:
            if self._owned():
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
        init = _array.array("i", init)
        window.Lock(rank, MPI.LOCK_SHARED)
        window.Accumulate(init, rank, op=MPI.REPLACE)
        window.Unlock(rank)
        comm.Barrier()

    def _enqueue(self, process):
        # pylint: disable=redefined-builtin
        null_rank, tail_rank = MPI.PROC_NULL, 0
        next_id, tail_id = (1, 2)
        window = self._window

        rank = _array.array("i", [process])
        prev = _array.array("i", [null_rank])
        next = _array.array("i", [process])  # noqa: A001

        window.Lock_all()
        window.Fetch_and_op(rank, prev, tail_rank, tail_id, MPI.REPLACE)
        window.Flush(tail_rank)
        if prev[0] != null_rank:
            window.Fetch_and_op(rank, next, prev[0], next_id, MPI.REPLACE)
            window.Flush(prev[0])
        window.Accumulate(next, rank[0], next_id, MPI.REPLACE)
        window.Unlock_all()

    def _dequeue(self, maxnumprocs):
        # pylint: disable=redefined-builtin
        null_rank, tail_rank = MPI.PROC_NULL, 0
        next_id, tail_id = (1, 2)
        window = self._window

        null = _array.array("i", [null_rank])
        prev = _array.array("i", [null_rank])
        next = _array.array("i", [null_rank])  # noqa: A001

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
        _rma_spinloop(window, "i", flag_id, 0, reset=True)
        window.Unlock_all()

    def _wakeup(self, processes):
        flag_id = 0
        window = self._window
        flag = _array.array("i", [1])
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

    def _mutex_owned(self):
        # pylint: disable=protected-access
        return self._mutex._owned()

    def _mutex_reset(self):
        # pylint: disable=protected-access
        if self._mutex._window:
            if self._mutex._owned():
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

    def owned(self):
        """Return whether the underlying mutex is held by the caller."""
        if not self._window:
            raise RuntimeError("condition already freed")
        return self._mutex.owned()

    def locked(self):
        """Return whether the underlying mutex is held by any process."""
        if not self._window:
            raise RuntimeError("condition already freed")
        return self._mutex.locked()

    def wait(self):
        """Wait until notified by another process.

        Returns:
            Always `True`.

        """
        if not self._window:
            raise RuntimeError("condition already freed")
        if not self._mutex_owned():
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
        if not self._mutex_owned():
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
            raise ValueError("increment must be one or more")
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


class Event:
    """Event object."""

    def __init__(
        self,
        *,
        comm=MPI.COMM_SELF,
        info=MPI.INFO_NULL,
        root=0,
    ):
        """Initialize event object.

        Args:
            comm: Intracommunicator context.
            info: Info object for RMA context creation.
            root: Process rank holding flag memory.

        """
        self._cond = Condition(comm=comm, info=info)
        self._flag = Value("i", 0, comm=comm, info=info, root=root)

    def is_set(self):
        """Return whether the internal flag is `True`."""
        return bool(self._flag.value)

    def set(self):
        """Set the internal flag to `True`."""
        with self._cond:
            self._flag.value = int(True)
            self._cond.notify_all()

    def clear(self):
        """Reset the internal flag to `False`."""
        with self._cond:
            self._flag.value = int(False)

    def wait(self):
        """Block until the internal flag is `True`."""
        with self._cond:
            done = bool(self._flag.value)
            if not done:
                done = self._cond.wait()
            return done

    def free(self):
        """Free event resources."""
        self._cond.free()
        self._flag.free()


def _new_array(typecode, initializer):
    if __import__("sys").version_info < (3, 15):  # pragma: no cover
        if typecode in {"Zf", "Zd"}:
            numpy = __import__("numpy")
            dtype = numpy.dtype(typecode[-1].upper())
            return numpy.array(initializer, dtype)
    return _array.array(typecode, initializer)  # ty: ignore[deprecated]


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
    window,
    typecode,
    index,
    value,
    reset=False,
    backoff=None,
    progress=None,
):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    memory = memoryview(window).cast(typecode)
    backoff = backoff or _new_backoff()
    progress = progress or _rma_progress
    window.Sync()
    while memory[index] == value:
        backoff()
        progress(window)
        window.Sync()
    value = memory[index]
    if reset:
        memory[index] = value
    return value
