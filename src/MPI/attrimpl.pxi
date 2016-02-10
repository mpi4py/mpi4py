#------------------------------------------------------------------------------

@cython.final
@cython.internal
cdef class _p_keyval:
    cdef object copy_fn
    cdef object delete_fn
    def __cinit__(self, copy_fn, delete_fn):
        if copy_fn   is False: copy_fn   = None
        if delete_fn is False: delete_fn = None
        if delete_fn is True:  delete_fn = None
        self.copy_fn   = copy_fn
        self.delete_fn = delete_fn

cdef dict type_keyval = {}
cdef dict comm_keyval = {}
cdef dict win_keyval  = {}

#------------------------------------------------------------------------------

ctypedef fused PyMPI_attr_type:
    MPI_Datatype
    MPI_Comm
    MPI_Win

cdef inline object PyMPI_attr_call(
    object function,
    PyMPI_attr_type hdl,
    int keyval,
    object attrval):
    cdef object ob
    if PyMPI_attr_type is MPI_Datatype:
        ob = new_Datatype(hdl)
    if PyMPI_attr_type is MPI_Comm:
        ob = new_Comm(hdl)
    if PyMPI_attr_type is MPI_Win:
        ob = new_Win (hdl)
    try:
        attrval = function(ob, keyval, attrval)
    finally:
        if PyMPI_attr_type is MPI_Datatype:
            (<Datatype>ob).ob_mpi = MPI_DATATYPE_NULL
        if PyMPI_attr_type is MPI_Comm:
            (<Comm>ob).ob_mpi = MPI_COMM_NULL
        if PyMPI_attr_type is MPI_Win:
            (<Win>ob).ob_mpi = MPI_WIN_NULL
    return attrval

cdef inline int PyMPI_attr_copy(
    PyMPI_attr_type hdl,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag) except -1:
    cdef _p_keyval state = <_p_keyval>extra_state
    if state.copy_fn is None:
        flag[0] = 0
        return 0
    cdef object attrval = <object>attrval_in
    if state.copy_fn is not True:
        attrval = PyMPI_attr_call(state.copy_fn, hdl, keyval, attrval)
    (<void **>attrval_out)[0] = <void *>attrval
    flag[0] = 1
    Py_INCREF(attrval)
    Py_INCREF(state)
    return 0

cdef inline int PyMPI_attr_delete(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval_in,
    void *extra_state) except -1:
    cdef _p_keyval state = <_p_keyval>extra_state
    cdef object attrval = <object>attrval_in
    if state.delete_fn is not None:
        PyMPI_attr_call(state.delete_fn, hdl, keyval, attrval)
    Py_DECREF(attrval)
    Py_DECREF(state)
    return 0

cdef inline int PyMPI_attr_copy_cb(
    PyMPI_attr_type hdl,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag,
    ) except MPI_ERR_UNKNOWN with gil:
    cdef object exc
    try:
        PyMPI_attr_copy(hdl, keyval, extra_state,
                        attrval_in, attrval_out, flag)
    except MPIException as exc:
        print_traceback()
        return exc.Get_error_code()
    except:
        print_traceback()
        return MPI_ERR_OTHER
    return MPI_SUCCESS

cdef inline int PyMPI_attr_delete_cb(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval,
    void *extra_state,
    ) except MPI_ERR_UNKNOWN with gil:
    cdef object exc
    try:
        PyMPI_attr_delete(hdl, keyval, attrval, extra_state)
    except MPIException as exc:
        print_traceback()
        return exc.Get_error_code()
    except:
        print_traceback()
        return MPI_ERR_OTHER
    return MPI_SUCCESS


@cython.callspec("MPIAPI")
cdef int PyMPI_attr_copy_fn(PyMPI_attr_type hdl,
                          int keyval,
                          void *extra_state,
                          void *attrval_in,
                          void *attrval_out,
                          int *flag) nogil:
    if extra_state == NULL: return MPI_ERR_INTERN
    if attrval_in  == NULL: return MPI_ERR_INTERN
    if attrval_out == NULL: return MPI_ERR_INTERN
    flag[0] = 0
    if not Py_IsInitialized(): return MPI_SUCCESS
    return PyMPI_attr_copy_cb(hdl, keyval, extra_state,
                            attrval_in, attrval_out, flag)

@cython.callspec("MPIAPI")
cdef int PyMPI_attr_delete_fn(PyMPI_attr_type hdl,
                            int keyval,
                            void *attrval,
                            void *extra_state) nogil:
    if extra_state == NULL: return MPI_ERR_INTERN
    if attrval     == NULL: return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_SUCCESS
    return PyMPI_attr_delete_cb(hdl, keyval, attrval, extra_state)

#------------------------------------------------------------------------------

cdef inline _p_keyval PyMPI_attr_state(
    PyMPI_attr_type hdl,
    int keyval):
    <void>hdl # unused
    if PyMPI_attr_type is MPI_Datatype:
        return <_p_keyval>type_keyval.get(keyval)
    elif PyMPI_attr_type is MPI_Comm:
        return <_p_keyval>comm_keyval.get(keyval)
    elif PyMPI_attr_type is MPI_Win:
        return <_p_keyval>win_keyval.get(keyval)

cdef inline object PyMPI_attr_get(
    PyMPI_attr_type hdl,
    int keyval,
    void *attrval):
    cdef _p_keyval state = PyMPI_attr_state(hdl, keyval)
    if state is not None:
        return <object>attrval
    else:
        return PyLong_FromVoidPtr(attrval)

cdef inline int PyMPI_attr_set(
    PyMPI_attr_type hdl,
    int keyval,
    object attrval,
    ) except -1:
    cdef _p_keyval state = PyMPI_attr_state(hdl, keyval)
    cdef void *ptrval = NULL
    if state is not None:
        ptrval = <void *>attrval
    else:
        ptrval = PyLong_AsVoidPtr(attrval)
    if PyMPI_attr_type is MPI_Datatype:
        CHKERR( MPI_Type_set_attr(hdl, keyval, ptrval) )
    if PyMPI_attr_type is MPI_Comm:
        CHKERR( MPI_Comm_set_attr(hdl, keyval, ptrval) )
    if PyMPI_attr_type is MPI_Win:
        CHKERR( MPI_Win_set_attr(hdl, keyval, ptrval) )
    if state is not None:
        Py_INCREF(attrval)
        Py_INCREF(state)
    return 0

#------------------------------------------------------------------------------
