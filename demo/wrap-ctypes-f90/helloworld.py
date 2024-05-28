from mpi4py import MPI
import ctypes
import os

_libdir = os.path.dirname(__file__)

MPI_Fint = ctypes.c_int
lib = ctypes.CDLL(os.path.join(_libdir, "libhelloworld.so"))
lib.sayhello_.restype = None
lib.sayhello_.argtypes = [ctypes.POINTER(MPI_Fint)]

def sayhello(comm):
    comm_f = MPI_Fint(comm.py2f())
    lib.sayhello_(comm_f)
