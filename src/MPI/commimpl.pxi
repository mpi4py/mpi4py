# -----------------------------------------------------------------------------

cdef dict comm_keyval = {}

cdef int comm_keyval_new(int keyval,
                         object copy_fn,object delete_fn) except -1:
    comm_keyval[keyval] = (copy_fn, delete_fn)
    return 0

cdef int comm_keyval_del(int keyval) except -1:
    try: del comm_keyval[keyval]
    except KeyError: pass
    return 0

cdef int comm_attr_copy(
    MPI_Comm comm,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag) except -1:
    cdef tuple entry = comm_keyval.get(keyval)
    cdef object copy_fn = None
    if entry is not None: copy_fn = entry[0]
    if copy_fn is None or copy_fn is False:
        flag[0] = 0
        return 0
    cdef object attrval = <object>attrval_in
    cdef void **aptr = <void **>attrval_out
    if copy_fn is not True:
        attrval = copy_fn(attrval)
    Py_INCREF(attrval)
    aptr[0] = <void*>attrval
    flag[0] = 1
    return 0

cdef int comm_attr_copy_cb(
    MPI_Comm comm,
    int keyval,
    void *extra_state,
    void *attrval_in,
    void *attrval_out,
    int *flag) with gil:
    cdef object exc
    try:
        comm_attr_copy(comm, keyval, extra_state,
                       attrval_in, attrval_out, flag)
    except MPIException, exc:
        print_traceback()
        return exc.Get_error_code()
    except:
        print_traceback()
        return MPI_ERR_OTHER
    return MPI_SUCCESS

cdef int comm_attr_delete(
    MPI_Comm comm,
    int keyval,
    void *attrval,
    void *extra_state) except -1:
    cdef tuple entry = comm_keyval.get(keyval)
    cdef object delete_fn = None
    if entry is not None: delete_fn = entry[1]
    if delete_fn is not None:
        delete_fn(<object>attrval)
    Py_DECREF(<object>attrval)
    return 0

cdef int comm_attr_delete_cb(
    MPI_Comm comm,
    int keyval,
    void *attrval,
    void *extra_state) with gil:
    cdef object exc
    try:
        comm_attr_delete(comm, keyval, attrval, extra_state)
    except MPIException, exc:
        print_traceback()
        return exc.Get_error_code()
    except:
        print_traceback()
        return MPI_ERR_OTHER
    return MPI_SUCCESS

@cython.callspec("PyMPIAPI")
cdef int comm_attr_copy_fn(MPI_Comm comm,
                           int keyval,
                           void *extra_state,
                           void *attrval_in,
                           void *attrval_out,
                           int *flag) nogil:
    if attrval_in == NULL:  return MPI_ERR_INTERN
    if attrval_out == NULL: return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_SUCCESS
    return comm_attr_copy_cb(comm, keyval, extra_state,
                             attrval_in, attrval_out, flag)

@cython.callspec("PyMPIAPI")
cdef int comm_attr_delete_fn(MPI_Comm comm,
                             int keyval,
                             void *attrval,
                             void *extra_state) nogil:
    if attrval == NULL: return MPI_ERR_INTERN
    if not Py_IsInitialized(): return MPI_SUCCESS
    return comm_attr_delete_cb(comm, keyval, attrval, extra_state)

# -----------------------------------------------------------------------------

cdef _p_buffer _buffer = None

cdef inline int attach_buffer(ob, void **p, int *n) except -1:
    global _buffer
    cdef void *bptr = NULL
    cdef MPI_Aint blen = 0
    _buffer = getbuffer_w(ob, &bptr, &blen)
    p[0] = bptr
    n[0] = <int>blen # XXX Overflow ?
    return 0

cdef inline object detach_buffer(void *p, int n):
    global _buffer
    cdef object ob = None
    try:
        if (_buffer is not None and
            _buffer.view.buf == p and
            _buffer.view.len == <Py_ssize_t>n and
            _buffer.view.obj != NULL):
            ob = <object>_buffer.view.obj
        else:
            ob = tomemory(p, <MPI_Aint>n)
    finally:
        _buffer = None
    return ob

# -----------------------------------------------------------------------------

cdef object __UNWEIGHTED__    = <MPI_Aint>MPI_UNWEIGHTED

cdef object __WEIGHTS_EMPTY__ = <MPI_Aint>MPI_WEIGHTS_EMPTY

cdef object asarray_weights(object weights, int nweight, int **iweight):
    #
    if weights is None:
        iweight[0] = MPI_UNWEIGHTED
        return None
    #
    if weights is __WEIGHTS_EMPTY__:
        if MPI_WEIGHTS_EMPTY != MPI_UNWEIGHTED:
            iweight[0] = MPI_WEIGHTS_EMPTY
            return None
        else:
            return newarray_int(nweight, iweight)
    #
    if weights is __UNWEIGHTED__:
        iweight[0] = MPI_UNWEIGHTED
        return None
    #
    return chkarray_int(weights, nweight, iweight)

# -----------------------------------------------------------------------------

cdef inline int comm_neighbors_count(MPI_Comm comm,
                                     int *incoming,
                                     int *outgoing,
                                     ) except -1:
    cdef int topo = MPI_UNDEFINED
    cdef int size=0, ndims=0, rank=0, nneighbors=0
    cdef int indegree=0, outdegree=0, weighted=0
    CHKERR( MPI_Topo_test(comm, &topo) )
    if topo == <int>MPI_UNDEFINED: # XXX
        CHKERR( MPI_Comm_size(comm, &size) )
        indegree = outdegree = size
    elif topo == <int>MPI_CART:
        CHKERR( MPI_Cartdim_get(comm, &ndims) )
        indegree = outdegree = 2*ndims
    elif topo == <int>MPI_GRAPH:
        CHKERR( MPI_Comm_rank(comm, &rank) )
        CHKERR( MPI_Graph_neighbors_count(
                comm, rank, &nneighbors) )
        indegree = outdegree = nneighbors
    elif topo == <int>MPI_DIST_GRAPH:
        CHKERR( MPI_Dist_graph_neighbors_count(
                comm, &indegree, &outdegree, &weighted) )
    if incoming != NULL: incoming[0] = indegree
    if outgoing != NULL: outgoing[0] = outdegree
    return 0

# -----------------------------------------------------------------------------
