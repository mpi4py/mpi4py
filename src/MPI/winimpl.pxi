cdef int PyMPI_WIN_MEMORY = MPI_KEYVAL_INVALID

cdef void win_memory_del(void *ob) with gil:
    Py_DECREF(<object>ob)

cdef int win_keyval_memory_del(MPI_Win w, int k, void *v, void *s) nogil:
    if Py_IsInitialized():
        win_memory_del(v)
    return 0

cdef int PyMPI_Win_set_attr_memory(MPI_Win win, object memory) except -1:
    if memory is None: return 0
    # create keyval for memory object
    if PyMPI_WIN_MEMORY == MPI_KEYVAL_INVALID:
        CHKERR( MPI_Win_create_keyval(MPI_WIN_NULL_COPY_FN,
                                      win_keyval_memory_del,
                                      &PyMPI_WIN_MEMORY, NULL) )
    # hold a reference to the object exposing memory
    CHKERR( MPI_Win_set_attr(win, PyMPI_WIN_MEMORY, <void*>memory) )
    Py_INCREF(memory)
    return 0
