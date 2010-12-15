## mpiexec -n 3 python ex-2.29.py

# Use a blocking probe to wait for an incoming message

# --------------------------------------------------------------------

from mpi4py import MPI
import array

if MPI.COMM_WORLD.Get_size() < 3:
    raise SystemExit

# --------------------------------------------------------------------

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    i = array.array('i', [7]*5)
    comm.Send([i, MPI.INT], 2, 0)
elif rank == 1:
    x = array.array('f', [7]*5)
    comm.Send([x, MPI.FLOAT], 2, 0)
elif rank == 2:
    i = array.array('i', [0]*5)
    x = array.array('f', [0]*5)
    status = MPI.Status()
    for j in range(2):
        comm.Probe(MPI.ANY_SOURCE, 0, status)
        if status.Get_source() == 0:
            comm.Recv([i, MPI.INT], 0, 0, status)
        else:
            comm.Recv([x, MPI.FLOAT], 1, 0, status)

# --------------------------------------------------------------------

if rank == 2:
    for v in i: assert v == 7
    for v in x: assert v == 7
    assert status.source in (0, 1)
    assert status.tag == 0
    assert status.error == 0

# --------------------------------------------------------------------
