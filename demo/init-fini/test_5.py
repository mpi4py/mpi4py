from mpi4py import rc
del rc.initialize
del rc.threaded
del rc.thread_level
del rc.finalize

from mpi4py import MPI
assert MPI.Is_initialized()
assert not MPI.Is_finalized()

import sys
name, _ = MPI.get_vendor()
if name == 'MPICH2' and sys.platform[:3]!='win':
    assert MPI.Query_thread() == MPI.THREAD_MULTIPLE
