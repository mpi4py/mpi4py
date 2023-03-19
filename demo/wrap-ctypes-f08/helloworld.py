from mpi4py import MPI
import ctypes
import os

_libdir = os.path.dirname(__file__)

MPI_Fint = ctypes.c_int

class MPI_Comm(ctypes.Structure):
    _fields_ = [("mpi_val", MPI_Fint)]

_lib = ctypes.CDLL(os.path.join(_libdir, "libhelloworld.so"))
_lib.sayhello.restype = None
_lib.sayhello.argtypes = [ctypes.POINTER(MPI_Comm)]

def sayhello(comm):
    fcomm = MPI_Comm(comm.py2f())
    _lib.sayhello(fcomm)
