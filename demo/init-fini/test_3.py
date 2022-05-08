import os
from mpi4py import rc

assert rc.initialize is True
assert rc.finalize   is None
os.environ['MPI4PY_RC_INITIALIZE'] = 'false'
os.environ['MPI4PY_RC_FINALIZE']   = 'off'
from mpi4py import MPI
assert rc.initialize is False
assert rc.finalize   is False

assert not MPI.Is_initialized()
assert not MPI.Is_finalized()
