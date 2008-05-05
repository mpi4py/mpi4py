## mpiexec -n 3 python ex-2.29.py

# Use a blocking probe to wait for an incoming message

# --------------------------------------------------------------------

import numpy
import mpi4py.MPI as MPI

if MPI.COMM_WORLD.Get_size() < 3 : raise SystemExit

# --------------------------------------------------------------------

i = numpy.empty(5, dtype='i')
x = numpy.empty(5, dtype='f')
comm = MPI.COMM_WORLD

rank = comm.Get_rank()

if rank == 0:
    i.fill(7)
    comm.Send([i, MPI.INT], 2, 0)
elif rank == 1:
    x.fill(7)
    comm.Send([x, MPI.FLOAT], 2, 0)
elif rank == 2:
    status = MPI.Status()
    for j in xrange(2):
        comm.Probe(MPI.ANY_SOURCE, 0, status)
        if status.Get_source() == 0:
            comm.Recv([i, MPI.INT], 0, 0, status)
        else:
            comm.Recv([x, MPI.FLOAT], 1, 0, status)

# --------------------------------------------------------------------

all = numpy.all

if rank == 2:
    assert all(i == 7)
    assert all(x == 7)
    assert status.source in (0, 1)
    assert status.tag == 0
    assert status.error == 0

# --------------------------------------------------------------------
