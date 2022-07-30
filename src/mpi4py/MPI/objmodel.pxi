#------------------------------------------------------------------------------

ctypedef fused handle_t:
    MPI_Datatype
    MPI_Request
    MPI_Message
    MPI_Op
    MPI_Group
    MPI_Info
    MPI_Errhandler
    MPI_Session
    MPI_Comm
    MPI_Win
    MPI_File

cdef inline int named_Datatype(MPI_Datatype arg) nogil:
    if arg == MPI_DATATYPE_NULL           : return 1
    if arg == MPI_PACKED                  : return 1
    if arg == MPI_BYTE                    : return 1
    if arg == MPI_AINT                    : return 1
    if arg == MPI_OFFSET                  : return 1
    if arg == MPI_COUNT                   : return 1
    if arg == MPI_CHAR                    : return 1
    if arg == MPI_WCHAR                   : return 1
    if arg == MPI_SIGNED_CHAR             : return 1
    if arg == MPI_SHORT                   : return 1
    if arg == MPI_INT                     : return 1
    if arg == MPI_LONG                    : return 1
    if arg == MPI_LONG_LONG               : return 1
    if arg == MPI_UNSIGNED_CHAR           : return 1
    if arg == MPI_UNSIGNED_SHORT          : return 1
    if arg == MPI_UNSIGNED                : return 1
    if arg == MPI_UNSIGNED_LONG           : return 1
    if arg == MPI_UNSIGNED_LONG_LONG      : return 1
    if arg == MPI_FLOAT                   : return 1
    if arg == MPI_DOUBLE                  : return 1
    if arg == MPI_LONG_DOUBLE             : return 1
    if arg == MPI_C_BOOL                  : return 1
    if arg == MPI_INT8_T                  : return 1
    if arg == MPI_INT16_T                 : return 1
    if arg == MPI_INT32_T                 : return 1
    if arg == MPI_INT64_T                 : return 1
    if arg == MPI_UINT8_T                 : return 1
    if arg == MPI_UINT16_T                : return 1
    if arg == MPI_UINT32_T                : return 1
    if arg == MPI_UINT64_T                : return 1
    if arg == MPI_C_COMPLEX               : return 1
    if arg == MPI_C_FLOAT_COMPLEX         : return 1
    if arg == MPI_C_DOUBLE_COMPLEX        : return 1
    if arg == MPI_C_LONG_DOUBLE_COMPLEX   : return 1
    if arg == MPI_CXX_BOOL                : return 1
    if arg == MPI_CXX_FLOAT_COMPLEX       : return 1
    if arg == MPI_CXX_DOUBLE_COMPLEX      : return 1
    if arg == MPI_CXX_LONG_DOUBLE_COMPLEX : return 1
    if arg == MPI_SHORT_INT               : return 1
    if arg == MPI_2INT                    : return 1
    if arg == MPI_LONG_INT                : return 1
    if arg == MPI_FLOAT_INT               : return 1
    if arg == MPI_DOUBLE_INT              : return 1
    if arg == MPI_LONG_DOUBLE_INT         : return 1
    if arg == MPI_CHARACTER               : return 1
    if arg == MPI_LOGICAL                 : return 1
    if arg == MPI_INTEGER                 : return 1
    if arg == MPI_REAL                    : return 1
    if arg == MPI_DOUBLE_PRECISION        : return 1
    if arg == MPI_COMPLEX                 : return 1
    if arg == MPI_DOUBLE_COMPLEX          : return 1
    if arg == MPI_LOGICAL1                : return 1
    if arg == MPI_LOGICAL2                : return 1
    if arg == MPI_LOGICAL4                : return 1
    if arg == MPI_LOGICAL8                : return 1
    if arg == MPI_INTEGER1                : return 1
    if arg == MPI_INTEGER2                : return 1
    if arg == MPI_INTEGER4                : return 1
    if arg == MPI_INTEGER8                : return 1
    if arg == MPI_INTEGER16               : return 1
    if arg == MPI_REAL2                   : return 1
    if arg == MPI_REAL4                   : return 1
    if arg == MPI_REAL8                   : return 1
    if arg == MPI_REAL16                  : return 1
    if arg == MPI_COMPLEX4                : return 1
    if arg == MPI_COMPLEX8                : return 1
    if arg == MPI_COMPLEX16               : return 1
    if arg == MPI_COMPLEX32               : return 1
    return 0

