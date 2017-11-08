# --------------------------------------------------------------------

from mpi4py import MPI
from array import array as _array
import struct as _struct

class Counter(object):

    def __init__(self, comm):
        #
        size = comm.Get_size()
        rank = comm.Get_rank()
        #
        itemsize = MPI.INT.Get_size()
        if rank == 0:
            mem = MPI.Alloc_mem(itemsize*size, MPI.INFO_NULL)
            mem[:] = _struct.pack('i', 0) * size
        else:
            mem = MPI.BOTTOM
        self.win = MPI.Win.Create(mem, itemsize, MPI.INFO_NULL, comm)
        #
        blens = [rank, size-rank-1]
        disps = [0, rank+1]
        self.dt_get = MPI.INT.Create_indexed(blens, disps).Commit()
        #
        self.myval = 0

    def free(self):
        self.dt_get.Free()
        mem = self.win.tomemory()
        self.win.Free()
        if mem: MPI.Free_mem(mem)

    def next(self):
        #
        group  = self.win.Get_group()
        size = group.Get_size()
        rank = group.Get_rank()
        group.Free()
        #
        incr = _array('i', [1])
        vals = _array('i', [0])*size
        self.win.Lock(0)
        self.win.Accumulate([incr, 1, MPI.INT], 0,
                            [rank, 1, MPI.INT], MPI.SUM)
        self.win.Get([vals, 1, self.dt_get], 0,
                     [   0, 1, self.dt_get])
        self.win.Unlock(0)
        #
        vals[rank] = self.myval
        self.myval += 1
        nxtval = sum(vals)
        #
        return nxtval

# --------------------------------------------------------------------

def test():
    vals = []
    counter = Counter(MPI.COMM_WORLD)
    for i in range(5):
        c = counter.next()
        vals.append(c)
    counter.free()

    vals = MPI.COMM_WORLD.allreduce(vals)
    assert sorted(vals) == list(range(len(vals)))

if __name__ == '__main__':
    test()

# --------------------------------------------------------------------
