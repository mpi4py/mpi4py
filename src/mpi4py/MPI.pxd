# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
# Id:      $Id$

# --

include "mpi.pxi"

# --

ctypedef MPI_Aint   Aint
ctypedef MPI_Offset Offset

cdef class Status:
    cdef MPI_Status ob_mpi
    cdef int flags

cdef class Datatype:
    cdef MPI_Datatype ob_mpi
    cdef int flags

cdef class Request:
    cdef MPI_Request ob_mpi
    cdef int flags

cdef class Prequest(Request):
    pass

cdef class Grequest(Request):
    pass

cdef class Op:
    cdef MPI_Op ob_mpi
    cdef int flags
    cdef object (*op_fun)(object, object)
    cdef bint   __commute
    cdef object __callable

cdef class Group:
    cdef MPI_Group ob_mpi
    cdef int flags

cdef class Info:
    cdef MPI_Info ob_mpi
    cdef int flags

cdef class Errhandler:
    cdef MPI_Errhandler ob_mpi
    cdef int flags

cdef class Comm:
    cdef MPI_Comm ob_mpi
    cdef int flags

cdef class Intracomm(Comm):
    pass

cdef class Cartcomm(Intracomm):
    pass

cdef class Graphcomm(Intracomm):
    pass

cdef class Intercomm(Comm):
    pass

cdef class Win:
    cdef MPI_Win ob_mpi
    cdef int flags
    cdef object __memory

cdef class File:
    cdef MPI_File ob_mpi
    cdef int flags

# --