cdef inline int predef_Datatype(MPI_Datatype arg) nogil:
    if named_Datatype(arg): return 1
    cdef MPI_Count ni = 0, na = 0, nc = 0, nd = 0
    cdef int combiner = MPI_UNDEFINED
    cdef int ierr = MPI_Type_get_envelope_c(
        arg, &ni, &na, &nc, &nd, &combiner)
    if ierr != MPI_SUCCESS: return 0 # XXX Error?
    return (
        combiner == MPI_COMBINER_NAMED       or
        combiner == MPI_COMBINER_F90_INTEGER or
        combiner == MPI_COMBINER_F90_REAL    or
        combiner == MPI_COMBINER_F90_COMPLEX
    )

cdef inline int predef_Request(MPI_Request arg) nogil:
    if arg == MPI_REQUEST_NULL : return 1
    return 0

cdef inline int predef_Message(MPI_Message arg) nogil:
    if arg == MPI_MESSAGE_NULL    : return 1
    if arg == MPI_MESSAGE_NO_PROC : return 1
    return 0

cdef inline int predef_Op(MPI_Op arg) nogil:
    if arg == MPI_OP_NULL : return 1
    if arg == MPI_MAX     : return 1
    if arg == MPI_MIN     : return 1
    if arg == MPI_SUM     : return 1
    if arg == MPI_PROD    : return 1
    if arg == MPI_LAND    : return 1
    if arg == MPI_BAND    : return 1
    if arg == MPI_LOR     : return 1
    if arg == MPI_BOR     : return 1
    if arg == MPI_LXOR    : return 1
    if arg == MPI_BXOR    : return 1
    if arg == MPI_MAXLOC  : return 1
    if arg == MPI_MINLOC  : return 1
    if arg == MPI_REPLACE : return 1
    if arg == MPI_NO_OP   : return 1
    return 0

cdef inline int predef_Group(MPI_Group arg) nogil:
    if arg == MPI_GROUP_NULL  : return 1
    if arg == MPI_GROUP_EMPTY : return 1
    return 0

cdef inline int predef_Info(MPI_Info arg) nogil:
    if arg == MPI_INFO_NULL : return 1
    if arg == MPI_INFO_ENV  : return 1
    return 0

cdef inline int predef_Errhandler(MPI_Errhandler arg) nogil:
    if arg == MPI_ERRHANDLER_NULL  : return 1
    if arg == MPI_ERRORS_RETURN    : return 1
    if arg == MPI_ERRORS_ABORT     : return 1
    if arg == MPI_ERRORS_ARE_FATAL : return 1
    return 0

cdef inline int predef_Session(MPI_Session arg) nogil:
    if arg == MPI_SESSION_NULL : return 1
    return 0

cdef inline int predef_Comm(MPI_Comm arg) nogil:
    if arg == MPI_COMM_NULL  : return 1
    if arg == MPI_COMM_SELF  : return 1
    if arg == MPI_COMM_WORLD : return 1
    return 0

cdef inline int predef_Win(MPI_Win arg) nogil:
    if arg == MPI_WIN_NULL : return 1
    return 0

cdef inline int predef_File(MPI_File arg) nogil:
    if arg == MPI_FILE_NULL : return 1
    return 0

