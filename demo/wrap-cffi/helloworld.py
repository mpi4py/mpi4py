from mpi4py import MPI
import cffi
import os

_libdir = os.path.dirname(__file__)

ffi = cffi.FFI()
if MPI._sizeof(MPI.Comm) == ffi.sizeof('int'):
    _mpi_comm_t = 'int'
else:
    _mpi_comm_t = 'void*'
ffi.cdef("""
typedef %(_mpi_comm_t)s MPI_Comm;
void sayhello(MPI_Comm);
""" % vars())
lib = ffi.dlopen(os.path.join(_libdir, "libhelloworld.so"))

def sayhello(comm):
    comm_ptr = MPI._addressof(comm)
    comm_val = ffi.cast('MPI_Comm*', comm_ptr)[0]
    lib.sayhello(comm_val)
