# -----------------------------------------------------------------------------

#  Datatype

cdef api object PyMPIDatatype_New(MPI_Datatype arg):
    cdef Datatype obj = Datatype.__new__(Datatype)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Datatype* PyMPIDatatype_Get(object arg) except NULL:
    return &(<Datatype?>arg).ob_mpi

# -----------------------------------------------------------------------------

#  Status

cdef api object PyMPIStatus_New(MPI_Status *arg):
    cdef Status obj = Status.__new__(Status)
    if (arg != NULL and
        arg != MPI_STATUS_IGNORE and
        arg != MPI_STATUSES_IGNORE):
        obj.ob_mpi = arg[0]
    return obj

cdef api MPI_Status* PyMPIStatus_Get(object arg) except? NULL:
    if arg is None: return MPI_STATUS_IGNORE
    return &(<Status?>arg).ob_mpi

# -----------------------------------------------------------------------------

#  Request

cdef api object PyMPIRequest_New(MPI_Request arg):
    cdef Request obj = Request.__new__(Request)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api object PyMPIPrequest_New(MPI_Request arg):
    cdef Prequest obj = Prequest.__new__(Prequest)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api object PyMPIGrequest_New(MPI_Request arg):
    cdef Grequest obj = Grequest.__new__(Grequest)
    obj.ob_grequest = arg
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Request* PyMPIRequest_Get(object arg) except NULL:
    return &(<Request?>arg).ob_mpi

# -----------------------------------------------------------------------------

#  Message

cdef api object PyMPIMessage_New(MPI_Message arg):
    cdef Message obj = Message.__new__(Message)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Message* PyMPIMessage_Get(object arg) except NULL:
    return &(<Message?>arg).ob_mpi

# -----------------------------------------------------------------------------

#  Op

cdef api object PyMPIOp_New(MPI_Op arg):
    cdef Op obj = Op.__new__(Op)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Op* PyMPIOp_Get(object arg) except NULL:
    return &(<Op?>arg).ob_mpi

# -----------------------------------------------------------------------------

#  Group

cdef api object PyMPIGroup_New(MPI_Group arg):
    cdef Group obj = Group.__new__(Group)
    obj.ob_mpi = arg
    return obj

cdef api MPI_Group* PyMPIGroup_Get(object arg) except NULL:
    return &(<Group?>arg).ob_mpi

# -----------------------------------------------------------------------------

#  Info

cdef api object PyMPIInfo_New(MPI_Info arg):
    cdef Info obj = Info.__new__(Info)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Info* PyMPIInfo_Get(object arg) except NULL:
    return &(<Info?>arg).ob_mpi

# -----------------------------------------------------------------------------

# Errhandler

cdef api object PyMPIErrhandler_New(MPI_Errhandler arg):
    cdef Errhandler obj = Errhandler.__new__(Errhandler)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Errhandler* PyMPIErrhandler_Get(object arg) except NULL:
    return &(<Errhandler?>arg).ob_mpi

# -----------------------------------------------------------------------------

# Session

cdef api object PyMPISession_New(MPI_Session arg):
    cdef Session obj = Session.__new__(Session)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Session* PyMPISession_Get(object arg) except NULL:
    return &(<Session?>arg).ob_mpi

# -----------------------------------------------------------------------------

# Comm

cdef api object PyMPIComm_New(MPI_Comm arg):
    cdef type cls = CommType(arg)
    cdef Comm obj = <Comm>cls.__new__(cls)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Comm* PyMPIComm_Get(object arg) except NULL:
    return &(<Comm?>arg).ob_mpi

# -----------------------------------------------------------------------------

# Win

cdef api object PyMPIWin_New(MPI_Win arg):
    cdef Win obj = Win.__new__(Win)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_Win* PyMPIWin_Get(object arg) except NULL:
    return &(<Win?>arg).ob_mpi

# -----------------------------------------------------------------------------

# File

cdef api object PyMPIFile_New(MPI_File arg):
    cdef File obj = File.__new__(File)
    obj.ob_mpi = arg
    obj.flags |= 0
    return obj

cdef api MPI_File* PyMPIFile_Get(object arg) except NULL:
    return &(<File?>arg).ob_mpi

# -----------------------------------------------------------------------------
