cdef extern from "mpi-compat.h": pass

cimport mpi4py.MPI as MPI
from mpi4py.libmpi cimport *

cdef extern from "stdio.h":
    int printf(char*, ...)

cdef void c_sayhello(MPI_Comm comm):
    cdef int size, rank, plen
    cdef char pname[MPI_MAX_PROCESSOR_NAME]
    if comm == MPI_COMM_NULL:
        printf(b"You passed MPI_COMM_NULL !!!%s", b"\n")
        return
    MPI_Comm_size(comm, &size)
    MPI_Comm_rank(comm, &rank)
    MPI_Get_processor_name(pname, &plen)
    printf(b"Hello, World! I am process %d of %d on %s.\n",
           rank, size, pname)

def sayhello(MPI.Comm comm not None ):
    cdef MPI_Comm c_comm = comm.ob_mpi
    c_sayhello(c_comm)
