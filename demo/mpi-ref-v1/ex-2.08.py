## mpiexec -n 2 python ex-2.08.py

# An exchange of messages

# --------------------------------------------------------------------

import mpi4py.MPI as MPI
if MPI.COMM_WORLD.Get_size() < 2 : raise SystemExit

import numpy

# --------------------------------------------------------------------

sendbuf = numpy.empty(10, dtype=float)
recvbuf = numpy.empty(10, dtype=float)
tag = 0
status = MPI.Status()

myrank = MPI.COMM_WORLD.Get_rank()

if myrank == 0:
    sendbuf[:] = numpy.arange(len(sendbuf))
    MPI.COMM_WORLD.Send([sendbuf, MPI.DOUBLE], 1, tag)
    MPI.COMM_WORLD.Recv([recvbuf, MPI.DOUBLE], 1, tag, status)
elif myrank == 1:
    MPI.COMM_WORLD.Recv([recvbuf, MPI.DOUBLE], 0, tag, status)
    sendbuf[:] = recvbuf
    MPI.COMM_WORLD.Send([sendbuf, MPI.DOUBLE], 0, tag)

# --------------------------------------------------------------------

if myrank == 0:
    assert status.source == 1
    assert status.tag == tag
    assert status.error == MPI.SUCCESS
    assert status.Get_count(MPI.DOUBLE) == len(recvbuf)
    assert (sendbuf == recvbuf).all()
elif myrank == 1:
    assert status.source == 0
    assert status.tag == tag
    assert status.error == MPI.SUCCESS
    assert status.Get_count(MPI.DOUBLE) == len(recvbuf)
    assert (sendbuf == recvbuf).all()

# --------------------------------------------------------------------
