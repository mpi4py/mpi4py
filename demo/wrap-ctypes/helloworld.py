from mpi4py import MPI
import ctypes
import os

_libdir = os.path.dirname(__file__)

if MPI._sizeof(MPI.Comm) == ctypes.sizeof(ctypes.c_int):
    MPI_Comm = ctypes.c_int
else:
    MPI_Comm = ctypes.c_void_p
lib = ctypes.CDLL(os.path.join(_libdir, "libhelloworld.so"))
lib.sayhello.restype = None
lib.sayhello.argtypes = [MPI_Comm]

def sayhello(comm):
    comm_c = MPI_Comm(comm.handle)
    lib.sayhello(comm_c)
