# ---

cdef class _p_greq:

    cdef object query_fn
    cdef object free_fn
    cdef object cancel_fn
    cdef tuple args
    cdef dict  kargs

    def __cinit__(self, query_fn, free_fn, cancel_fn, args, kargs):
        self.query_fn  = query_fn
        self.free_fn   = free_fn
        self.cancel_fn = cancel_fn
        self.args  = tuple(args) if args  is not None else ()
        self.kargs = dict(kargs) if kargs is not None else {}

    cdef int query(self, MPI_Status *status) except -1:
        status.MPI_SOURCE = MPI_ANY_SOURCE
        status.MPI_TAG = MPI_ANY_TAG
        MPI_Status_set_elements(status, MPI_BYTE, 0)
        MPI_Status_set_cancelled(status, 0)
        cdef Status sts = Status()
        if self.query_fn is not None:
            sts.ob_mpi = status[0]
            self.query_fn(sts, *self.args, **self.kargs)
            status[0] = sts.ob_mpi
            if self.cancel_fn is None:
                MPI_Status_set_cancelled(status, 0)
        return MPI_SUCCESS

    cdef int free(self) except -1:
        if self.free_fn is not None:
            self.free_fn(*self.args, **self.kargs)
        return MPI_SUCCESS

    cdef int cancel(self, bint completed) except -1:
        if self.cancel_fn is not None:
            self.cancel_fn(completed, *self.args, **self.kargs)
        return MPI_SUCCESS

# ---

cdef int greq_query(void *extra_state, MPI_Status *status) with gil:
    cdef _p_greq state = <_p_greq>extra_state
    cdef int ierr = MPI_SUCCESS
    try:
        ierr = state.query(status)
    except MPIException, exc:
        ierr = exc.Get_error_code()
    except:
        ierr = MPI_ERR_OTHER
    return ierr

cdef int greq_free(void *extra_state) with gil:
    cdef _p_greq state = <object>extra_state
    cdef int ierr = MPI_SUCCESS
    try:
        ierr = state.free()
    except MPIException, exc:
        ierr = exc.Get_error_code()
    except:
        ierr = MPI_ERR_OTHER
    Py_DECREF(<object>extra_state)
    return ierr

cdef int greq_cancel(void *extra_state, int completed) with gil:
    cdef _p_greq state = <object>extra_state
    cdef int ierr = MPI_SUCCESS
    try:
        ierr = state.cancel(completed)
    except MPIException, exc:
        ierr = exc.Get_error_code()
    except:
        ierr = MPI_ERR_OTHER
    return ierr

# ---

@cython.callspec("PyMPI_API_CALL")
cdef int greq_query_fn(void *extra_state, MPI_Status *status) nogil:
    if extra_state == NULL:
        return MPI_ERR_INTERN
    if status == NULL:
        return MPI_ERR_INTERN
    if not Py_IsInitialized():
        return MPI_ERR_INTERN
    return greq_query(extra_state, status)

@cython.callspec("PyMPI_API_CALL")
cdef int greq_free_fn(void *extra_state) nogil:
    if extra_state == NULL:
        return MPI_ERR_INTERN
    if not Py_IsInitialized():
        return MPI_ERR_INTERN
    return greq_free(extra_state)

@cython.callspec("PyMPI_API_CALL")
cdef int greq_cancel_fn(void *extra_state, int completed) nogil:
    if extra_state == NULL:
        return MPI_ERR_INTERN
    if not Py_IsInitialized():
        return MPI_ERR_INTERN
    return greq_cancel(extra_state, completed)

# ---
