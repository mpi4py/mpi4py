from mpi4py import rc
del rc.initialize
del rc.threaded
del rc.thread_level
del rc.finalize

from mpi4py import MPI
assert MPI.Is_initialized()
assert not MPI.Is_finalized()

name, _ = MPI.get_vendor()
if name == 'MPICH2':
    assert MPI.Query_thread() == MPI.THREAD_MULTIPLE
