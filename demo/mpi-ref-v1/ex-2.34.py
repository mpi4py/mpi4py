## mpiexec -n 2 python ex-2.34.py

# Use of ready-mode and synchonous-mode

# --------------------------------------------------------------------

from mpi4py import MPI
try:
    import numpy
except ImportError:
    raise SystemExit

if MPI.COMM_WORLD.Get_size() < 2:
    raise SystemExit

# --------------------------------------------------------------------

comm = MPI.COMM_WORLD

buff = numpy.empty((1000,2), dtype='f', order='fortran')

rank = comm.Get_rank()

if rank == 0:
    req1 = comm.Irecv([buff[:, 0], MPI.FLOAT], 1, 1)
    req2 = comm.Irecv([buff[:, 1], MPI.FLOAT], 1, 2)
    status = [MPI.Status(), MPI.Status()]
    MPI.Request.Waitall([req1, req2], status)
elif rank == 1:
    buff[:, 0] = 5
    buff[:, 1] = 7
    comm.Ssend([buff[:, 1], MPI.FLOAT], 0, 2)
    comm.Rsend([buff[:, 0], MPI.FLOAT], 0, 1)

# --------------------------------------------------------------------

all = numpy.all

if rank == 0:
    assert all(buff[:, 0] == 5)
    assert all(buff[:, 1] == 7)
    assert status[0].source == 1
    assert status[0].tag ==  1
    assert status[1].source == 1
    assert status[1].tag ==  2

# --------------------------------------------------------------------
