from mpi4py import MPI
import ctypes
import os

_libdir = os.path.dirname(__file__)

MPI_Fint = ctypes.c_int

class MPI_Comm(ctypes.Structure):
    _fields_ = [("mpi_val", MPI_Fint)]

lib = ctypes.CDLL(os.path.join(_libdir, "libhelloworld.so"))
lib.sayhello.restype = None
lib.sayhello.argtypes = [ctypes.POINTER(MPI_Comm)]

def sayhello(comm):
    comm_f = MPI_Comm(comm.py2f())
    lib.sayhello(comm_f)
