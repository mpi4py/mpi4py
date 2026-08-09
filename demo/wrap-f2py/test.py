import helloworld as hw

from mpi4py import MPI

null = MPI.COMM_NULL
fnull = null.py2f()
hw.sayhello(fnull)  # ty:ignore[invalid-argument-type]

comm = MPI.COMM_WORLD
fcomm = comm.py2f()
hw.sayhello(fcomm)  # ty:ignore[invalid-argument-type]

try:
    hw.sayhello(None)  # ty:ignore[invalid-argument-type]
except (AttributeError, TypeError):
    pass
else:
    assert 0, "exception not raised"
