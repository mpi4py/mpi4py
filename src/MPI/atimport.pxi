
# --------------------------------------------------------------------

cdef extern from "stdio.h":
    ctypedef struct FILE
    FILE *stderr
    int fprintf(FILE *, char *, ...)
    int fflush(FILE *)

cdef extern from "Python.h":
    int Py_AtExit(void (*)())

cdef extern from "atimport.h":
    object PyMPI_Get_vendor()

# --------------------------------------------------------------------

cdef int mpi_is_owned  = 0
cdef int mpi_is_active = 0
cdef MPI_Errhandler comm_self_eh
cdef MPI_Errhandler comm_world_eh

# --------------------------------------------------------------------

cdef inline int _mpi_active():
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

cdef inline void _atexit():
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
    # restore default error handlers for predefined communicators
    global comm_self_eh, comm_world_eh
    if comm_self_eh != MPI_ERRHANDLER_NULL:
        ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF,  comm_self_eh)
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
        if not ierr: return
    # We MUST NOT issue Python API calls at this point
    fflush(stderr)
    fprintf(stderr, "MPI_Finalize() failed [error code: %d]\n", ierr)
    fflush(stderr)

cdef inline int _init1() except -1:
    global comm_self_eh, comm_world_eh
    comm_self_eh  = MPI_ERRHANDLER_NULL
    comm_world_eh = MPI_ERRHANDLER_NULL
    # MPI initialized ?
    cdef int initialized = 0
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
    ierr = MPI_Init(NULL, NULL)
    if ierr: raise RuntimeError("MPI_Init() failed [error code: %d]" % ierr)
    if ierr: return -1 # not sure if Cython does this automatically
    # We initialized MPI, so it is owned and active at this point
    mpi_is_owned  = 1
    mpi_is_active = 1
    # then finalize it when Python process exits
    return Py_AtExit(_atexit)

# --------------------------------------------------------------------

cdef inline int _init2() except -1:
    cdef int ierr = 0
    if not _mpi_active(): return 0
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

cdef int active_keyval_del(MPI_Comm c,int k, void *v, void *xs):
    # MPI is no longer active
    global mpi_is_active
    mpi_is_active = 0
    # and we are done
    return 0

cdef inline int _init3() except -1:
    if not _mpi_active(): return 0
    cdef int ierr = 0
    cdef int keyval = MPI_KEYVAL_INVALID
    ierr = MPI_Comm_create_keyval(MPI_COMM_NULL_COPY_FN,
                                  active_keyval_del,
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
