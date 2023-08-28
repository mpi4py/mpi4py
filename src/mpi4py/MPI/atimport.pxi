# -----------------------------------------------------------------------------

cdef extern from * nogil:
    """
    #include "lib-mpi/config.h"
    #include "lib-mpi/missing.h"
    #include "lib-mpi/fallback.h"
    #include "lib-mpi/compat.h"

    #include "pympivendor.h"
    #include "pympistatus.h"
    #include "pympicommctx.h"
    """

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    enum: PY_VERSION_HEX

cdef extern from "Python.h":
    """
    #if PY_VERSION_HEX < 0x030B0000 && !defined(Py_GETENV)
    #  define Py_GETENV(s) (Py_IgnoreEnvironmentFlag ? NULL : getenv(s))
    #endif
    """
    const char *Py_GETENV(const char[]) nogil

cdef extern from * nogil:
    """
    #if defined(PYPY_VERSION)
    #  define PyMPI_RUNTIME_PYPY 1
    #else
    #  define PyMPI_RUNTIME_PYPY 0
    #endif
    """
    enum: PYPY "PyMPI_RUNTIME_PYPY"

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    """
    #if PY_VERSION_HEX < 0x30C00A7 && !defined(PyErr_DisplayException)
    #define PyErr_DisplayException PyErr_DisplayException_312
    static void PyErr_DisplayException(PyObject *exc)
    {
      PyObject *et = NULL;
      PyObject *tb = NULL;
      #if defined(PYPY_VERSION)
      et = PyObject_Type(exc);
      tb = PyException_GetTraceback(exc);
      #endif
      PyErr_Display(et, exc, tb);
      if (et) Py_DecRef(et);
      if (tb) Py_DecRef(tb);
    }
    #endif
    """
    void *PyExc_RuntimeError
    void *PyExc_NotImplementedError
    void PyErr_SetNone(object)
    void PyErr_SetObject(object, object)
    void PyErr_DisplayException(object)
    int  PyErr_WarnFormat(object, Py_ssize_t, const char[], ...) except -1
    void PySys_WriteStderr(const char[], ...)

# -----------------------------------------------------------------------------

cdef extern from * nogil:
    """
    #if !defined(PyMPI_USE_MATCHED_RECV)
    #  if defined(PyMPI_HAVE_MPI_Mprobe) && defined(PyMPI_HAVE_MPI_Mrecv)
    #    if defined(MPI_VERSION) && MPI_VERSION >= 3
    #      define PyMPI_USE_MATCHED_RECV 1
    #    endif
    #  endif
    #endif
    #if !defined(PyMPI_USE_MATCHED_RECV)
    #  define PyMPI_USE_MATCHED_RECV 0
    #endif
    """
    enum: USE_MATCHED_RECV "PyMPI_USE_MATCHED_RECV"

ctypedef struct Options:
    bint      initialize
    bint      threads
    int       thread_level
    bint      finalize
    bint      fast_reduce
    bint      recv_mprobe
    MPI_Count irecv_bufsz
    int       errors

cdef Options options
options.initialize = 1
options.threads = 1
options.thread_level = MPI_THREAD_MULTIPLE
options.finalize = 1
options.fast_reduce = 1
options.recv_mprobe = 1
options.irecv_bufsz = 32768
options.errors = 1

cdef object getOpt(object rc, const char name[], object value):
    cdef bytes bname = b"MPI4PY_RC_" + name.upper()
    cdef const char *cname  = <const char*>bname
    cdef const char *cvalue = Py_GETENV(cname)
    if cvalue == NULL:
        return getattr(rc, pystr(name), value)
    if cstr_is_uint(cvalue) and (type(value) is int):
        value = int(pystr(cvalue))
    elif cstr_is_bool(cvalue):
        value = <bint>cstr2bool(cvalue)
    else:
        value = pystr(cvalue).lower()
    try:
        setattr(rc, pystr(name), value)
    except:
        pass
    return value

cdef int warnOpt(const char name[], object value) except -1:
    value = PyUnicode_AsUTF8String(repr(value))
    PyErr_WarnFormat(
        RuntimeWarning, 1,
        b"mpi4py.rc.%s: unexpected value %.200s",
        name, <const char*>value,
    )
    return 0

