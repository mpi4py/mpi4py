import os
from mpi4py import rc

assert rc.initialize   is True
assert rc.finalize     is None
assert rc.thread_level == 'multiple'

os.environ['MPI4PY_RC_INITIALIZE']   = 'false'
os.environ['MPI4PY_RC_FINALIZE']     = 'off'
os.environ['MPI4PY_RC_THREAD_LEVEL'] = 'single'

from mpi4py import MPI
assert not MPI.Is_initialized()
assert not MPI.Is_finalized()

assert rc.initialize   is False
assert rc.finalize     is False
assert rc.thread_level == 'single'
