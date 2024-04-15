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
    "RMutex",
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
    """Parallel counter."""

    def __init__(
        self,
        comm,
        start=0,
        step=1,
        typecode='i',
        root=0,
        info=MPI.INFO_NULL,
    ):
        """Initialize counter object.

        Args:
            comm: Intracommunicator context.
            start: Start value.
            step: Increment value.
            typecode: Type code as defined in the `array` module.
            root: Process rank holding the counter memory.
            info: Info object for RMA context creation.

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
        rank, disp = self._location

        incr = incr if incr is not None else self._step
        incr = _array.array(typechar, [incr])
        prev = _array.array(typechar, [0])
        window.Lock(rank, MPI.LOCK_SHARED)
        window.Fetch_and_op(incr, prev, rank, disp, MPI.SUM)
        window.Unlock(rank)
        return prev[0]

    def free(self):
        """Free counter resources."""
        window = self._window
        self._window = MPI.WIN_NULL
        if window:
            window.Free()


class Mutex:
    """Parallel mutex."""

    def __init__(self, comm, info=MPI.INFO_NULL):
        """Initialize mutex object.

        Args:
            comm: Intracommunicator context.
            info: Info object for RMA context creation.

        """
        null_rank, tail_rank = MPI.PROC_NULL, 0

        rank = comm.Get_rank()
        count = 3 if rank == tail_rank else 2
        unitsize = MPI.INT.Get_size()
        window = MPI.Win.Allocate(count * unitsize, unitsize, info, comm)
        self._rank = rank
        self._window = window

        init = [False, null_rank, null_rank][:count]
        init = _array.array('i', init)
        window.Lock(rank, MPI.LOCK_SHARED)
        window.Accumulate(init, rank, op=MPI.REPLACE)
        window.Unlock(rank)
        comm.Barrier()

    def __enter__(self):
        """Acquire mutex."""
        self.acquire()
        return self

    def __exit__(self, *exc):
        """Release mutex."""
        self.release()

    def _backoff(self):
        backoff = _new_backoff()
        return lambda: next(backoff)

    def _progress(self):
        return lambda: self._window.Flush(self._rank)

    def _spinloop(self, index, sentinel):
        window = self._window
        memory = memoryview(window).cast('i')
        backoff = self._backoff()
        progress = self._progress()
        window.Sync()
        while memory[index] == sentinel:
            backoff()
            progress()
            window.Sync()
        return memory[index]

    def acquire(self, blocking=True):
        """Acquire mutex, blocking or non-blocking.

        Args:
            blocking: If `True`, block until the mutex is held.

        Returns:
            `True` if mutex is held, `False` otherwise.

        """
        null_rank, tail_rank = MPI.PROC_NULL, 0
        lock_id, next_id, tail_id = (0, 1, 2)

        if not self._window:
            raise RuntimeError("mutex already freed")
        if self.locked():
            raise RuntimeError("cannot acquire already held mutex")

        window = self._window
        window.Lock_all()

        rank = _array.array('i', [self._rank])
        null = _array.array('i', [null_rank])
        prev = _array.array('i', [null_rank])
        window.Accumulate(null, self._rank, next_id, MPI.REPLACE)
        if blocking:
            window.Fetch_and_op(rank, prev, tail_rank, tail_id, MPI.REPLACE)
        else:
            window.Compare_and_swap(rank, null, prev, tail_rank, tail_id)
        window.Flush(tail_rank)
        locked = bool(prev[0] == null_rank)
        if blocking and not locked:
            # Add ourselves to the waiting queue
            window.Accumulate(rank, prev[0], next_id, MPI.REPLACE)
            # Spin until we are given the lock
            locked = bool(self._spinloop(lock_id, 0))

        # Set the local lock flag
        flag = _array.array('i', [locked])
        window.Accumulate(flag, self._rank, lock_id, MPI.REPLACE)

        window.Unlock_all()
        return locked

    def release(self):
        """Release mutex."""
        null_rank, tail_rank = MPI.PROC_NULL, 0
        lock_id, next_id, tail_id = (0, 1, 2)

        if not self._window:
            raise RuntimeError("mutex already freed")
        if not self.locked():
            raise RuntimeError("cannot release unheld mutex")

        window = self._window
        window.Lock_all()

        rank = _array.array('i', [self._rank])
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
        window.Accumulate(false, self._rank, lock_id, MPI.REPLACE)

        window.Unlock_all()

    def locked(self):
        """Return whether the mutex is held."""
        lock_id = 0

        if not self._window:
            raise RuntimeError("mutex already freed")

        memory = memoryview(self._window).cast('i')
        return bool(memory[lock_id])

    def free(self):
        """Free mutex resources."""
        if self._window:
            if self.locked():
                self.release()
        window = self._window
        self._rank = MPI.PROC_NULL
        self._window = MPI.WIN_NULL
        if window:
            window.Free()


class RMutex:
    """Parallel recursive mutex."""

    def __init__(self, comm, info=MPI.INFO_NULL):
        """Initialize recursive mutex object.

        Args:
            comm: Intracommunicator context.
            info: Info object for RMA context creation.

        """
        self._block = Mutex(comm, info)
        self._count = 0

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
            `True` if mutex is held, `False` otherwise.

        """
        if self._block.locked():
            self._count += 1
            return True
        locked = self._block.acquire(blocking)
        if locked:
            self._count = 1
        return locked

    def release(self):
        """Release mutex."""
        if not self._block.locked():
            raise RuntimeError("cannot release unheld mutex")
        self._count = count = self._count - 1
        if not count:
            self._block.release()

    def count(self):
        """Return recursion count."""
        return self._count

    def free(self):
        """Free mutex resources."""
        self._block.free()
        self._count = 0


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
    def backoff():
        delay = delay_init
        while True:
            _time.sleep(delay)
            delay = min(delay_max, max(delay_min, delay * delay_ratio))
            yield
    return backoff()
