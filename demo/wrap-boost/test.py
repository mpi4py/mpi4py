from mpi4py import MPI
import helloworld as hw

null = MPI.COMM_NULL
hw.sayhello(null)

comm = MPI.COMM_WORLD
hw.sayhello(comm)

try:
    hw.sayhello(list())
except:
    pass
else:
    assert 0, "exception not raised"
