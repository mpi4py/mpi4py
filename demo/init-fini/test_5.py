import mpi4py
mpi4py.rc = None

from mpi4py import MPI
assert MPI.Is_initialized()
assert not MPI.Is_finalized()
