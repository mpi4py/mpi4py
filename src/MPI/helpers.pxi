#---------------------------------------------------------------------

cdef enum PyMPI_OBJECT_FLAGS:
    PyMPI_SKIP_FREE = 1<<1

#---------------------------------------------------------------------
# Status

cdef inline MPI_Status *_arg_Status(object status):
    if status is None: return MPI_STATUS_IGNORE
    return &((<Status?>status).ob_mpi)

#---------------------------------------------------------------------
# Datatype

cdef inline Datatype _new_Datatype(MPI_Datatype ob):
    cdef Datatype datatype = Datatype()
    datatype.ob_mpi = ob
    if ob != MPI_DATATYPE_NULL:
        datatype.flags |= PyMPI_SKIP_FREE
    return datatype

cdef inline int _del_Datatype(MPI_Datatype* ob):
    #
    if ob    == NULL              : return 0
    if ob[0] == MPI_DATATYPE_NULL : return 0
    if not _mpi_active()          : return 0
    #
    return MPI_Type_free(ob)

cdef inline int _named_Datatype(MPI_Datatype ob):
    if ob == MPI_DATATYPE_NULL: return 0
    cdef int ni = 0, na = 0, nt = 0, combiner = MPI_UNDEFINED
    cdef int ierr = 0
    ierr = MPI_Type_get_envelope(ob, &ni, &na, &nt, &combiner)
    if ierr: return 0 # XXX
    return combiner == MPI_COMBINER_NAMED

cdef void _fix_Datatype(Datatype datatype):
    cdef MPI_Datatype ob = datatype.ob_mpi
    if ob == MPI_DATATYPE_NULL: return
    if _named_Datatype(ob):
        datatype.flags |= PyMPI_SKIP_FREE

#---------------------------------------------------------------------
# Request

include "reqimpl.pxi"

cdef inline Request _new_Request(MPI_Request ob):
    cdef Request request = Request()
    request.ob_mpi = ob
    return request

cdef inline int _del_Request(MPI_Request* ob):
    #
    if ob    == NULL             : return 0
    if ob[0] == MPI_REQUEST_NULL : return 0
    if not _mpi_active()         : return 0
    #
    return MPI_Request_free(ob)

#---------------------------------------------------------------------
# Op

include "opimpl.pxi"

cdef inline Op _new_Op(MPI_Op ob):
    cdef Op op = Op()
    op.ob_mpi = ob
    if   ob == MPI_OP_NULL : op.op_fun = NULL
    elif ob == MPI_MAX     : op.op_fun = _op_MAX
    elif ob == MPI_MIN     : op.op_fun = _op_MIN
    elif ob == MPI_SUM     : op.op_fun = _op_SUM
    elif ob == MPI_PROD    : op.op_fun = _op_PROD
    elif ob == MPI_LAND    : op.op_fun = _op_LAND
    elif ob == MPI_BAND    : op.op_fun = _op_BAND
    elif ob == MPI_LOR     : op.op_fun = _op_LOR
    elif ob == MPI_BOR     : op.op_fun = _op_BOR
    elif ob == MPI_LXOR    : op.op_fun = _op_LXOR
    elif ob == MPI_BXOR    : op.op_fun = _op_BXOR
    elif ob == MPI_MAXLOC  : op.op_fun = _op_MAXLOC
    elif ob == MPI_MINLOC  : op.op_fun = _op_MINLOC
    elif ob == MPI_REPLACE : op.op_fun = _op_REPLACE
    return op

cdef inline int _del_Op(MPI_Op* ob):
    #
    if ob    == NULL        : return 0
    if ob[0] == MPI_OP_NULL : return 0
    if ob[0] == MPI_MAX     : return 0
    if ob[0] == MPI_MIN     : return 0
    if ob[0] == MPI_SUM     : return 0
    if ob[0] == MPI_PROD    : return 0
    if ob[0] == MPI_LAND    : return 0
    if ob[0] == MPI_BAND    : return 0
    if ob[0] == MPI_LOR     : return 0
    if ob[0] == MPI_BOR     : return 0
    if ob[0] == MPI_LXOR    : return 0
    if ob[0] == MPI_BXOR    : return 0
    if ob[0] == MPI_MAXLOC  : return 0
    if ob[0] == MPI_MINLOC  : return 0
    if ob[0] == MPI_REPLACE : return 0
    if not _mpi_active()    : return 0
    #
    return MPI_Op_free(ob)

