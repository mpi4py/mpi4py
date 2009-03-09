
# --------------------------------------------------------------------

cdef extern from "Python.h":
    ctypedef struct PyObject
    Py_ssize_t Py_REFCNT(object)
    void Py_INCREF(object) except *
    void Py_DECREF(object) except *
    int Py_IsInitialized() nogil
    void PySys_WriteStderr(char*,...)
    int Py_AtExit(void (*)())

# --------------------------------------------------------------------

cdef extern from "atimport.h":
    int PyMPI_KEYVAL_ATEXIT_MPI

# --------------------------------------------------------------------

cdef int mpi_is_owned = 0
cdef int cleanup_done = 0

cdef MPI_Errhandler comm_self_eh  = MPI_ERRHANDLER_NULL
cdef MPI_Errhandler comm_world_eh = MPI_ERRHANDLER_NULL
cdef int PyMPI_KEYVAL_WIN_MEMORY  = MPI_KEYVAL_INVALID

cdef inline int mpi_active() nogil:
    cdef int ierr = MPI_SUCCESS
    # MPI initialized ?
    cdef int initialized = 0
    ierr = MPI_Initialized(&initialized)
    if not initialized: return 0
    # MPI finalized ?
    cdef int finalized = 1
    ierr = MPI_Finalized(&finalized)
    if finalized: return 0
    # MPI should be active ...
    return 1

cdef int initialize() except -1:
    global mpi_is_owned
    cdef int ierr = MPI_SUCCESS
    # MPI initialized ?
    cdef int initialized = 1
    ierr = MPI_Initialized(&initialized)
    # MPI finalized ?
    cdef int finalized = 1
    ierr = MPI_Finalized(&finalized)
    # Do we have to initialize MPI?
    if initialized:
        if not finalized:
            if Py_AtExit(atexit_py) < 0:
                PySys_WriteStderr("warning: could not register"
                                  "cleanup with Py_AtExit()")
        return 0
    # We have to initialize MPI
    cdef int required = MPI_THREAD_SINGLE
    cdef int provided = MPI_THREAD_SINGLE
    if _mpi_threading(&required):
        ierr = MPI_Init_thread(NULL, NULL, required, &provided)
        if ierr != MPI_SUCCESS: raise RuntimeError(
            u"MPI_Init_thread() failed [error code: %d]" % ierr)
    else:
        ierr = MPI_Init(NULL, NULL)
        if ierr != MPI_SUCCESS: raise RuntimeError(
            u"MPI_Init() failed [error code: %d]" % ierr)
    # We initialized MPI, so it is owned and active at this point
    mpi_is_owned  = 1
    # then finalize it when Python process exits
    if Py_AtExit(atexit_py) < 0:
        PySys_WriteStderr("warning: could not register"
                          "MPI_Finalize() with Py_AtExit()")
    return 0

cdef int startup() except -1:
    if not mpi_active(): return 0
    #
    #DBG:# fprintf(stderr, "statup: BEGIN\n"); fflush(stderr)
    cdef int ierr = MPI_SUCCESS
    # change error handlers for predefined communicators
    global comm_world_eh
    if comm_world_eh == MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_get_errhandler(MPI_COMM_WORLD, &comm_world_eh)
        ierr = MPI_Comm_set_errhandler(MPI_COMM_WORLD, MPI_ERRORS_RETURN)
    global comm_self_eh
    if comm_self_eh == MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_get_errhandler(MPI_COMM_SELF,  &comm_self_eh)
        ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF,  MPI_ERRORS_RETURN)
    # make the call to MPI_Finalize() run a cleanup function
    global PyMPI_KEYVAL_ATEXIT_MPI
    cdef int keyval = PyMPI_KEYVAL_ATEXIT_MPI
    if keyval == MPI_KEYVAL_INVALID:
        ierr = MPI_Comm_create_keyval(MPI_COMM_NULL_COPY_FN,
                                      atexit_mpi, &keyval, NULL)
        ierr = MPI_Comm_set_attr(MPI_COMM_SELF, keyval, NULL)
        ierr = MPI_Comm_free_keyval(&keyval)
        PyMPI_KEYVAL_ATEXIT_MPI = keyval
    #
    #DBG:# fprintf(stderr, "statup: END\n"); fflush(stderr)
    return 0

