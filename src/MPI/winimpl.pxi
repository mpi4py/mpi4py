# -----------------------------------------------------------------------------

cdef extern from *:
    int PyMPI_KEYVAL_WIN_MEMORY

cdef void win_memory_decref(void *ob) with gil:
    Py_DECREF(<object>ob)

@cython.callspec("MPIAPI")
cdef int win_memory_del(MPI_Win w, int k, void *v, void *xs) nogil:
    if v != NULL:
        if Py_IsInitialized():
            win_memory_decref(v)
    return MPI_SUCCESS

cdef int PyMPI_Win_set_memory(MPI_Win win, object memory):
    if memory is None: return MPI_SUCCESS
    # hold a reference to memory
    cdef int ierr = MPI_SUCCESS
    if PyMPI_KEYVAL_WIN_MEMORY == MPI_KEYVAL_INVALID:
        ierr = MPI_Win_create_keyval(MPI_WIN_NULL_COPY_FN, win_memory_del,
                                     &PyMPI_KEYVAL_WIN_MEMORY, NULL)
        if ierr: return ierr
    ierr = MPI_Win_set_attr(win, PyMPI_KEYVAL_WIN_MEMORY, <void*>memory)
    if ierr: return ierr
    Py_INCREF(memory)
    return MPI_SUCCESS

cdef object PyMPI_Win_get_memory(MPI_Win win):
    cdef int flag = 0
    cdef void *attr = NULL
    if PyMPI_KEYVAL_WIN_MEMORY != MPI_KEYVAL_INVALID:
        CHKERR( MPI_Win_get_attr(win, PyMPI_KEYVAL_WIN_MEMORY, &attr, &flag) )
        if flag and attr != NULL: return <object>attr
    return None

# -----------------------------------------------------------------------------

cdef dict win_keyval = {}

cdef inline int win_keyval_new(int keyval,
                               object copy_fn,object delete_fn) except -1:
    win_keyval[keyval] = (copy_fn, delete_fn)
    return 0

cdef inline int win_keyval_del(int keyval) except -1:
    try: del win_keyval[keyval]
    except KeyError: pass
    return 0

cdef inline Win newwin(MPI_Win ob):
    cdef Win win = <Win>Win.__new__(Win)
    win.ob_mpi = ob
    return win

cdef int win_attr_copy(
    MPI_Win win,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag) except -1:
    cdef tuple entry = win_keyval.get(keyval)
    cdef object copy_fn = None
    if entry is not None: copy_fn = entry[0]
    if copy_fn is None or copy_fn is False:
        flag[0] = 0
        return 0
    cdef object attrval = <object>attrval_in
    cdef void **aptr = <void **>attrval_out
    if copy_fn is not True:
        attrval = copy_fn(newwin(win), keyval, attrval)
    Py_INCREF(attrval)
    aptr[0] = <void*>attrval
    flag[0] = 1
    return 0

cdef int win_attr_copy_cb(
    MPI_Win win,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag) with gil:
    cdef object exc
    try:
        win_attr_copy(win, keyval, extra_state,
                       attrval_in, attrval_out, flag)
    except MPIException as exc:
        print_traceback()
        return exc.Get_error_code()
    except:
        print_traceback()
        return MPI_ERR_OTHER
    return MPI_SUCCESS

cdef int win_attr_delete(
    MPI_Win win,
    int keyval,
    void *attrval,
    void *extra_state) except -1:
    cdef tuple entry = win_keyval.get(keyval)
    cdef object delete_fn = None
    if entry is not None: delete_fn = entry[1]
    if delete_fn is not None:
        delete_fn(newwin(win), keyval, <object>attrval)
    Py_DECREF(<object>attrval)
    return 0

cdef int win_attr_delete_cb(
    MPI_Win win,
    int keyval,
    void *attrval,
    void *extra_state) with gil:
    cdef object exc
    try:
        win_attr_delete(win, keyval, attrval, extra_state)
    except MPIException as exc:
        print_traceback()
        return exc.Get_error_code()
    except:
        print_traceback()
        return MPI_ERR_OTHER
    return MPI_SUCCESS

@cython.callspec("MPIAPI")
cdef int win_attr_copy_fn(MPI_Win win,
                          int keyval,
                          void *extra_state,
                          void *attrval_in,
                          void *attrval_out,
                          int *flag) nogil:
    if attrval_in  == NULL: return MPI_ERR_INTERN
    if attrval_out == NULL: return MPI_ERR_INTERN
    if not Py_IsInitialized():
        flag[0] = 0
        return MPI_SUCCESS
    return win_attr_copy_cb(win, keyval, extra_state,
                            attrval_in, attrval_out, flag)

@cython.callspec("MPIAPI")
cdef int win_attr_delete_fn(MPI_Win win,
                            int keyval,
                            void *attrval,
                            void *extra_state) nogil:
    if attrval == NULL: return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_SUCCESS
    return win_attr_delete_cb(win, keyval, attrval, extra_state)

# -----------------------------------------------------------------------------
