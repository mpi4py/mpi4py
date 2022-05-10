# -----------------------------------------------------------------------------

cdef extern from "mpimodule.h": pass

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    void *PyExc_RuntimeError
    void *PyExc_NotImplementedError
    void PyErr_SetObject(object, object)
    int  PyErr_WarnFormat(object, Py_ssize_t, const char[], ...) except -1

# -----------------------------------------------------------------------------

cdef extern from *:
    """
    #if defined(PYPY_VERSION)
    #  define PyMPI_RUNTIME_PYPY 1
    #else
    #  define PyMPI_RUNTIME_PYPY 0
    #endif
    """
    enum: PYPY "PyMPI_RUNTIME_PYPY"

# -----------------------------------------------------------------------------

cdef extern from *:
    """
    #if !defined(Py_GETENV)
    #  define Py_GETENV(s) (Py_IgnoreEnvironmentFlag ? NULL : getenv(s))
    #endif
    """
    const char *Py_GETENV(const char[]) nogil

# -----------------------------------------------------------------------------

cdef extern from *:
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
    int initialize
    int threads
    int thread_level
    int finalize
    int fast_reduce
    int recv_mprobe
    int errors

cdef Options options
options.initialize = 1
options.threads = 1
options.thread_level = MPI_THREAD_MULTIPLE
options.finalize = 1
options.fast_reduce = 1
options.recv_mprobe = 1
options.errors = 1

cdef object getOpt(object rc, const char name[], object value):
    cdef bytes bname = b"MPI4PY_RC_" + name.upper()
    cdef const char *cname  = <const char*>bname
    cdef const char *cvalue = Py_GETENV(cname)
    if cvalue == NULL:
        try:
            value = getattr(rc, pystr(name), value)
        except:
            pass
        return value
    cdef int bvalue = cstr2bool(cvalue)
    cdef object svalue = None
    if bvalue >= 0:
        svalue = <bint>bvalue
    else:
        svalue = pystr(cvalue).lower()
    try:
        setattr(rc, pystr(name), svalue)
    except:
        pass
    return svalue

cdef int warnOpt(const char name[], object value) except -1:
    value = PyUnicode_AsUTF8String(repr(value))
    PyErr_WarnFormat(
        RuntimeWarning, 1,
        b"mpi4py.rc.%s: unexpected value %.200s",
        name, <const char*>value,
    )
    return 0

cdef int getOptions(Options* opts) except -1:
    cdef object rc
    opts.initialize = 1
    opts.threads = 1
    opts.thread_level = MPI_THREAD_MULTIPLE
    opts.finalize = 1
    opts.fast_reduce = 1
    opts.recv_mprobe = USE_MATCHED_RECV
    opts.errors = 1
    try: from . import rc
    except: return 0
    #
    cdef object initialize   = getOpt(rc, b"initialize"   , True        )
    cdef object threads      = getOpt(rc, b"threads"      , True        )
    cdef object thread_level = getOpt(rc, b"thread_level" , 'multiple'  )
    cdef object finalize     = getOpt(rc, b"finalize"     , None        )
    cdef object fast_reduce  = getOpt(rc, b"fast_reduce"  , True        )
    cdef object recv_mprobe  = getOpt(rc, b"recv_mprobe"  , True        )
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
    if errors == 'default':
        opts.errors = 0
    elif errors == 'exception':
        opts.errors = 1
    elif errors == 'fatal':
        opts.errors = 2
    else:
        warnOpt(b"errors", errors)
    #
    return 0

# -----------------------------------------------------------------------------

cdef extern from *:
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

cdef int check_mpiexec() nogil except -1:
    cdef int ierr, size = 0
    ierr = MPI_Comm_size(MPI_COMM_WORLD, &size)
    if ierr != MPI_SUCCESS: return 0
    if size > 1: return 0

    cdef int check = 1
    cdef const char *check_name   = b"MPI4PY_CHECK_MPIEXEC"
    cdef const char *check_value  = Py_GETENV(check_name)
    if check_value != NULL: check = cstr2bool(check_value)
    if check <= 0:
        if check == -1:
            with gil:
                PyErr_WarnFormat(
                    RuntimeWarning, 1,
                    b"Environment variable %s: "
                    b"unexpected value '%s'",
                    check_name, check_value,
                )
        return 0

    cdef const char *hydra   = b"HYDI_CONTROL_FD"
    cdef const char *mpich   = b"PMI_SIZE"
    cdef const char *openmpi = b"OMPI_COMM_WORLD_SIZE"
    cdef const char *bad_env = NULL
    if MPICH:
        if getenv(mpich) == NULL and getenv(hydra) == NULL:
            if getenv(openmpi) != NULL:
                bad_env = openmpi
    if OPENMPI:
        if getenv(openmpi) == NULL:
            if getenv(mpich) != NULL and getenv(hydra) != NULL:
                bad_env = mpich
    if bad_env == NULL: return 0

    cdef const char *vendor = NULL
    <void>PyMPI_Get_vendor(&vendor, NULL, NULL, NULL)

    with gil:
        PyErr_WarnFormat(
            RuntimeWarning, 1,
            b"Suspicious MPI execution environment.\n"
            b"Your environment has %s=%.200s set, "
            b"but mpi4py was built with %s.\n"
            b"You may be using `mpiexec` or `mpirun` "
            b"from a different MPI implementation.",
            bad_env, getenv(bad_env), vendor,
        )
    return  0

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    int Py_AtExit(void (*)())
    void PySys_WriteStderr(char*,...)

