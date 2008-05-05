## mpiexec -n 1 python ex-2.35.py

# Calls to attach and detach buffers

# --------------------------------------------------------------------

import mpi4py.MPI as MPI
import numpy

# --------------------------------------------------------------------

BUFSISE = 10000

buff = numpy.empty(BUFSISE, dtype='b')

MPI.Attach_buffer(buff)

buff2 = MPI.Detach_buffer()

MPI.Attach_buffer(buff2)

MPI.Detach_buffer()


# --------------------------------------------------------------------

assert len(buff2) == BUFSISE

# --------------------------------------------------------------------
