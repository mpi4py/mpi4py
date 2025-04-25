import helloworld as hw

from mpi4py import MPI

null = MPI.COMM_NULL
hw.sayhello(null)

comm = MPI.COMM_WORLD
hw.sayhello(comm)

try:
    hw.sayhello(None)
except (AttributeError, TypeError):
    pass
else:
    assert 0, "exception not raised"
