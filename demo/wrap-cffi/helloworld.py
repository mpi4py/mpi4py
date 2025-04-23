import pathlib

import cffi

from mpi4py import MPI

_libdir = pathlib.Path(__file__).parent

ffi = cffi.FFI()
if MPI._sizeof(MPI.Comm) == ffi.sizeof("int"):
    MPI_Comm = "int"
else:
    MPI_Comm = "void*"
ffi.cdef(f"""
typedef {MPI_Comm} MPI_Comm;
void sayhello(MPI_Comm);
""")
lib = ffi.dlopen(_libdir / "libhelloworld.so")


def sayhello(comm):
    comm_c = ffi.cast("MPI_Comm", comm.handle)
    lib.sayhello(comm_c)
