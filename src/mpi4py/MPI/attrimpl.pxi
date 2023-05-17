#------------------------------------------------------------------------------

cdef extern from "Python.h":
    void Py_INCREF(object)
    void Py_DECREF(object)

#------------------------------------------------------------------------------

@cython.final
@cython.internal
cdef class _p_keyval:
    cdef public object copy_fn
    cdef public object delete_fn
    cdef public bint   nopython
    def __cinit__(self, copy_fn, delete_fn, nopython):
        if copy_fn   is False: copy_fn   = None
        if delete_fn is False: delete_fn = None
        if delete_fn is True:  delete_fn = None
        self.copy_fn   = copy_fn
        self.delete_fn = delete_fn
        self.nopython  = nopython

cdef object keyval_lock_type = Lock()
cdef object keyval_lock_comm = Lock()
cdef object keyval_lock_win  = Lock()

cdef dict   keyval_registry_type = {}
cdef dict   keyval_registry_comm = {}
cdef dict   keyval_registry_win  = {}

_keyval_registry = {
    'Datatype' : keyval_registry_type,
    'Comm'     : keyval_registry_comm,
    'Win'      : keyval_registry_win,
}

#------------------------------------------------------------------------------

ctypedef fused PyMPI_attr_type:
    MPI_Datatype
    MPI_Comm
    MPI_Win


cdef inline object PyMPI_attr_call(
    object function,
    PyMPI_attr_type hdl,
    int keyval,
    object attrval,
):
    cdef object handle
    cdef object result
    if PyMPI_attr_type is MPI_Datatype:
        handle = PyMPIDatatype_New(hdl)
    if PyMPI_attr_type is MPI_Comm:
        handle = PyMPIComm_New(hdl)
    if PyMPI_attr_type is MPI_Win:
        handle = PyMPIWin_New(hdl)
    try:
        result = function(handle, keyval, attrval)
    finally:
        if False: pass
        elif PyMPI_attr_type is MPI_Datatype:
            (<Datatype>handle).ob_mpi = MPI_DATATYPE_NULL
        elif PyMPI_attr_type is MPI_Comm:
            (<Comm>handle).ob_mpi = MPI_COMM_NULL
        elif PyMPI_attr_type is MPI_Win:
            (<Win>handle).ob_mpi = MPI_WIN_NULL
    return result


cdef inline int PyMPI_attr_copy(
    PyMPI_attr_type hdl,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag,
) except -1:
    if flag != NULL: flag[0] = 0
    cdef _p_keyval state = <_p_keyval>extra_state
    if state.copy_fn is None: return 0
    cdef int p = not state.nopython
    if p and attrval_in == NULL: raise RuntimeError
    cdef object attrval
    if p: attrval = <object>attrval_in
    else: attrval = PyLong_FromVoidPtr(attrval_in)
    if state.copy_fn is not True:
        attrval = PyMPI_attr_call(state.copy_fn, hdl, keyval, attrval)
        if attrval is NotImplemented: return 0
    cdef void **outval = <void **>attrval_out
    if p: outval[0] = <void *>attrval
    else: outval[0] = PyLong_AsVoidPtr(attrval)
    if flag != NULL: flag[0] = 1
    if p: Py_INCREF(attrval)
    Py_INCREF(state)
    return 0


cdef inline int PyMPI_attr_delete(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval_in,
    void *extra_state,
) except -1:
    cdef _p_keyval state = <_p_keyval>extra_state
    cdef int p = not state.nopython
    if p and attrval_in == NULL: raise RuntimeError
    cdef object attrval
    if p: attrval = <object>attrval_in
    else: attrval = PyLong_FromVoidPtr(attrval_in)
    if state.delete_fn is not None:
        PyMPI_attr_call(state.delete_fn, hdl, keyval, attrval)
    if p: Py_DECREF(attrval)
    Py_DECREF(state)
    return 0

# ---

cdef inline int PyMPI_attr_copy_cb(
    PyMPI_attr_type hdl,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag,
) noexcept with gil:
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        PyMPI_attr_copy(
            hdl, keyval, extra_state,
            attrval_in, attrval_out, flag,
        )
    except BaseException as exc:           #> TODO
        ierr = PyMPI_HandleException(exc)  #> TODO
    return ierr


