# -----------------------------------------------------------------------------


@cython.final
@cython.internal
cdef class _p_rs:

    cdef int         count
    cdef MPI_Request *requests
    cdef MPI_Status  *status, _status[1]
    cdef MPI_Status  *statuses
    cdef int         outcount
    cdef int         *indices
    cdef object      arg_req
    cdef object      buf_req
    cdef object      buf_sts
    cdef object      buf_ids
    cdef MPI_Status  tmp_sts

    def __cinit__(self):
        self.count    = 0
        self.requests = NULL
        self.status   = MPI_STATUS_IGNORE
        self.statuses = MPI_STATUSES_IGNORE
        self.outcount = MPI_UNDEFINED
        self.indices  = NULL
        self.arg_req = None
        self.buf_req = None
        self.buf_sts = None
        self.buf_ids = None

    cdef int set_request(self, Request request) except -1:
        self.arg_req = request
        return 0

    cdef int set_status(self, Status status) except -1:
        if status is not None:
            self.status = &status.ob_mpi
        else:
            self.status = &self.tmp_sts
            <void>MPI_Status_set_source ( self.status, MPI_ANY_SOURCE )
            <void>MPI_Status_set_tag    ( self.status, MPI_ANY_TAG    )
            <void>MPI_Status_set_error  ( self.status, MPI_SUCCESS    )
        return 0

    cdef int set_requests(self, requests) except -1:
        self.arg_req = requests
        cdef Py_ssize_t count = len(requests)
        self.count = <int>count
        self.outcount = <int>count
        self.buf_req = allocate(self.count, sizeof(MPI_Request), &self.requests)
        for i in range(self.count):
            self.requests[i] = (<Request?>requests[i]).ob_mpi
        return 0

    cdef int add_statuses(self) except -1:
        cdef MPI_Status *status = &self.tmp_sts
        <void>MPI_Status_set_source ( status, MPI_ANY_SOURCE )
        <void>MPI_Status_set_tag    ( status, MPI_ANY_TAG    )
        <void>MPI_Status_set_error  ( status, MPI_SUCCESS    )
        self.buf_sts = allocate(self.count, sizeof(MPI_Status), &self.statuses)
        for i in range(self.count):
            self.statuses[i] = status[0]
        return 0

    cdef int add_indices(self) except -1:
        self.outcount = MPI_UNDEFINED
        self.buf_ids = newarray(self.count, &self.indices)
        return 0

    cdef int acquire(self, requests, statuses=None) except -1:
        self.set_requests(requests)
        if statuses is not None:
            self.add_statuses()
        return 0

    cdef int release(self, statuses=None) except -1:
        cdef Request request
        cdef Py_ssize_t nr = self.count
        for i in range(nr):
            request = <Request>self.arg_req[i]
            request.ob_mpi = self.requests[i]
            if request.ob_mpi == MPI_REQUEST_NULL:
                if request.ob_buf is not None:
                    request.ob_buf = None
        #
        if statuses is None:
            return 0
        if self.outcount == MPI_UNDEFINED:
            return 0
        cdef Py_ssize_t outcount = self.outcount
        cdef Py_ssize_t ns = len(statuses)
        if outcount > ns:
            if isinstance(statuses, list):
                statuses += [
                    <Status>New(Status)
                    for _ in range (ns, outcount)
                ]
                ns = outcount
        for i in range(min(nr, ns)):
            (<Status?>statuses[i]).ob_mpi = self.statuses[i]
        return 0

    cdef object get_buffer(self, Py_ssize_t index):
        cdef Request request
        if index >= 0:
            if self.indices != NULL:
                index = self.indices[index]
            request = <Request>self.arg_req[index]
        else:
            request = <Request>self.arg_req
        cdef object buf = request.ob_buf
        if request.ob_mpi == MPI_REQUEST_NULL:
            if request.ob_buf is not None:
                request.ob_buf = None
        return buf

    cdef object get_result(self):
        return self.get_object(-1)

    cdef object get_object(self, Py_ssize_t index):
        return PyMPI_load(self.get_buffer(index), self.status)

    cdef object get_objects(self):
        if self.outcount == MPI_UNDEFINED: return None
        return [
            PyMPI_load(self.get_buffer(i), &self.statuses[i])
            for i in range(self.outcount)
        ]

    cdef object get_indices(self):
        if self.outcount == MPI_UNDEFINED: return None
        return [self.indices[i] for i in range(self.outcount)]

