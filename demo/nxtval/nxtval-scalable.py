from mpi4py import MPI

# -----------------------------------------------------------------------------

import struct as _struct
try:
    from numpy import empty as _empty
    def _array_new(size, typecode, init=0):
        a = _empty(size, typecode)
        a.fill(init)
        return a
    def _array_set(ary, value):
        ary.fill(value)
    def _array_sum(ary):
        return ary.sum()
except ImportError:
    from array import array as _array
    def _array_new(size, typecode, init=0):
        return _array(typecode, [init]) * size
    def _array_set(ary, value):
        for i, _ in enumerate(ary):
            ary[i] = value
    def _array_sum(ary):
        return sum(ary, 0)

# -----------------------------------------------------------------------------

class Counter(object):

    def __init__(self, comm, init=0):
        #
        size = comm.Get_size()
        rank = comm.Get_rank()
        mask = 1
        while mask < size:
            mask <<= 1
        mask >>= 1
        idx = 0
        get_idx = []
        acc_idx = []
        while mask >= 1:
            left  = idx + 1
            right = idx + (mask<<1)
            if rank < mask:
                acc_idx.append( left  )
                get_idx.append( right )
                idx = left
            else:
                acc_idx.append( right )
                get_idx.append( left  )
                idx = right
            rank = rank % mask
            mask >>= 1
        #
        typecode = 'i'
        datatype = MPI.INT
        itemsize = datatype.Get_size()
        #
        root = 0
        rank = comm.Get_rank()
        if rank == root:
            nlevels = len(get_idx) + 1
            nentries = (1<<nlevels) - 1
            self.mem = MPI.Alloc_mem(nentries*itemsize, MPI.INFO_NULL)
            self.mem[:] = _struct.pack(typecode, init) * nentries
        else:
            self.mem = None
        #
        self.win = MPI.Win.Create(self.mem, itemsize, MPI.INFO_NULL, comm)
        self.acc_type = datatype.Create_indexed_block(1, acc_idx).Commit()
        self.get_type = datatype.Create_indexed_block(1, get_idx).Commit()
        self.acc_buf = _array_new(len(acc_idx), typecode)
        self.get_buf = _array_new(len(get_idx), typecode)
        self.myval = 0

    def free(self):
        if self.win:
            self.win.Free()
        if self.mem:
            MPI.Free_mem(self.mem)
            self.mem = None
        if self.get_type:
            self.get_type.Free()
        if self.acc_type:
            self.acc_type.Free()

    def next(self, increment=1):
        _array_set(self.acc_buf, increment)
        root = 0
        self.win.Lock(root)
        self.win.Get(self.get_buf, root, [0, 1, self.get_type])
        self.win.Accumulate(self.acc_buf, root, [0, 1, self.acc_type], MPI.SUM)
        self.win.Unlock(root)
        nxtval = self.myval + _array_sum(self.get_buf)
        self.myval += increment
        return nxtval

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
