cdef void win_memory_del(void *ob) with gil:
    if Py_IsInitialized():
        Py_DECREF(<object>ob)

cdef int keyval_win_memory_del(MPI_Win w, int k, void *v, void *xs) nogil:
    win_memory_del(v)
    return 0

cdef int PyMPI_Win_set_attr_memory(MPI_Win win, object memory) except -1:
    if memory is None: return 0
    # create keyval for memory object
    global PyMPI_KEYVAL_WIN_MEMORY
    if PyMPI_KEYVAL_WIN_MEMORY == MPI_KEYVAL_INVALID:
        CHKERR( MPI_Win_create_keyval(MPI_WIN_NULL_COPY_FN,
                                      keyval_win_memory_del,
                                      &PyMPI_KEYVAL_WIN_MEMORY, NULL) )
    # hold a reference to the object exposing windows memory
    CHKERR( MPI_Win_set_attr(win, PyMPI_KEYVAL_WIN_MEMORY, <void*>memory) )
    Py_INCREF(memory)
    return 0