cdef inline int PyMPI_attr_delete_cb(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval,
    void *extra_state,
) noexcept with gil:
    cdef int ierr = MPI_SUCCESS
    cdef object exc
    try:
        PyMPI_attr_delete(
            hdl, keyval, attrval, extra_state,
        )
    except BaseException as exc:           #> TODO
        ierr = PyMPI_HandleException(exc)  #> TODO
    return ierr

# ---

@cython.callspec("MPIAPI")
cdef int PyMPI_attr_copy_fn(
    PyMPI_attr_type hdl,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag,
) noexcept nogil:
    if flag != NULL: flag[0] = 0
    if extra_state == NULL:    return MPI_ERR_INTERN
    if attrval_out == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_SUCCESS
    if not py_module_alive():  return MPI_SUCCESS
    return PyMPI_attr_copy_cb(
        hdl, keyval, extra_state,
        attrval_in, attrval_out, flag,
    )


@cython.callspec("MPIAPI")
cdef int PyMPI_attr_delete_fn(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval,
    void *extra_state,
) noexcept nogil:
    if extra_state == NULL:    return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_SUCCESS
    if not py_module_alive():  return MPI_SUCCESS
    return PyMPI_attr_delete_cb(
        hdl, keyval, attrval, extra_state
    )

# ---

cdef inline _p_keyval PyMPI_attr_state_get(
    PyMPI_attr_type hdl,
    int keyval,
):
    <void> hdl # unused
    if PyMPI_attr_type is MPI_Datatype:
        with keyval_lock_type:
            return <_p_keyval>keyval_registry_type.get(keyval)
    if PyMPI_attr_type is MPI_Comm:
        with keyval_lock_comm:
            return <_p_keyval>keyval_registry_comm.get(keyval)
    if PyMPI_attr_type is MPI_Win:
        with keyval_lock_win:
            return <_p_keyval>keyval_registry_win.get(keyval)


cdef inline int PyMPI_attr_state_set(
    PyMPI_attr_type hdl,
    int keyval,
    _p_keyval state,
) except -1:
    <void> hdl # unused
    if PyMPI_attr_type is MPI_Datatype:
        with keyval_lock_type:
            keyval_registry_type[keyval] = state
    if PyMPI_attr_type is MPI_Comm:
        with keyval_lock_comm:
            keyval_registry_comm[keyval] = state
    if PyMPI_attr_type is MPI_Win:
        with keyval_lock_win:
            keyval_registry_win[keyval] = state
    return 0


cdef inline int PyMPI_attr_state_del(
    PyMPI_attr_type hdl,
    int keyval,
) except -1:
    <void> hdl # unused
    try:
        if PyMPI_attr_type is MPI_Datatype:
            with keyval_lock_type:
                del keyval_registry_type[keyval]
        if PyMPI_attr_type is MPI_Comm:
            with keyval_lock_comm:
                del keyval_registry_comm[keyval]
        if PyMPI_attr_type is MPI_Win:
            with keyval_lock_win:
                del keyval_registry_win[keyval]
    except KeyError:  #> no cover
        pass
    return 0

# ---

cdef inline object PyMPI_attr_get(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval,
):
    cdef _p_keyval state = PyMPI_attr_state_get(hdl, keyval)
    if state is not None and not state.nopython:
        return <object>attrval
    else:
        return PyLong_FromVoidPtr(attrval)


cdef inline int PyMPI_attr_set(
    PyMPI_attr_type hdl,
    int keyval,
    object attrval,
) except -1:
    cdef _p_keyval state = PyMPI_attr_state_get(hdl, keyval)
    cdef void *valptr = NULL
    if state is not None and not state.nopython:
        valptr = <void *>attrval
    else:
        valptr = PyLong_AsVoidPtr(attrval)
    if PyMPI_attr_type is MPI_Datatype:
        CHKERR( MPI_Type_set_attr(hdl, keyval, valptr) )
    if PyMPI_attr_type is MPI_Comm:
        CHKERR( MPI_Comm_set_attr(hdl, keyval, valptr) )
    if PyMPI_attr_type is MPI_Win:
        CHKERR( MPI_Win_set_attr(hdl, keyval, valptr) )
    if state is not None:
        if not state.nopython:
            Py_INCREF(attrval)
        Py_INCREF(state)
    return 0

#------------------------------------------------------------------------------
