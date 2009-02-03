
# --------------------------------------------------------------------

cdef extern from "Python.h":
    int Py_IsInitialized() nogil
    Py_ssize_t Py_REFCNT(object)
    void Py_INCREF(object) except *
    void Py_DECREF(object) except *
    int Py_AtExit(void (*)())
    void PySys_WriteStderr(char*,...)

cdef extern from "stdio.h":
    ctypedef struct FILE
    FILE *stderr
    int fprintf(FILE *, char *, ...) nogil

# --------------------------------------------------------------------

cdef int mpi_is_owned  = 0
cdef int mpi_is_active = 0

cdef int PyMPI_KEYVAL_WIN_MEMORY = MPI_KEYVAL_INVALID

cdef MPI_Errhandler comm_self_eh = MPI_ERRHANDLER_NULL
cdef MPI_Errhandler comm_world_eh = MPI_ERRHANDLER_NULL

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

cdef inline int _mpi_active() nogil:
    # shortcut
    global mpi_is_active
    if mpi_is_active: return 1
    # MPI initialized ?
    cdef int initialized = 0
    MPI_Initialized(&initialized)
    if not initialized: return 0
    # MPI finalized ?
    cdef int finalized = 1
    MPI_Finalized(&finalized)
    if finalized: return 0
    # MPI should be active
    return 1

cdef void _atexit_py() nogil:
    cdef int ierr = 0
    global mpi_is_active
    mpi_is_active = 0
    # test if MPI was initialized
    cdef int initialized = 0
    MPI_Initialized(&initialized)
    if not initialized: return
    # test if MPI was finalized
    cdef int finalized = 1
    MPI_Finalized(&finalized)
    if finalized: return
    # free windows keyval
    global PyMPI_KEYVAL_WIN_MEMORY
    if PyMPI_KEYVAL_WIN_MEMORY != MPI_KEYVAL_INVALID:
        ierr = MPI_Win_free_keyval(&PyMPI_KEYVAL_WIN_MEMORY)
    # restore default error handlers for predefined communicators
    global comm_self_eh, comm_world_eh
    if comm_self_eh != MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF, comm_self_eh)
        ierr = MPI_Errhandler_free(&comm_self_eh)
        comm_self_eh = MPI_ERRHANDLER_NULL
    if comm_world_eh != MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_set_errhandler(MPI_COMM_WORLD, comm_world_eh)
        ierr = MPI_Errhandler_free(&comm_world_eh)
        comm_world_eh = MPI_ERRHANDLER_NULL
    # try to finalize MPI
    global mpi_is_owned
    if mpi_is_owned:
        ierr = MPI_Finalize()
        if ierr != MPI_SUCCESS:
            fprintf(stderr, "MPI_Finalize() failed "
                    "[error code: %d]\n", ierr)

cdef inline int _init1() except -1:
    global comm_self_eh, comm_world_eh
    comm_self_eh  = MPI_ERRHANDLER_NULL
    comm_world_eh = MPI_ERRHANDLER_NULL
    # MPI initialized ?
    cdef int initialized = 1
    MPI_Initialized(&initialized)
    # MPI finalized ?
    cdef int finalized = 1
    MPI_Finalized(&finalized)
    # Do we have to initialize MPI?
    global mpi_is_owned
    global mpi_is_active
    mpi_is_owned  = 0
    mpi_is_active = 0
    if initialized:
        if not finalized:
            mpi_is_active = 1
        return 0
    # We have to initialize MPI
    cdef int ierr = 0
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
    mpi_is_active = 1
    # then finalize it when Python process exits
    if Py_AtExit(_atexit_py) < 0:
        PySys_WriteStderr("warning: could not register"
                          "MPI_Finalize() with Py_AtExit()")
    return 0

# --------------------------------------------------------------------

cdef inline int _init2() except -1:
    cdef int ierr = 0
    if not mpi_is_active: return 0
    # backup default error handlers for predefined communicators
    global comm_self_eh, comm_world_eh
    ierr = MPI_Comm_get_errhandler(MPI_COMM_SELF,  &comm_self_eh)
    if ierr: pass # XXX handle error, but unlikely fails
    ierr = MPI_Comm_get_errhandler(MPI_COMM_WORLD, &comm_world_eh)
    if ierr: pass # XXX handle error, but unlikely fails
    # We are going to manage MPI errors raising Python exceptions
    ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF,  MPI_ERRORS_RETURN)
    if ierr: pass # XXX handle error, but unlikely fails
    ierr = MPI_Comm_set_errhandler(MPI_COMM_WORLD, MPI_ERRORS_RETURN)
    if ierr: pass # XXX handle error, but unlikely fails
    return 0

# --------------------------------------------------------------------

# Interception of the actual call to MPI_Finalize()

cdef int _atexit_mpi(MPI_Comm c,int k, void *v, void *xs) nogil:
    # MPI is no longer active
    global mpi_is_active
    mpi_is_active = 0
    # and we are done
    return MPI_SUCCESS

cdef inline int _init3() except -1:
    if not mpi_is_active: return 0
    cdef int ierr = 0
    cdef int keyval = MPI_KEYVAL_INVALID
    ierr = MPI_Comm_create_keyval(MPI_COMM_NULL_COPY_FN,
                                  _atexit_mpi,
                                  &keyval, NULL)
    if ierr: pass # XXX handle error ?
    ierr = MPI_Comm_set_attr(MPI_COMM_SELF, keyval, NULL)
    if ierr: pass # XXX handle error ?
    ierr = MPI_Comm_free_keyval(&keyval)
    if ierr: pass # XXX handle error ?
    return 0

# --------------------------------------------------------------------

# Vile hack for raising a exception and not contaminate the traceback

cdef extern from *:
    void __Pyx_Raise(object, object, void*)


cdef int PyMPI_Raise(int ierr) except -1 with gil:
    if ierr != -1:
        __Pyx_Raise(Exception, ierr, NULL)
    else:
        __Pyx_Raise(NotImplementedError, None, NULL)
    return 0

cdef inline int CHKERR(int ierr) nogil except -1:
    if ierr == 0: return 0
    PyMPI_Raise(ierr)
    return -1

# --------------------------------------------------------------------