cdef extern from *:
    int PyMPI_Commctx_finalize() nogil

cdef int bootstrap() except -1:
    # Get options from 'mpi4py.rc' module
    getOptions(&options)
    # Cleanup at (the very end of) Python exit
    if Py_AtExit(atexit) < 0:
        PySys_WriteStderr(b"warning: could not register "
                          b"cleanup with Py_AtExit()%s", b"\n")
    # Do we have to initialize MPI?
    cdef int initialized = 1
    <void>MPI_Initialized(&initialized)
    if initialized:
        options.finalize = 0
        return 0
    if not options.initialize:
        return 0
    # MPI initialization
    cdef int ierr = MPI_SUCCESS
    cdef int required = MPI_THREAD_SINGLE
    cdef int provided = MPI_THREAD_SINGLE
    if options.threads:
        required = options.thread_level
        ierr = MPI_Init_thread(NULL, NULL, required, &provided)
        if ierr != MPI_SUCCESS: raise RuntimeError(
            f"MPI_Init_thread() failed [error code: {ierr}]")
    else:
        ierr = MPI_Init(NULL, NULL)
        if ierr != MPI_SUCCESS: raise RuntimeError(
            f"MPI_Init() failed [error code: {ierr}]")
    return 0

cdef inline int mpi_active() nogil:
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

cdef int initialize() nogil except -1:
    if not mpi_active(): return 0
    check_mpiexec()
    comm_set_eh(MPI_COMM_SELF)
    comm_set_eh(MPI_COMM_WORLD)
    return 0

cdef void finalize() nogil:
    if not mpi_active(): return
    <void>PyMPI_Commctx_finalize()

cdef int abort_status = 0

cdef void atexit() nogil:
    if not mpi_active(): return
    if abort_status:
        <void>MPI_Abort(MPI_COMM_WORLD, abort_status)
    finalize()
    if options.finalize:
        <void>MPI_Finalize()

def _set_abort_status(object status: Any) -> None:
    "Helper for ``python -m mpi4py.run ...``"
    global abort_status
    try:
        abort_status = status
    except:
        abort_status = 1 if status else 0

# -----------------------------------------------------------------------------

# Vile hack for raising a exception and not contaminate the traceback

cdef extern from *:
    enum: PyMPI_ERR_UNAVAILABLE

cdef object MPIException = <object>PyExc_RuntimeError

cdef int PyMPI_Raise(int ierr) except -1 with gil:
    if ierr == PyMPI_ERR_UNAVAILABLE:
        PyErr_SetObject(<object>PyExc_NotImplementedError, None)
        return 0
    if (<void*>MPIException) != NULL:
        PyErr_SetObject(MPIException, <long>ierr)
    else:
        PyErr_SetObject(<object>PyExc_RuntimeError, <long>ierr)
    return 0

cdef inline int CHKERR(int ierr) nogil except -1:
    if ierr == MPI_SUCCESS: return 0
    PyMPI_Raise(ierr)
    return -1

cdef inline void print_traceback():
    cdef object sys, traceback
    import sys, traceback
    traceback.print_exc()
    try: sys.stderr.flush()
    except: pass

# -----------------------------------------------------------------------------

# PyPy: Py_IsInitialized() cannot be called without the GIL

cdef extern from "Python.h":
    int _Py_IsInitialized"Py_IsInitialized"() nogil

cdef object _pypy_sentinel = None

cdef inline int Py_IsInitialized() nogil:
    if PYPY and (<void*>_pypy_sentinel) == NULL: return 0
    return _Py_IsInitialized()

# -----------------------------------------------------------------------------