cdef void cleanup() nogil:
    if not mpi_active(): return
    #
    global cleanup_done
    if cleanup_done: return
    cleanup_done = 1
    #
    #DBG:# fprintf(stderr, "cleanup: BEGIN\n"); fflush(stderr)
    cdef int ierr = MPI_SUCCESS
    # free windows keyval
    global PyMPI_KEYVAL_WIN_MEMORY
    if PyMPI_KEYVAL_WIN_MEMORY != MPI_KEYVAL_INVALID:
        ierr = MPI_Win_free_keyval(&PyMPI_KEYVAL_WIN_MEMORY)
        PyMPI_KEYVAL_WIN_MEMORY = MPI_KEYVAL_INVALID
    # restore default error handlers for predefined communicators
    global comm_self_eh
    if comm_self_eh != MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF, comm_self_eh)
        ierr = MPI_Errhandler_free(&comm_self_eh)
        comm_self_eh = MPI_ERRHANDLER_NULL
    global comm_world_eh
    if comm_world_eh != MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_set_errhandler(MPI_COMM_WORLD, comm_world_eh)
        ierr = MPI_Errhandler_free(&comm_world_eh)
        comm_world_eh = MPI_ERRHANDLER_NULL
    #DBG:# fprintf(stderr, "cleanup: END\n"); fflush(stderr)

cdef int atexit_mpi(MPI_Comm c,int k, void *v, void *xs) nogil:
    #DBG:# fprintf(stderr, "atexit_mpi: BEGIN\n"); fflush(stderr)
    cleanup()
    #DBG:# fprintf(stderr, "atexit_mpi: END\n"); fflush(stderr)
    return MPI_SUCCESS

cdef void atexit_py() nogil:
    #DBG:# fprintf(stderr, "atexit_py: BEGIN\n"); fflush(stderr)
    cleanup()
    # try to finalize MPI
    global mpi_is_owned
    cdef int ierr = MPI_SUCCESS
    if mpi_is_owned and mpi_active():
        ierr = MPI_Finalize()
    #DBG:# fprintf(stderr, "atexit_py: END\n"); fflush(stderr)

# --------------------------------------------------------------------

cdef inline int _mpi_threading(int *level) except -1:
    try:
        from mpi4py.rc import thread_level
    except ImportError:
        thread_level = None
    #
    if thread_level is None:
        return 0
    elif thread_level in (0, u'single'):
        level[0] = MPI_THREAD_SINGLE
    elif thread_level in (1, u'funneled'):
        level[0] = MPI_THREAD_FUNNELED
    elif thread_level in (2, u'serialized'):
        level[0] = MPI_THREAD_SERIALIZED
    elif thread_level in (3, u'multiple'):
        level[0] = MPI_THREAD_MULTIPLE
    else:
        from warnings import warn
        warn("mpi4py.rc: unrecognized thread level")
        return 0
    return 1

# --------------------------------------------------------------------

# Vile hack for raising a exception and not contaminate the traceback

cdef extern from *:
    void __Pyx_Raise(object, object, void*)

cdef extern from *:
    PyObject *PyExc_RuntimeError
    PyObject *PyExc_NotImplementedError

cdef object MPIException = <object>PyExc_RuntimeError

cdef int PyMPI_Raise(int ierr) except -1 with gil:
    if ierr != -1:
        if (<void*>MPIException) != NULL:
            __Pyx_Raise(MPIException, ierr, NULL)
        else:
            __Pyx_Raise(<object>PyExc_RuntimeError, ierr, NULL)
    else:
        __Pyx_Raise(<object>PyExc_NotImplementedError, None, NULL)
    return 0

cdef inline int CHKERR(int ierr) nogil except -1:
    if ierr == 0: return 0
    PyMPI_Raise(ierr)
    return -1

# --------------------------------------------------------------------