cdef int getOptions(Options* opts) except -1:
    opts.initialize = 1
    opts.threads = 1
    opts.thread_level = MPI_THREAD_MULTIPLE
    opts.finalize = 1
    opts.fast_reduce = 1
    opts.recv_mprobe = USE_MATCHED_RECV
    opts.irecv_bufsz = 32768
    opts.errors = 1
    #
    cdef object rc
    try:
        from . import rc
    except (ImportError, ImportWarning):
        rc = None
    #
    cdef object initialize   = getOpt(rc, b"initialize"   , True        )
    cdef object threads      = getOpt(rc, b"threads"      , True        )
    cdef object thread_level = getOpt(rc, b"thread_level" , 'multiple'  )
    cdef object finalize     = getOpt(rc, b"finalize"     , None        )
    cdef object fast_reduce  = getOpt(rc, b"fast_reduce"  , True        )
    cdef object recv_mprobe  = getOpt(rc, b"recv_mprobe"  , True        )
    cdef object irecv_bufsz  = getOpt(rc, b"irecv_bufsz"  , 32768       )
    cdef object errors       = getOpt(rc, b"errors"       , 'exception' )
    #
    if initialize in (True, 'yes'):
        opts.initialize = 1
    elif initialize in (False, 'no'):
        opts.initialize = 0
    else:
        warnOpt(b"initialize", initialize)
    #
    if threads in (True, 'yes'):
        opts.threads = 1
    elif threads in (False, 'no'):
        opts.threads = 0
    else:
        warnOpt(b"threads", threads)
    #
    if thread_level == 'single':
        opts.thread_level = MPI_THREAD_SINGLE
    elif thread_level == 'funneled':
        opts.thread_level = MPI_THREAD_FUNNELED
    elif thread_level == 'serialized':
        opts.thread_level = MPI_THREAD_SERIALIZED
    elif thread_level == 'multiple':
        opts.thread_level = MPI_THREAD_MULTIPLE
    else:
        warnOpt(b"thread_level", thread_level)
    #
    if finalize is None:
        opts.finalize = opts.initialize
    elif finalize in (True, 'yes'):
        opts.finalize = 1
    elif finalize in (False, 'no'):
        opts.finalize = 0
    else:
        warnOpt(b"finalize", finalize)
    #
    if fast_reduce in (True, 'yes'):
        opts.fast_reduce = 1
    elif fast_reduce in (False, 'no'):
        opts.fast_reduce = 0
    else:
        warnOpt(b"fast_reduce", fast_reduce)
    #
    if recv_mprobe in (True, 'yes'):
        opts.recv_mprobe = 1 and USE_MATCHED_RECV
    elif recv_mprobe in (False, 'no'):
        opts.recv_mprobe = 0
    else:
        warnOpt(b"recv_mprobe", recv_mprobe)
    #
    if type(irecv_bufsz) is int and irecv_bufsz >= 0:
        opts.irecv_bufsz = irecv_bufsz
    else:
        warnOpt(b"irecv_bufsz", irecv_bufsz)
    #
    if errors == 'default':
        opts.errors = 0
    elif errors == 'exception':
        opts.errors = 1
    elif errors == 'abort':
        opts.errors = 2
        if MPI_ERRORS_ABORT == MPI_ERRHANDLER_NULL: opts.errors = 3
    elif errors == 'fatal':
        opts.errors = 3
    else:
        warnOpt(b"errors", errors)
    #
    return 0

# -----------------------------------------------------------------------------

cdef extern from * nogil:
    """
    #if defined(MPICH)
    #  define PyMPI_HAVE_MPICH   1
    #  define PyMPI_HAVE_OPENMPI 0
    #elif defined(OPEN_MPI)
    #  define PyMPI_HAVE_MPICH   0
    #  define PyMPI_HAVE_OPENMPI 1
    #else
    #  define PyMPI_HAVE_MPICH   0
    #  define PyMPI_HAVE_OPENMPI 0
    #endif
    """
    enum: MPICH   "PyMPI_HAVE_MPICH"
    enum: OPENMPI "PyMPI_HAVE_OPENMPI"

cdef int warn_environ(const char envvar[]) except -1 with gil:
    PyErr_WarnFormat(
        RuntimeWarning, 1,
        b"environment variable %s: "
        b"unexpected value '%.200s'",
        envvar, getenv(envvar),
    )

cdef int warn_mpiexec(const char envvar[]) except -1 with gil:
    cdef const char *vendor = NULL
    <void>PyMPI_Get_vendor(&vendor, NULL, NULL, NULL)
    PyErr_WarnFormat(
        RuntimeWarning, 1,
        b"suspicious MPI execution environment\n"
        b"Your environment has %s=%.200s set, "
        b"but mpi4py was built with %s.\n"
        b"You may be using `mpiexec` or `mpirun` "
        b"from a different MPI implementation.",
        envvar, getenv(envvar), vendor,
    )

cdef int check_mpiexec() except -1 nogil:
    cdef int ierr, size = 0
    ierr = MPI_Comm_size(MPI_COMM_WORLD, &size)
    if ierr != MPI_SUCCESS: return 0
    if size > 1: return 0

    cdef int check = 1
    cdef const char *ename  = b"MPI4PY_CHECK_MPIEXEC"
    cdef const char *value  = Py_GETENV(ename)
    if value != NULL: check = cstr2bool(value)
    if check == -1: warn_environ(ename)
    if check <=  0: return 0

    cdef const char *hydra   = b"HYDI_CONTROL_FD"
    cdef const char *mpich   = b"PMI_SIZE"
    cdef const char *openmpi = b"OMPI_COMM_WORLD_SIZE"
    cdef const char *bad_env = NULL
    if MPICH:
        if getenv(mpich) == NULL and getenv(hydra) == NULL:      #~> mpich
            if getenv(openmpi) != NULL:                          #~> mpich
                bad_env = openmpi                                #~> mpich
    if OPENMPI:
        if getenv(openmpi) == NULL:                              #~> openmpi
            if getenv(mpich) != NULL and getenv(hydra) != NULL:  #~> openmpi
                bad_env = mpich                                  #~> openmpi
    if bad_env != NULL:
        warn_mpiexec(bad_env)
    return 0

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    int Py_AtExit(void (*)() noexcept nogil)

