# -----------------------------------------------------------------------------

cdef memory _buffer = None

cdef inline int attach_buffer(ob, void **p, int *n) except -1:
    global _buffer
    cdef void *bptr = NULL
    cdef MPI_Aint blen = 0
    _buffer = getbuffer_w(ob, &bptr, &blen)
    p[0] = bptr
    n[0] = clipcount(blen)
    return 0

cdef inline object detach_buffer(void *p, int n):
    global _buffer
    cdef object ob = None
    try:
        if (_buffer is not None and
            _buffer.view.buf == p and
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
    if weights is None:
        iweight[0] = MPI_UNWEIGHTED
        return None
    if weights is __UNWEIGHTED__:
        iweight[0] = MPI_UNWEIGHTED
        return None
    if weights is __WEIGHTS_EMPTY__:
        if nweight > 0: raise ValueError("empty weights but nonzero degree")
        iweight[0] = MPI_WEIGHTS_EMPTY
        return None
    return chkarray(weights, nweight, iweight)

# -----------------------------------------------------------------------------

cdef inline int comm_neighbors_count(MPI_Comm comm,
                                     int *incoming,
                                     int *outgoing,
                                     ) except -1:
    cdef int topo = MPI_UNDEFINED
    cdef int size=0, ndims=0, rank=0, nneighbors=0
    cdef int indegree=0, outdegree=0, weighted=0
    CHKERR( MPI_Topo_test(comm, &topo) )
    if topo == MPI_UNDEFINED: # XXX
        CHKERR( MPI_Comm_size(comm, &size) )
        indegree = outdegree = size
    elif topo == MPI_CART:
        CHKERR( MPI_Cartdim_get(comm, &ndims) )
        indegree = outdegree = <int>2*ndims
    elif topo == MPI_GRAPH:
        CHKERR( MPI_Comm_rank(comm, &rank) )
        CHKERR( MPI_Graph_neighbors_count(
                comm, rank, &nneighbors) )
        indegree = outdegree = nneighbors
    elif topo == MPI_DIST_GRAPH:
        CHKERR( MPI_Dist_graph_neighbors_count(
                comm, &indegree, &outdegree, &weighted) )
    if incoming != NULL: incoming[0] = indegree
    if outgoing != NULL: outgoing[0] = outdegree
    return 0

# -----------------------------------------------------------------------------

cdef object allocate_lock = None
if PY_MAJOR_VERSION >= 3:
    try:
        from _thread import allocate_lock
    except ImportError:
        from _dummy_thread import allocate_lock
else:
    try:
        from thread  import allocate_lock
    except ImportError:
        from dummy_thread import allocate_lock

cdef int  lock_keyval     = MPI_KEYVAL_INVALID
cdef dict lock_comm_null  = {}
cdef dict lock_comm_self  = {}
cdef dict lock_comm_world = {}

cdef inline void lock_free_cb(void *attrval) with gil:
    Py_DECREF(<object>attrval)

@cython.callspec("MPIAPI")
cdef int lock_free_fn(MPI_Comm comm, int keyval,
                      void *attrval, void *xstate) nogil:
    if Py_IsInitialized():
        if attrval != NULL: lock_free_cb(attrval)
    if comm == MPI_COMM_SELF:
        return MPI_Comm_free_keyval(&lock_keyval)
    return MPI_SUCCESS

cdef inline dict PyMPI_Lock_table(MPI_Comm comm):
    if comm == MPI_COMM_NULL:
        return lock_comm_null
    if comm == MPI_COMM_SELF:
        return lock_comm_self
    if comm == MPI_COMM_WORLD:
        return lock_comm_world
    if lock_keyval == MPI_KEYVAL_INVALID:
        CHKERR( MPI_Comm_create_keyval(
            MPI_COMM_NULL_COPY_FN, lock_free_fn, &lock_keyval, NULL) )
        CHKERR( MPI_Comm_set_attr(MPI_COMM_SELF, lock_keyval, NULL) )
    cdef dict  table
    cdef int   flag    = 0
    cdef void *attrval = NULL
    CHKERR( MPI_Comm_get_attr(comm, lock_keyval, &attrval, &flag) )
    if not flag:
        table = {}
        CHKERR( MPI_Comm_set_attr(comm, lock_keyval, <void*> table) )
        Py_INCREF(table)
    else:
        table = <dict> attrval
    return table

cdef inline object PyMPI_Lock(MPI_Comm comm, object key):
    cdef dict   table = PyMPI_Lock_table(comm)
    cdef object lock
    try:
        lock = table[key]
    except KeyError:
        lock = table[key] = allocate_lock()
    return lock

def _lock_table(Comm comm not None):
    "Internal communicator lock table"
    return PyMPI_Lock_table(comm.ob_mpi)

# -----------------------------------------------------------------------------
