cdef class _p_greq:

    cdef object query_fn
    cdef object free_fn
    cdef object cancel_fn
    cdef object args, kargs

    def __cinit__(self, query_fn, free_fn, cancel_fn,
                  args=None, kargs=None):
        self.query_fn  = query_fn
        self.free_fn   = free_fn
        self.cancel_fn = cancel_fn
        self.args  = tuple(args) if args  is not None else ()
        self.kargs = dict(kargs) if kargs is not None else {}

    cdef int query(self, MPI_Status *status) except -1:
        cdef Status sts = Status()
        if self.query_fn is not None:
            self.query_fn(sts, *self.args, **self.kargs)
        memcpy(status, &sts.ob_mpi, sizeof(MPI_Status))
        return MPI_SUCCESS

    cdef int free(self) except -1:
        if self.free_fn is not None:
            self.free_fn(*self.args, **self.kargs)
        return MPI_SUCCESS

    cdef int cancel(self, bint completed) except -1:
        if self.cancel_fn is not None:
            self.cancel_fn(completed, *self.args, **self.kargs)
        elif not completed:
            return MPI_ERR_PENDING
        return MPI_SUCCESS


cdef int greq_query_fn(void *extra_state, MPI_Status *status) with gil:
    cdef _p_greq state = <_p_greq>extra_state
    try:
        return state.query(status)
    except Exception, exc:
        return exc.Get_error_code()
    except:
        return MPI_ERR_UNKNOWN

cdef int greq_free_fn(void *extra_state) with gil:
    cdef _p_greq state = <object>extra_state
    try:
        return state.free()
    except Exception, exc:
        return exc.Get_error_code()
    except:
        return MPI_ERR_UNKNOWN

cdef int greq_cancel_fn(void *extra_state, int completed) with gil:
    cdef _p_greq state = <object>extra_state
    try:
        return state.cancel(completed)
    except Exception, exc:
        return exc.Get_error_code()
    except:
        return MPI_ERR_UNKNOWN
