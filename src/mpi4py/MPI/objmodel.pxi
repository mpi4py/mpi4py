# -----------------------------------------------------------------------------

cdef object Lock = None

if PY_VERSION_HEX >= 0x030900F0:
    from _thread import allocate_lock as Lock
else:
    try:                                                 #~> legacy
        from _thread import allocate_lock as Lock        #~> legacy
    except ImportError:                                  #~> legacy
        from _dummy_thread import allocate_lock as Lock  #~> legacy

# -----------------------------------------------------------------------------

cdef inline object New(type cls):
    return cls.__new__(cls)

# -----------------------------------------------------------------------------

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

cdef inline handle_t mpinull(handle_t _) noexcept nogil:
    cdef handle_t null
    if handle_t is MPI_Datatype   : null = MPI_DATATYPE_NULL
    if handle_t is MPI_Request    : null = MPI_REQUEST_NULL
    if handle_t is MPI_Message    : null = MPI_MESSAGE_NULL
    if handle_t is MPI_Op         : null = MPI_OP_NULL
    if handle_t is MPI_Group      : null = MPI_GROUP_NULL
    if handle_t is MPI_Info       : null = MPI_INFO_NULL
    if handle_t is MPI_Errhandler : null = MPI_ERRHANDLER_NULL
    if handle_t is MPI_Session    : null = MPI_SESSION_NULL
    if handle_t is MPI_Comm       : null = MPI_COMM_NULL
    if handle_t is MPI_Win        : null = MPI_WIN_NULL
    if handle_t is MPI_File       : null = MPI_FILE_NULL
    return null

cdef inline int named_Datatype(MPI_Datatype arg) noexcept nogil:
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

cdef inline int predef_Datatype(MPI_Datatype arg) noexcept nogil:
    if named_Datatype(arg): return 1
    cdef MPI_Count ni = 0, na = 0, nc = 0, nd = 0
    cdef int combiner = MPI_UNDEFINED
    cdef int ierr = MPI_Type_get_envelope_c(
        arg, &ni, &na, &nc, &nd, &combiner)
    if ierr != MPI_SUCCESS: return 0 # XXX Error?
    return (
        combiner == MPI_COMBINER_NAMED       or
        combiner == MPI_COMBINER_VALUE_INDEX or
        combiner == MPI_COMBINER_F90_INTEGER or
        combiner == MPI_COMBINER_F90_REAL    or
        combiner == MPI_COMBINER_F90_COMPLEX
    )

cdef inline int predef_Request(MPI_Request arg) noexcept nogil:
    if arg == MPI_REQUEST_NULL : return 1
    return 0

cdef inline int predef_Message(MPI_Message arg) noexcept nogil:
    if arg == MPI_MESSAGE_NULL    : return 1
    if arg == MPI_MESSAGE_NO_PROC : return 1
    return 0

cdef inline int predef_Op(MPI_Op arg) noexcept nogil:
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

cdef inline int predef_Group(MPI_Group arg) noexcept nogil:
    if arg == MPI_GROUP_NULL  : return 1
    if arg == MPI_GROUP_EMPTY : return 1
    return 0

cdef inline int predef_Info(MPI_Info arg) noexcept nogil:
    if arg == MPI_INFO_NULL : return 1
    if arg == MPI_INFO_ENV  : return 1
    return 0

cdef inline int predef_Errhandler(MPI_Errhandler arg) noexcept nogil:
    if arg == MPI_ERRHANDLER_NULL  : return 1
    if arg == MPI_ERRORS_RETURN    : return 1
    if arg == MPI_ERRORS_ABORT     : return 1
    if arg == MPI_ERRORS_ARE_FATAL : return 1
    return 0

cdef inline int predef_Session(MPI_Session arg) noexcept nogil:
    if arg == MPI_SESSION_NULL : return 1
    return 0

