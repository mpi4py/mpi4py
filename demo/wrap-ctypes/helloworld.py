from os import path as _pth
import ctypes as _ctypes
from mpi4py import MPI

_libdir = _pth.dirname(__file__)

_lib = _ctypes.CDLL(_pth.join(_libdir, "libhelloworld.so"))
_lib.sayhello.restype = None
_lib.sayhello.argtypes = [_ctypes.c_void_p]

def sayhello(comm):
    address = MPI._addressof(comm)
    comm_ptr = _ctypes.c_void_p(address)
    _lib.sayhello(comm_ptr)
