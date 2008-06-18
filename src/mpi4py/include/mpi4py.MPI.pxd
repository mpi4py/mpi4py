# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
# Id:      $Id$


cdef extern from "mpi.h":

    ctypedef long      MPI_Aint
    ctypedef long long MPI_Offset

    ctypedef struct MPI_Status:
        int MPI_SOURCE
        int MPI_TAG
        int MPI_ERROR

    ctypedef struct _mpi_datatype_t
    ctypedef _mpi_datatype_t* MPI_Datatype

    ctypedef struct _mpi_request_t
    ctypedef _mpi_request_t* MPI_Request

    ctypedef struct _mpi_op_t
    ctypedef _mpi_op_t* MPI_Op

    ctypedef struct _mpi_group_t
    ctypedef _mpi_group_t* MPI_Group

    ctypedef struct _mpi_info_t
    ctypedef _mpi_info_t* MPI_Info

    ctypedef struct _mpi_errhandler_t
    ctypedef _mpi_errhandler_t* MPI_Errhandler

    cdef struct _mpi_comm_t
    ctypedef _mpi_comm_t* MPI_Comm

    ctypedef struct _mpi_win_t
    ctypedef _mpi_win_t* MPI_Win

    ctypedef struct _mpi_file_t
    ctypedef _mpi_file_t* MPI_File


cdef extern from "mpi4py/mpi4py.h":

    ctypedef class mpi4py.MPI.Status [object PyMPIStatusObject]:
        cdef MPI_Status ob_mpi, status "ob_mpi"

    ctypedef class mpi4py.MPI.Datatype [object PyMPIDatatypeObject]:
        cdef MPI_Datatype ob_mpi, datatype "ob_mpi"

    ctypedef class mpi4py.MPI.Request [object PyMPIRequestObject]:
        cdef MPI_Request ob_mpi, request "ob_mpi"

    ctypedef class mpi4py.MPI.Prequest(Request) [object PyMPIPrequestObject]:
        pass

    ctypedef class mpi4py.MPI.Grequest(Request) [object PyMPIGrequestObject]:
        pass

    ctypedef class mpi4py.MPI.Op [object PyMPIOpObject]:
        cdef MPI_Op ob_mpi, op "ob_mpi"

    ctypedef class mpi4py.MPI.Group [object PyMPIGroupObject]:
        cdef MPI_Group ob_mpi, group "ob_mpi"

    ctypedef class mpi4py.MPI.Info [object PyMPIInfoObject]:
        cdef MPI_Info ob_mpi, info "ob_mpi"

    ctypedef class mpi4py.MPI.Errhandler [object PyMPIErrhandlerObject]:
        cdef MPI_Errhandler ob_mpi, errhandler "ob_mpi"

    ctypedef class mpi4py.MPI.Comm [object PyMPICommObject]:
        cdef MPI_Comm ob_mpi, comm "ob_mpi"

    ctypedef class mpi4py.MPI.Intracomm(Comm) [object PyMPIIntracommObject]:
        pass

    ctypedef class mpi4py.MPI.Cartcomm(Intracomm) [object PyMPICartcommObject]:
        pass

    ctypedef class mpi4py.MPI.Graphcomm(Intracomm) [object PyMPIGraphcommObject]:
        pass

    ctypedef class mpi4py.MPI.Intercomm(Comm) [object PyMPIIntercommObject]:
        pass

    ctypedef class mpi4py.MPI.Win [object PyMPIWinObject]:
        cdef MPI_Win ob_mpi, win "ob_mpi"

    ctypedef class mpi4py.MPI.File [object PyMPIFileObject]:
        cdef MPI_File ob_mpi, file "ob_mpi"