cdef inline int predef_Comm(MPI_Comm arg) noexcept nogil:
    if arg == MPI_COMM_NULL  : return 1
    if arg == MPI_COMM_SELF  : return 1
    if arg == MPI_COMM_WORLD : return 1
    return 0

cdef inline int predef_Win(MPI_Win arg) noexcept nogil:
    if arg == MPI_WIN_NULL : return 1
    return 0

cdef inline int predef_File(MPI_File arg) noexcept nogil:
    if arg == MPI_FILE_NULL : return 1
    return 0

cdef inline int predefined(handle_t arg) noexcept nogil:
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

cdef inline int named(handle_t arg) noexcept nogil:
    if handle_t is MPI_Datatype:
        return named_Datatype(arg)
    else:
        return predefined(arg)

# -----------------------------------------------------------------------------

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

cdef extern from * nogil:
    """
    #define PyMPI_FLAGS_READY   (1U<<0)
    #define PyMPI_FLAGS_CONST   (1U<<1)
    #define PyMPI_FLAGS_TEMP    (1U<<2)
    """
    enum: PyMPI_FLAGS_READY
    enum: PyMPI_FLAGS_CONST
    enum: PyMPI_FLAGS_TEMP

cdef inline int cinit(PyMPIClass self, PyMPIClass arg) except -1:
    self.ob_mpi = mpinull(self.ob_mpi)
    self.flags |= PyMPI_FLAGS_READY
    if arg is None: return 0
    self.ob_mpi = arg.ob_mpi
    if PyMPIClass is Request:
        self.ob_buf = arg.ob_buf
    if PyMPIClass is Message:
        self.ob_buf = arg.ob_buf
    if PyMPIClass is Op:
        self.ob_uid = arg.ob_uid
    if PyMPIClass is Win:
        self.ob_mem = arg.ob_mem
    return 0

cdef inline int marktemp(PyMPIClass self) except -1:
    if not predefined(self.ob_mpi):
        self.flags |= PyMPI_FLAGS_TEMP
    return 0

@cython.linetrace(False)
cdef inline int freetemp(PyMPIClass self) except -1:
    if named(self.ob_mpi): return 0
    if not mpi_active(): return 0
    if PyMPIClass is Datatype:
        CHKERR( MPI_Type_free(&self.ob_mpi) )
    return 0

