from mpi4py import MPI
import ctypes
import os

_libdir = os.path.dirname(__file__)

MPI_Fint = ctypes.c_int
_lib = ctypes.CDLL(os.path.join(_libdir, "libhelloworld.so"))
_lib.sayhello_.restype = None
_lib.sayhello_.argtypes = [ctypes.POINTER(MPI_Fint)]

def sayhello(comm):
    fcomm = MPI_Fint(comm.py2f())
    _lib.sayhello_(fcomm)
