import os
import sys

import mpi4py

del mpi4py.rc
del sys.modules["mpi4py.rc"]

os.environ["MPI4PY_RC_ERRORS"] = "exception"

from mpi4py import MPI  # noqa: E402

assert MPI.Is_initialized()
assert not MPI.Is_finalized()
