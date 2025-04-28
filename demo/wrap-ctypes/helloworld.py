import ctypes
import pathlib

from mpi4py import MPI

_libdir = pathlib.Path(__file__).resolve().parent

if MPI._sizeof(MPI.Comm) == ctypes.sizeof(ctypes.c_int):
    MPI_Comm = ctypes.c_int
else:
    MPI_Comm = ctypes.c_void_p

lib = ctypes.CDLL(_libdir / "libhelloworld.so")
lib.sayhello.restype = None
lib.sayhello.argtypes = [MPI_Comm]


def sayhello(comm):
    comm_c = MPI_Comm(comm.handle)
    lib.sayhello(comm_c)
