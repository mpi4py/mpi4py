from mpi4py import rc
rc.initialize = False

from mpi4py import MPI
assert not MPI.Is_initialized()
assert not MPI.Is_finalized()

MPI.Init_thread(MPI.THREAD_MULTIPLE)
assert MPI.Is_initialized()
assert not MPI.Is_finalized()

MPI.Finalize()
assert MPI.Is_initialized()
assert MPI.Is_finalized()
