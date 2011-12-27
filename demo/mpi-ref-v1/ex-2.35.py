## mpiexec -n 1 python ex-2.35.py

# Calls to attach and detach buffers

# --------------------------------------------------------------------

from mpi4py import MPI
try:
    from numpy import empty
except ImportError:
    from array import array
    def empty(size, dtype):
        return array(dtype, [0]*size)

# --------------------------------------------------------------------

BUFSISE = 10000 + MPI.BSEND_OVERHEAD

buff = empty(BUFSISE, dtype='b')

MPI.Attach_buffer(buff)

buff2 = MPI.Detach_buffer()

MPI.Attach_buffer(buff2)

MPI.Detach_buffer()


# --------------------------------------------------------------------

assert len(buff2) == BUFSISE

# --------------------------------------------------------------------