#---------------------------------------------------------------------
# Info

cdef inline Info _new_Info(MPI_Info ob):
    cdef Info info = Info()
    info.ob_mpi = ob
    return info

cdef inline int _del_Info(MPI_Info* ob):
    #
    if ob    == NULL          : return 0
    if ob[0] == MPI_INFO_NULL : return 0
    if not _mpi_active()      : return 0
    #
    return MPI_Info_free(ob)

cdef inline MPI_Info _arg_Info(object info):
    if info is None: return MPI_INFO_NULL
    return (<Info?>info).ob_mpi

#---------------------------------------------------------------------
# Group

cdef inline Group _new_Group(MPI_Group ob):
     cdef Group group = Group()
     group.ob_mpi = ob
     if ob != MPI_GROUP_NULL:
         group.flags |= PyMPI_SKIP_FREE
     return group


cdef inline int _del_Group(MPI_Group* ob):
     #
     if ob    == NULL            : return 0
     if ob[0] == MPI_GROUP_NULL  : return 0
     if ob[0] == MPI_GROUP_EMPTY : return 0
     if not _mpi_active()        : return 0
     #
     return MPI_Group_free(ob)

#---------------------------------------------------------------------
# Comm

cdef inline Comm _new_Comm(MPI_Comm ob):
    cdef Comm comm = Comm()
    comm.ob_mpi = ob
    return comm

cdef inline Intracomm _new_Intracomm(MPI_Comm ob):
    cdef Intracomm comm = Intracomm()
    comm.ob_mpi = ob
    return comm

cdef inline Intercomm _new_Intercomm(MPI_Comm ob):
    cdef Intercomm comm = Intercomm()
    comm.ob_mpi = ob
    return comm

cdef inline int _del_Comm(MPI_Comm* ob):
    #
    if ob    == NULL           : return 0
    if ob[0] == MPI_COMM_NULL  : return 0
    if ob[0] == MPI_COMM_SELF  : return 0
    if ob[0] == MPI_COMM_WORLD : return 0
    if not _mpi_active()       : return 0
    #
    return MPI_Comm_free(ob)

#---------------------------------------------------------------------
# Win

cdef inline Win _new_Win(MPI_Win ob):
    cdef Win win = Win()
    win.ob_mpi = ob
    return win

cdef inline int _del_Win(MPI_Win* ob):
    #
    if ob    == NULL         : return 0
    if ob[0] == MPI_WIN_NULL : return 0
    if not _mpi_active()     : return 0
    #
    return MPI_Win_free(ob)

#---------------------------------------------------------------------
# File

cdef inline File _new_File(MPI_File ob):
    cdef File file = File()
    file.ob_mpi = ob
    return file

cdef inline int _del_File(MPI_File* ob):
    #
    if ob    == NULL          : return 0
    if ob[0] == MPI_FILE_NULL : return 0
    if not _mpi_active()      : return 0
    #
    return MPI_File_close(ob)

#---------------------------------------------------------------------
# Errhandler

cdef inline Errhandler _new_Errhandler(MPI_Errhandler ob):
    cdef Errhandler errhandler = Errhandler()
    errhandler.ob_mpi = ob
    if ob != MPI_ERRHANDLER_NULL:
        errhandler.flags |= PyMPI_SKIP_FREE
    return errhandler

cdef inline int _del_Errhandler(MPI_Errhandler* ob):
    #
    if ob    == NULL                : return 0
    if ob[0] == MPI_ERRHANDLER_NULL : return 0
    if not _mpi_active()            : return 0
    #
    return MPI_Errhandler_free(ob)

#---------------------------------------------------------------------