cdef inline int predefined(handle_t arg) nogil:
    cdef int result = 0
    if handle_t is MPI_Datatype   : result = predef_Datatype(arg)
    if handle_t is MPI_Request    : result = predef_Request(arg)
    if handle_t is MPI_Message    : result = predef_Message(arg)
    if handle_t is MPI_Op         : result = predef_Op(arg)
    if handle_t is MPI_Group      : result = predef_Group(arg)
    if handle_t is MPI_Info       : result = predef_Info(arg)
    if handle_t is MPI_Errhandler : result = predef_Errhandler(arg)
    if handle_t is MPI_Session    : result = predef_Session(arg)
    if handle_t is MPI_Comm       : result = predef_Comm(arg)
    if handle_t is MPI_Win        : result = predef_Win(arg)
    if handle_t is MPI_File       : result = predef_File(arg)
    return result

#------------------------------------------------------------------------------

ctypedef fused PyMPIClass:
    Datatype
    Request
    Message
    Op
    Group
    Info
    Errhandler
    Session
    Comm
    Win
    File

cdef extern from *:
    """
    #define PyMPI_FLAGS_READY   (1U<<0)
    #define PyMPI_FLAGS_CONST   (1U<<1)
    """
    enum: PyMPI_FLAGS_READY
    enum: PyMPI_FLAGS_CONST

cdef inline int cinit(PyMPIClass self, PyMPIClass arg) except -1:
    self.flags |= PyMPI_FLAGS_READY
    if arg is None: return 0
    self.ob_mpi = arg.ob_mpi
    if PyMPIClass is Request:
        self.ob_buf = arg.ob_buf
    if PyMPIClass is Message:
        self.ob_buf = arg.ob_buf
    if PyMPIClass is Op:
        self.ob_func = arg.ob_func
        self.ob_usrid = arg.ob_usrid
    if PyMPIClass is Win:
        self.ob_mem = arg.ob_mem
    return 0

cdef inline int dealloc(PyMPIClass self) except -1:
    if not (self.flags & PyMPI_FLAGS_READY): return 0
    if (self.flags & PyMPI_FLAGS_CONST): return 0
    if self.flags: return 0 # TODO: this always return
    if not mpi_active(): return 0
    if predefined(self.ob_mpi): return 0

    cdef str mod = type(self).__module__
    cdef str cls = type(self).__name__
    PyErr_WarnFormat(
        RuntimeWarning, 1,
        b"collecting %.200U.%.200U object with MPI handle %p",
        <PyObject*> mod, <PyObject*> cls,
        <void*> <Py_uintptr_t> self.ob_mpi,
    )

cdef extern from "Python.h":
    enum: Py_LT
    enum: Py_LE
    enum: Py_EQ
    enum: Py_NE
    enum: Py_GT
    enum: Py_GE

cdef inline object richcmp(PyMPIClass self, object other, int op):
    if op == Py_EQ: return (self.ob_mpi == (<PyMPIClass>other).ob_mpi)
    if op == Py_NE: return (self.ob_mpi != (<PyMPIClass>other).ob_mpi)
    cdef str mod = type(self).__module__
    cdef str cls = type(self).__name__
    raise TypeError(f"unorderable type '{mod}.{cls}'")

#------------------------------------------------------------------------------

# Status

cdef extern from * nogil:
    int PyMPI_Status_get_source(MPI_Status*, int*)
    int PyMPI_Status_set_source(MPI_Status*, int)
    int PyMPI_Status_get_tag(MPI_Status*, int*)
    int PyMPI_Status_set_tag(MPI_Status*, int)
    int PyMPI_Status_get_error(MPI_Status*, int*)
    int PyMPI_Status_set_error(MPI_Status*, int)

cdef inline MPI_Status *arg_Status(object status) except *:
    if status is None: return MPI_STATUS_IGNORE
    return &((<Status?>status).ob_mpi)

#------------------------------------------------------------------------------

# Datatype

cdef inline Datatype def_Datatype(MPI_Datatype arg):
    cdef Datatype obj = Datatype.__new__(Datatype)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

cdef inline Datatype ftn_Datatype(MPI_Datatype arg):
    cdef Datatype obj = Datatype.__new__(Datatype)
    obj.ob_mpi = arg
    return obj

