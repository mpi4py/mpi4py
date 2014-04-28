# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    int Py_IsInitialized() nogil
    void PySys_WriteStderr(char*,...)
    int Py_AtExit(void (*)())

    void Py_INCREF(object)
    void Py_DECREF(object)
    void Py_CLEAR(void*)

# -----------------------------------------------------------------------------

cdef extern from "atimport.h":
    pass

# -----------------------------------------------------------------------------

ctypedef struct Options:
    int initialize
    int threaded
    int thread_level
    int finalize

cdef Options options
options.initialize = 1
options.threaded = 1
options.thread_level = MPI_THREAD_MULTIPLE
options.finalize = 1

cdef int warnOpt(object name, object value) except -1:
    cdef object warn
    from warnings import warn
    warn("mpi4py.rc: '%s': unexpected value '%r'" % (name, value))

cdef int getOptions(Options* opts) except -1:
    cdef object rc
    opts.initialize = 1
    opts.threaded = 1
    opts.thread_level = MPI_THREAD_MULTIPLE
    opts.finalize = 1
    try: from mpi4py import rc
    except: return 0
    #
    cdef object initialize = True
    cdef object threaded = True
    cdef object thread_level = 'multiple'
    cdef object finalize = None
    try: initialize = rc.initialize
    except: pass
    try: threaded = rc.threaded
    except: pass
    try: thread_level = rc.thread_level
    except: pass
    try: finalize = rc.finalize
    except: pass
    #
    if initialize in (True, 'yes'):
        opts.initialize = 1
    elif initialize in (False, 'no'):
        opts.initialize = 0
    else:
        warnOpt("initialize", initialize)
    #
    if threaded in (True, 'yes'):
        opts.threaded = 1
    elif threaded in (False, 'no'):
        opts.threaded = 0
    else:
        warnOpt("threaded", threaded)
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
        warnOpt("thread_level", thread_level)
    #
    if finalize is None:
        opts.finalize = opts.initialize
    elif finalize in (True, 'yes'):
        opts.finalize = 1
    elif finalize in (False, 'no'):
        opts.finalize = 0
    else:
        warnOpt("finalize", finalize)
    #
    return 0

# -----------------------------------------------------------------------------

cdef extern from *:
    #
    int PyMPI_STARTUP_DONE
    int PyMPI_StartUp() nogil
    #
    int PyMPI_CLEANUP_DONE
    int PyMPI_CleanUp() nogil

PyMPI_STARTUP_DONE = 0
PyMPI_CLEANUP_DONE = 0

cdef int initialize() except -1:
    # Get options from 'mpi4py.rc' module
    getOptions(&options)
    # MPI initialized ?
    cdef int initialized = 1
    <void>MPI_Initialized(&initialized)
    # MPI finalized ?
    cdef int finalized = 1
    <void>MPI_Finalized(&finalized)
    # Do we have to initialize MPI?
    if initialized:
        if not finalized:
            # Cleanup at (the very end of) Python exit
            if Py_AtExit(atexit) < 0:
                PySys_WriteStderr(b"warning: could not register "
                                  b"cleanup with Py_AtExit()\n", 0)
        options.finalize = 0
        return 0
    #
    cdef int ierr = MPI_SUCCESS
    cdef int required = MPI_THREAD_SINGLE
    cdef int provided = MPI_THREAD_SINGLE
    if options.initialize: # We have to initialize MPI
        if options.threaded:
            required = options.thread_level
            ierr = MPI_Init_thread(NULL, NULL, required, &provided)
            if ierr != MPI_SUCCESS: raise RuntimeError(
                "MPI_Init_thread() failed [error code: %d]" % ierr)
        else:
            ierr = MPI_Init(NULL, NULL)
            if ierr != MPI_SUCCESS: raise RuntimeError(
                "MPI_Init() failed [error code: %d]" % ierr)
    # Cleanup at (the very end of) Python exit
    if Py_AtExit(atexit) < 0:
        PySys_WriteStderr(b"warning: could not register "
                          b"cleanup with Py_AtExit()\n", 0)
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

cdef void startup() nogil:
    if not mpi_active(): return
    #DBG# fprintf(stderr, b"statup: BEGIN\n"); fflush(stderr)
    <void>PyMPI_StartUp();
    #DBG# fprintf(stderr, b"statup: END\n"); fflush(stderr)

cdef void cleanup() nogil:
    if not mpi_active(): return
    #DBG# fprintf(stderr, b"cleanup: BEGIN\n"); fflush(stderr)
    <void>PyMPI_CleanUp()
    #DBG# fprintf(stderr, b"cleanup: END\n"); fflush(stderr)

cdef void atexit() nogil:
    if not mpi_active(): return
    #DBG# fprintf(stderr, b"atexit: BEGIN\n"); fflush(stderr)
    cleanup()
    if options.finalize:
        #DBG# fprintf(stderr, b"MPI_Finalize\n"); fflush(stderr)
        <void>MPI_Finalize()
    #DBG# fprintf(stderr, b"atexit: END\n"); fflush(stderr)

# -----------------------------------------------------------------------------

# Vile hack for raising a exception and not contaminate the traceback

cdef extern from *:
    void PyErr_SetObject(object, object)
    void *PyExc_RuntimeError
    void *PyExc_NotImplementedError

cdef object MPIException = <object>PyExc_RuntimeError

cdef int PyMPI_Raise(int ierr) except -1 with gil:
    if ierr == -1:
        PyErr_SetObject(<object>PyExc_NotImplementedError, None)
        return 0
    if (<void*>MPIException) != NULL:
        PyErr_SetObject(MPIException, <long>ierr)
    else:
        PyErr_SetObject(<object>PyExc_RuntimeError, <long>ierr)
    return 0

cdef inline int CHKERR(int ierr) nogil except -1:
    if ierr == 0: return 0
    PyMPI_Raise(ierr)
    return -1

cdef inline void print_traceback():
    cdef object sys, traceback
    import sys, traceback
    traceback.print_exc()
    try: sys.stderr.flush()
    except: pass

# -----------------------------------------------------------------------------
