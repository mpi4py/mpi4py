import ctypes
import pathlib

_libdir = pathlib.Path(__file__).parent

MPI_Fint = ctypes.c_int
lib = ctypes.CDLL(_libdir / "libhelloworld.so")
lib.sayhello_.restype = None
lib.sayhello_.argtypes = [ctypes.POINTER(MPI_Fint)]


def sayhello(comm):
    comm_f = MPI_Fint(comm.py2f())
    lib.sayhello_(comm_f)