# -----------------------------------------------------------------------------


@cython.final
@cython.internal
cdef class _p_greq:

    cdef object query_fn
    cdef object free_fn
    cdef object cancel_fn
    cdef tuple args
    cdef dict  kwargs

    def __cinit__(self, query_fn, free_fn, cancel_fn, args, kwargs):
        self.query_fn  = query_fn
        self.free_fn   = free_fn
        self.cancel_fn = cancel_fn
        self.args   = tuple(args)  if args   is not None else ()
        self.kwargs = dict(kwargs) if kwargs is not None else {}

    cdef int query(self, MPI_Status *status) except -1:
        <void>MPI_Status_set_source(status, MPI_ANY_SOURCE)
        <void>MPI_Status_set_tag(status, MPI_ANY_TAG)
        <void>MPI_Status_set_error(status, MPI_SUCCESS)
        <void>MPI_Status_set_elements_c(status, MPI_BYTE, 0)
        <void>MPI_Status_set_cancelled(status, 0)
        cdef Status sts = <Status>New(Status)
        if self.query_fn is not None:
            sts.ob_mpi = status[0]
            self.query_fn(sts, *self.args, **self.kwargs)
            status[0] = sts.ob_mpi
            if self.cancel_fn is None:
                <void>MPI_Status_set_cancelled(status, 0)
        return MPI_SUCCESS

    cdef int free(self) except -1:
        if self.free_fn is not None:
            self.free_fn(*self.args, **self.kwargs)
        return MPI_SUCCESS

    cdef int cancel(self, bint completed) except -1:
        if self.cancel_fn is not None:
            self.cancel_fn(completed, *self.args, **self.kwargs)
        return MPI_SUCCESS


cdef int greq_query(
    void *extra_state,
    MPI_Status *status,
) noexcept with gil:
    cdef _p_greq state = <_p_greq>extra_state
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        state.query(status)
    except BaseException as exc:
        ierr = PyMPI_HandleException(exc)
    return ierr


cdef int greq_free(
    void *extra_state,
) noexcept with gil:
    cdef _p_greq state = <_p_greq>extra_state
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        state.free()
    except BaseException as exc:
        ierr = PyMPI_HandleException(exc)
    finally:
        Py_DECREF(<object>extra_state)
    return ierr


cdef int greq_cancel(
    void *extra_state,
    int completed,
) noexcept with gil:
    cdef _p_greq state = <_p_greq>extra_state
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        state.cancel(completed)
    except BaseException as exc:
        ierr = PyMPI_HandleException(exc)
    return ierr


@cython.callspec("MPIAPI")
cdef int greq_query_fn(
    void *extra_state,
    MPI_Status *status,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if status == NULL:         return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_ERR_INTERN
    if not py_module_alive():  return MPI_ERR_INTERN
    return greq_query(extra_state, status)


@cython.callspec("MPIAPI")
cdef int greq_free_fn(
    void *extra_state,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_ERR_INTERN
    if not py_module_alive():  return MPI_ERR_INTERN
    return greq_free(extra_state)


@cython.callspec("MPIAPI")
cdef int greq_cancel_fn(
    void *extra_state,
    int completed,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_ERR_INTERN
    if not py_module_alive():  return MPI_ERR_INTERN
    return greq_cancel(extra_state, completed)


# -----------------------------------------------------------------------------
