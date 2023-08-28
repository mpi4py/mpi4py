import os
from mpi4py import rc

assert rc.initialize   is True
assert rc.finalize     is None
assert rc.threads      is True
assert rc.thread_level == 'multiple'

os.environ['MPI4PY_RC_INITIALIZE']   = 'false'
os.environ['MPI4PY_RC_FINALIZE']     = 'true'
os.environ['MPI4PY_RC_THREADS']      = 'false'
os.environ['MPI4PY_RC_THREAD_LEVEL'] = 'single'

os.environ['MPI4PY_RC_IRECV_BUFSZ'] = str(2048)
os.environ['MPI4PY_PICKLE_PROTOCOL']  =  str(3)
os.environ['MPI4PY_PICKLE_THRESHOLD'] =  str(1024)

from mpi4py import MPI
assert not MPI.Is_initialized()
assert not MPI.Is_finalized()

assert rc.initialize   is False
assert rc.finalize     is True
assert rc.threads      is False
assert rc.thread_level == 'single'

assert rc.irecv_bufsz == 2048
assert MPI.pickle.PROTOCOL == 3
assert MPI.pickle.THRESHOLD == 1024