cdef extern from * nogil:
    int PyMPI_Commctx_finalize()

cdef int bootstrap() except -1:
    # Get options from 'mpi4py.rc' module
    getOptions(&options)
    # Cleanup at (the very end of) Python exit
    if Py_AtExit(atexit) < 0:
        PySys_WriteStderr(                                   #~> uncovered
            b"WARNING: %s\n",                                #~> uncovered
            b"could not register cleanup with Py_AtExit()",  #~> uncovered
        )
    # Do we have to initialize MPI?
    cdef int initialized = 1
    <void>MPI_Initialized(&initialized)
    if initialized:
        options.finalize = 0  #~> TODO
        return 0              #~> TODO
    if not options.initialize:
        return 0
    # MPI initialization
    cdef int ierr = MPI_SUCCESS
    cdef int required = MPI_THREAD_SINGLE
    cdef int provided = MPI_THREAD_SINGLE
    if options.threads:
        required = options.thread_level
        ierr = MPI_Init_thread(NULL, NULL, required, &provided)
        if ierr != MPI_SUCCESS:
            raise RuntimeError(               #~> uncovered
                f"MPI_Init_thread() failed "  #~> uncovered
                f"[error code: {ierr}]")      #~> uncovered
    else:
        ierr = MPI_Init(NULL, NULL)
        if ierr != MPI_SUCCESS:
            raise RuntimeError(               #~> uncovered
                f"MPI_Init() failed "         #~> uncovered
                f"[error code: {ierr}]")      #~> uncovered
    return 0

@cython.linetrace(False)
cdef inline int mpi_active() noexcept nogil:
    cdef int ierr = MPI_SUCCESS
    # MPI initialized ?
    cdef int initialized = 0
    ierr = MPI_Initialized(&initialized)
    if not initialized or ierr != MPI_SUCCESS: return 0
    # MPI finalized ?
    cdef int finalized = 1
    ierr = MPI_Finalized(&finalized)
    if finalized or ierr != MPI_SUCCESS: return 0
    # MPI should be active ...
    return 1

cdef int initialize() except -1 nogil:
    if not mpi_active(): return 0
    check_mpiexec()
    comm_set_eh(MPI_COMM_SELF)
    comm_set_eh(MPI_COMM_WORLD)
    return 0

@cython.linetrace(False)
cdef void finalize() noexcept nogil:
    if not mpi_active(): return
    <void>PyMPI_Commctx_finalize()

cdef int abort_status = 0

@cython.linetrace(False)
cdef void atexit() noexcept nogil:
    if not mpi_active(): return
    if abort_status:
        <void>MPI_Abort(MPI_COMM_WORLD, abort_status)
    finalize()
    if options.finalize:
        <void>MPI_Finalize()

def _set_abort_status(int status: int) -> None:
    """
    Helper for ``python -m mpi4py.run ...``.
    """
    global abort_status
    abort_status = status

# -----------------------------------------------------------------------------

# Raise exceptions without adding to traceback

cdef extern from * nogil:
    enum: PyMPI_ERR_UNAVAILABLE

cdef object MPIException = <object>PyExc_RuntimeError

cdef int PyMPI_Raise(int ierr) except -1 with gil:
    if ierr == PyMPI_ERR_UNAVAILABLE:
        PyErr_SetObject(<object>PyExc_NotImplementedError, None)  #~> uncovered
        return 0                                                  #~> uncovered
    if (<void*>MPIException) == NULL:
        PyErr_SetObject(<object>PyExc_RuntimeError, <long>ierr)   #~> uncovered
        return 0                                                  #~> uncovered
    PyErr_SetObject(MPIException, <long>ierr)
    return 0

cdef inline int CHKERR(int ierr) except -1 nogil:
    if ierr == MPI_SUCCESS: return 0
    PyMPI_Raise(ierr)
    return -1

cdef int PyMPI_HandleException(object exc) noexcept:
    PyErr_DisplayException(exc)
    if (<void*>MPIException) != NULL:
        if isinstance(exc, Exception):
            return (<Exception>exc).ob_mpi
    return MPI_ERR_OTHER

# -----------------------------------------------------------------------------

cdef object _py_module_sentinel = None

@cython.linetrace(False)
cdef inline int py_module_alive() noexcept nogil:
    return NULL != <void *>_py_module_sentinel

# -----------------------------------------------------------------------------

# PyPy: Py_IsInitialized() cannot be called without the GIL

cdef extern from "Python.h":
    int _Py_IsInitialized"Py_IsInitialized"() noexcept nogil

@cython.linetrace(False)
cdef inline int Py_IsInitialized() noexcept nogil:
    if PYPY and not py_module_alive(): return 0
    return _Py_IsInitialized()

# -----------------------------------------------------------------------------