cdef inline Datatype ref_Datatype(MPI_Datatype arg):
    cdef Datatype obj = Datatype.__new__(Datatype)
    obj.ob_mpi = arg
    if not predefined(arg):
        obj.flags |= 0 # TODO
    return obj

#------------------------------------------------------------------------------

# Request

include "reqimpl.pxi"

cdef inline Request def_Request(MPI_Request arg):
    cdef Request obj = Request.__new__(Request)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------

# Message

cdef inline Message def_Message(MPI_Message arg):
    cdef Message obj = Message.__new__(Message)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------

# Op

include "opimpl.pxi"

cdef inline Op def_Op(MPI_Op arg):
    cdef Op obj = Op.__new__(Op)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    if   arg == MPI_OP_NULL : obj.ob_func = NULL
    elif arg == MPI_MAX     : obj.ob_func = _op_MAX
    elif arg == MPI_MIN     : obj.ob_func = _op_MIN
    elif arg == MPI_SUM     : obj.ob_func = _op_SUM
    elif arg == MPI_PROD    : obj.ob_func = _op_PROD
    elif arg == MPI_LAND    : obj.ob_func = _op_LAND
    elif arg == MPI_BAND    : obj.ob_func = _op_BAND
    elif arg == MPI_LOR     : obj.ob_func = _op_LOR
    elif arg == MPI_BOR     : obj.ob_func = _op_BOR
    elif arg == MPI_LXOR    : obj.ob_func = _op_LXOR
    elif arg == MPI_BXOR    : obj.ob_func = _op_BXOR
    elif arg == MPI_MAXLOC  : obj.ob_func = _op_MAXLOC
    elif arg == MPI_MINLOC  : obj.ob_func = _op_MINLOC
    elif arg == MPI_REPLACE : obj.ob_func = _op_REPLACE
    elif arg == MPI_NO_OP   : obj.ob_func = _op_NO_OP
    return obj

#------------------------------------------------------------------------------

# Group

cdef inline Group def_Group(MPI_Group arg):
    cdef Group obj = Group.__new__(Group)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------

# Info

cdef inline Info def_Info(MPI_Info arg):
    cdef Info obj = Info.__new__(Info)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj


cdef inline MPI_Info arg_Info(object obj):
    if obj is None: return MPI_INFO_NULL
    return (<Info>obj).ob_mpi

#------------------------------------------------------------------------------

# Errhandler

cdef inline Errhandler def_Errhandler(MPI_Errhandler arg):
    cdef Errhandler obj = Errhandler.__new__(Errhandler)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

cdef inline MPI_Errhandler arg_Errhandler(object obj) except *:
    if obj is not None: return (<Errhandler?>obj).ob_mpi
    cdef MPI_Errhandler eh_default = MPI_ERRORS_ARE_FATAL
    cdef int opt = options.errors
    if   opt == 0: return eh_default
    elif opt == 1: return MPI_ERRORS_RETURN
    elif opt == 2: return MPI_ERRORS_ABORT
    elif opt == 3: return MPI_ERRORS_ARE_FATAL
    else:          return eh_default

#------------------------------------------------------------------------------

# Session

cdef inline Session def_Session(MPI_Session arg):
    cdef Session obj = Session.__new__(Session)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------

# Comm

include "commimpl.pxi"

cdef inline Comm def_Comm(MPI_Comm arg):
    cdef Comm obj = Comm.__new__(Comm)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

cdef inline Intracomm def_Intracomm(MPI_Comm arg):
    cdef Intracomm obj = Intracomm.__new__(Intracomm)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

cdef inline Intercomm def_Intercomm(MPI_Comm arg):
    cdef Intercomm obj = Intercomm.__new__(Intercomm)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------

# Win

include "winimpl.pxi"

cdef inline Win def_Win(MPI_Win arg):
    cdef Win obj = Win.__new__(Win)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------

# File

include "drepimpl.pxi"

cdef inline File def_File(MPI_File arg):
    cdef File obj = File.__new__(File)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

#------------------------------------------------------------------------------