@cython.linetrace(False)
cdef inline int dealloc(PyMPIClass self) except -1:
    if not (self.flags & PyMPI_FLAGS_READY): return 0
    if (self.flags & PyMPI_FLAGS_CONST): return 0
    if (self.flags & PyMPI_FLAGS_TEMP ): return freetemp(self)
    if self.flags: return 0 # TODO: this always return

    if not mpi_active(): return 0
    if predefined(self.ob_mpi): return 0
    PyErr_WarnFormat(
        RuntimeWarning, 1,
        b"collecting object with %.200U handle %p",
        <PyObject*> cython.typeof(self.ob_mpi),
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

cdef inline int nonnull(PyMPIClass self) noexcept nogil:
     return self.ob_mpi != mpinull(self.ob_mpi)

# -----------------------------------------------------------------------------

cdef dict def_registry = {}

cdef inline type def_class(handle_t handle):
    <void> handle # unused
    cdef type result = None
    if handle_t is MPI_Datatype   : result = Datatype
    if handle_t is MPI_Request    : result = Request
    if handle_t is MPI_Message    : result = Message
    if handle_t is MPI_Op         : result = Op
    if handle_t is MPI_Group      : result = Group
    if handle_t is MPI_Info       : result = Info
    if handle_t is MPI_Errhandler : result = Errhandler
    if handle_t is MPI_Session    : result = Session
    if handle_t is MPI_Comm       : result = Comm
    if handle_t is MPI_Win        : result = Win
    if handle_t is MPI_File       : result = File
    return result

cdef inline int def_register(
    handle_t handle,
    object   pyobj,
    object   name,
) except -1:
    cdef type cls = def_class(handle)
    cdef dict registry = def_registry.get(cls)
    cdef object key = <Py_uintptr_t> handle
    if registry is None:
        registry = def_registry[cls] = {}
    if key not in registry:
        registry[key] = (pyobj, name)
    return 0

cdef inline object def_lookup(handle_t handle):
    cdef type cls = def_class(handle)
    cdef dict registry = def_registry[cls]
    cdef object key = <Py_uintptr_t> handle
    return registry[key]

cdef __newobj__ = None
from copyreg import __newobj__

cdef inline object def_reduce(PyMPIClass self):
    cdef object pyobj, name
    pyobj, name = def_lookup(self.ob_mpi)
    if self is pyobj: return name
    return (__newobj__, (type(self), pyobj))

cdef inline object reduce_default(PyMPIClass self):
    if named(self.ob_mpi):
        return def_reduce(self)
    cdef str mod = type(self).__module__
    cdef str cls = type(self).__name__
    raise ValueError(f"cannot serialize '{mod}.{cls}' instance")

# -----------------------------------------------------------------------------

cdef inline Py_uintptr_t tohandle(PyMPIClass self) noexcept nogil:
    return <Py_uintptr_t> self.ob_mpi

cdef inline object fromhandle(handle_t arg):
    cdef object obj = None
    if handle_t is MPI_Datatype   : obj = PyMPIDatatype_New(arg)
    if handle_t is MPI_Request    : obj = PyMPIRequest_New(arg)
    if handle_t is MPI_Message    : obj = PyMPIMessage_New(arg)
    if handle_t is MPI_Op         : obj = PyMPIOp_New(arg)
    if handle_t is MPI_Group      : obj = PyMPIGroup_New(arg)
    if handle_t is MPI_Info       : obj = PyMPIInfo_New(arg)
    if handle_t is MPI_Errhandler : obj = PyMPIErrhandler_New(arg)
    if handle_t is MPI_Session    : obj = PyMPISession_New(arg)
    if handle_t is MPI_Comm       : obj = PyMPIComm_New(arg)
    if handle_t is MPI_Win        : obj = PyMPIWin_New(arg)
    if handle_t is MPI_File       : obj = PyMPIFile_New(arg)
    return obj

# -----------------------------------------------------------------------------

# Status

cdef inline MPI_Status *arg_Status(object status) except? NULL:
    if status is None: return MPI_STATUS_IGNORE
    return &((<Status?>status).ob_mpi)

# -----------------------------------------------------------------------------

# Datatype

cdef inline Datatype def_Datatype(MPI_Datatype arg, object name):
    cdef Datatype obj = Datatype.__new__(Datatype)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

cdef inline Datatype ref_Datatype(MPI_Datatype arg):
    cdef Datatype obj = Datatype.__new__(Datatype)
    obj.ob_mpi = arg
    if not predefined(arg):
        obj.flags |= 0 # TODO
    return obj

cdef inline object reduce_Datatype(Datatype self):
    # named
    if named(self.ob_mpi):
        return def_reduce(self)
    # predefined and user-defined
    cdef object basetype, combiner, params
    basetype, combiner, params = datatype_decode(self, True)
    return (_datatype_create, (basetype, combiner, params, True))

# -----------------------------------------------------------------------------

# Request

cdef inline Request def_Request(MPI_Request arg, object name):
    cdef Request obj = Request.__new__(Request)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

# -----------------------------------------------------------------------------

# Message

cdef inline Message def_Message(MPI_Message arg, object name):
    cdef Message obj = Message.__new__(Message)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

# -----------------------------------------------------------------------------

# Op

cdef dict def_op = {}

cdef inline Op def_Op(MPI_Op arg, object name):
    cdef Op obj = Op.__new__(Op)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

cdef inline object reduce_Op(Op self):
    # predefined
    if named(self.ob_mpi):
         return def_reduce(self)
    # user-defined
    cdef int index = self.ob_uid
    if index == 0:
        raise ValueError("cannot pickle user-defined reduction operation")
    cdef object function = op_user_registry[index]
    cdef object commute = self.Is_commutative()
    return (type(self).Create, (function, commute,))

# -----------------------------------------------------------------------------

# Group

cdef inline Group def_Group(MPI_Group arg, object name):
    cdef Group obj = Group.__new__(Group)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

# -----------------------------------------------------------------------------

# Info

cdef inline Info def_Info(MPI_Info arg, object name):
    cdef Info obj = Info.__new__(Info)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj


cdef extern from *:
    const MPI_Info _info_null "MPI_INFO_NULL"

cdef inline MPI_Info arg_Info(object obj) except? _info_null:
    if obj is None: return MPI_INFO_NULL
    return (<Info?>obj).ob_mpi

cdef inline object reduce_Info(Info self):
    # predefined
    if named(self.ob_mpi):
         return def_reduce(self)
    # user-defined
    return (type(self).Create, (self.items(),))

# -----------------------------------------------------------------------------

# Errhandler

cdef inline Errhandler def_Errhandler(MPI_Errhandler arg, object name):
    cdef Errhandler obj = Errhandler.__new__(Errhandler)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

cdef extern from *:
    const MPI_Errhandler _errhandler_null "MPI_ERRHANDLER_NULL"

cdef inline MPI_Errhandler arg_Errhandler(object obj) except? _errhandler_null:
    if obj is not None: return (<Errhandler?>obj).ob_mpi
    cdef int opt = options.errors
    if   opt == 0: pass
    elif opt == 1: return MPI_ERRORS_RETURN
    elif opt == 2: return MPI_ERRORS_ABORT
    elif opt == 3: return MPI_ERRORS_ARE_FATAL
    return MPI_ERRORS_ARE_FATAL

# -----------------------------------------------------------------------------

# Session

cdef inline Session def_Session(MPI_Session arg, object name):
    cdef Session obj = Session.__new__(Session)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

# -----------------------------------------------------------------------------

# Comm

cdef inline type CommType(MPI_Comm arg):
    if arg == MPI_COMM_NULL:
        return Comm
    if arg == MPI_COMM_SELF:
        return Intracomm
    if arg == MPI_COMM_WORLD:
        return Intracomm
    cdef int inter = 0
    CHKERR( MPI_Comm_test_inter(arg, &inter) )
    if inter:
        return Intercomm
    cdef int topo  = MPI_UNDEFINED
    CHKERR( MPI_Topo_test(arg, &topo) )
    if topo == MPI_UNDEFINED:
        return Intracomm
    if topo == MPI_CART:
        return Cartcomm
    if topo == MPI_GRAPH:
        return Graphcomm
    if topo == MPI_DIST_GRAPH:
        return Distgraphcomm
    return Comm  #~> unreachable

cdef inline Comm def_Comm(MPI_Comm arg, object name):
    cdef Comm obj = Comm.__new__(Comm)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

cdef inline Intracomm def_Intracomm(MPI_Comm arg, object name):
    cdef Intracomm obj = Intracomm.__new__(Intracomm)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

cdef inline Intercomm def_Intercomm(MPI_Comm arg):
    cdef Intercomm obj = Intercomm.__new__(Intercomm)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    return obj

# -----------------------------------------------------------------------------

# Win

cdef inline Win def_Win(MPI_Win arg, object name):
    cdef Win obj = Win.__new__(Win)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

# -----------------------------------------------------------------------------

# File

cdef inline File def_File(MPI_File arg, object name):
    cdef File obj = File.__new__(File)
    obj.ob_mpi = arg
    obj.flags |= PyMPI_FLAGS_CONST
    def_register(arg, obj, name)
    return obj

# -----------------------------------------------------------------------------
