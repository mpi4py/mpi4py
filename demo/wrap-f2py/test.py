import helloworld as hw

from mpi4py import MPI

null = MPI.COMM_NULL
fnull = null.py2f()
hw.sayhello(fnull)

comm = MPI.COMM_WORLD
fcomm = comm.py2f()
hw.sayhello(fcomm)

try:
    hw.sayhello(None)
except (AttributeError, TypeError):
    pass
else:
    assert 0, "exception not raised"
