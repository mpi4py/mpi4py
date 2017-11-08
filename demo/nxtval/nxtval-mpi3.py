from mpi4py import MPI
from array import array as _array
import struct as _struct

# --------------------------------------------------------------------

class Counter(object):

    def __init__(self, comm):
        rank = comm.Get_rank()
        itemsize = MPI.INT.Get_size()
        if rank == 0:
            n = 1
        else:
            n = 0
        self.win = MPI.Win.Allocate(n*itemsize, itemsize, 
                                    MPI.INFO_NULL, comm)
        if rank == 0:
            mem = self.win.tomemory()
            mem[:] = _struct.pack('i', 0)

    def free(self):
        self.win.Free()

    def next(self, increment=1):
        incr = _array('i', [increment])
        nval = _array('i', [0])
        self.win.Lock(0)
        self.win.Get_accumulate([incr, 1, MPI.INT], 
                                [nval, 1, MPI.INT],
                                0, op=MPI.SUM)
        self.win.Unlock(0)
        return nval[0]

# -----------------------------------------------------------------------------

class Mutex(object):

    def __init__(self, comm):
        self.counter = Counter(comm)

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, *exc):
        self.unlock()
        return None

    def free(self):
        self.counter.free()

    def lock(self):
        value = self.counter.next(+1)
        while value != 0:
            value = self.counter.next(-1)
            value = self.counter.next(+1)

    def unlock(self):
        self.counter.next(-1)

# -----------------------------------------------------------------------------

def test_counter():
    vals = []
    counter = Counter(MPI.COMM_WORLD)
    for i in range(5):
        c = counter.next()
        vals.append(c)
    counter.free()

    vals = MPI.COMM_WORLD.allreduce(vals)
    assert sorted(vals) == list(range(len(vals)))

def test_mutex():
    mutex = Mutex(MPI.COMM_WORLD)
    mutex.lock()
    mutex.unlock()
    mutex.free()

if __name__ == '__main__':
    test_counter()
    test_mutex()

# -----------------------------------------------------------------------------
