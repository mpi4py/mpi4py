from mpi4py import MPI
import ctypes
import os

_libdir = os.path.dirname(__file__)

if MPI._sizeof(MPI.Comm) == ctypes.sizeof(ctypes.c_int):
    MPI_Comm = ctypes.c_int
else:
    MPI_Comm = ctypes.c_void_p
_lib = ctypes.CDLL(os.path.join(_libdir, "libhelloworld.so"))
_lib.sayhello.restype = None
_lib.sayhello.argtypes = [MPI_Comm]

def sayhello(comm):
    comm_ptr = MPI._addressof(comm)
    comm_val = MPI_Comm.from_address(comm_ptr)
    _lib.sayhello(comm_val)
