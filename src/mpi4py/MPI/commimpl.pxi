# -----------------------------------------------------------------------------

# Legacy ULFM interface

cdef extern from * nogil:
    int MPIX_Comm_failure_ack(MPI_Comm)
    int MPIX_Comm_failure_get_acked(MPI_Comm, MPI_Group*)

# -----------------------------------------------------------------------------

cdef memory _buffer = None

cdef inline int attach_buffer(ob, void **p, MPI_Count *n) except -1:
    global _buffer
    cdef void *bptr = NULL
    cdef MPI_Aint blen = 0
    _buffer = asbuffer_w(ob, &bptr, &blen)
    p[0] = bptr
    n[0] = blen
    return 0

cdef inline object detach_buffer(void *p, MPI_Count n):
    global _buffer
    cdef object ob = None
    try:
        if (_buffer is not None and
            _buffer.view.buf == p and
            _buffer.view.obj != NULL):
            ob = <object>_buffer.view.obj
        else:
            ob = mpibuf(p, n)
    finally:
        _buffer = None
    return ob

# -----------------------------------------------------------------------------

cdef object __UNWEIGHTED__    = <MPI_Aint>MPI_UNWEIGHTED

cdef object __WEIGHTS_EMPTY__ = <MPI_Aint>MPI_WEIGHTS_EMPTY


cdef inline bint is_UNWEIGHTED(object weights):
    return is_constant(weights, __UNWEIGHTED__)

cdef inline bint is_WEIGHTS_EMPTY(object weights):
    return is_constant(weights, __WEIGHTS_EMPTY__)


cdef object asarray_weights(object weights, int nweight, int **iweight):
    if weights is None:
        iweight[0] = MPI_UNWEIGHTED
        return None
    if is_UNWEIGHTED(weights):
        iweight[0] = MPI_UNWEIGHTED
        return None
    if is_WEIGHTS_EMPTY(weights):
        if nweight > 0:
            raise ValueError("empty weights but nonzero degree")
        iweight[0] = MPI_WEIGHTS_EMPTY
        return None
    return chkarray(weights, nweight, iweight)

# -----------------------------------------------------------------------------

cdef inline int comm_neighbors_count(
    MPI_Comm comm,
    int *incoming,
    int *outgoing,
) except -1:
    cdef int topo = MPI_UNDEFINED
    cdef int size=0, ndims=0, rank=0, nneighbors=0
    cdef int indegree=0, outdegree=0, weighted=0
    CHKERR( MPI_Topo_test(comm, &topo) )
    if topo == MPI_UNDEFINED:                 #~> unreachable
        CHKERR( MPI_Comm_size(comm, &size) )  #~> unreachable
        indegree = outdegree = size           #~> unreachable
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

cdef int    commlock_keyval   = MPI_KEYVAL_INVALID
cdef object commlock_lock     = Lock()
cdef dict   commlock_registry = {}


cdef inline int commlock_free_cb(
    MPI_Comm comm,
) except MPI_ERR_UNKNOWN with gil:
    cdef object key = <Py_uintptr_t>comm
    with commlock_lock:
        if key in commlock_registry:
            del commlock_registry[key]
    return MPI_SUCCESS


@cython.linetrace(False)
@cython.callspec("MPIAPI")
cdef int commlock_free_fn(
    MPI_Comm comm,
    int keyval,
    void *attrval,
    void *xstate,
) noexcept nogil:
    <void> keyval  # unused
    <void> attrval # unused
    <void> xstate  # unused
    if comm == MPI_COMM_SELF:  <void>MPI_Comm_free_keyval(&commlock_keyval)
    if not Py_IsInitialized(): return MPI_SUCCESS
    if not py_module_alive():  return MPI_SUCCESS
    return commlock_free_cb(comm)


cdef inline dict commlock_table(MPI_Comm comm):
    cdef int found = 0
    cdef void *attrval = NULL
    cdef dict table
    if commlock_keyval == MPI_KEYVAL_INVALID:
        CHKERR( MPI_Comm_create_keyval(
            MPI_COMM_NULL_COPY_FN,
            commlock_free_fn,
            &commlock_keyval, NULL) )
        table = {}
        CHKERR( MPI_Comm_set_attr(
            MPI_COMM_SELF, commlock_keyval, <void*> table) )
        commlock_registry[<Py_uintptr_t>MPI_COMM_SELF] = table
    CHKERR( MPI_Comm_get_attr(
        comm, commlock_keyval, &attrval, &found) )
    if not found:
        table = {}
        CHKERR( MPI_Comm_set_attr(
            comm, commlock_keyval, <void*> table) )
        commlock_registry[<Py_uintptr_t>comm] = table
    elif PYPY:
        table = commlock_registry[<Py_uintptr_t>comm]  #~> pypy
    else:
        table = <dict> attrval
    return table


cdef inline object PyMPI_Lock(MPI_Comm comm, object key):
    cdef dict table
    cdef object lock
    with commlock_lock:
        table = commlock_table(comm)
        try:
            lock = table[key]
        except KeyError:
            lock = Lock()
            table[key] = lock
        return lock


cdef inline object PyMPI_Lock_table(MPI_Comm comm):
    with commlock_lock:
        return commlock_table(comm)


def _comm_lock(Comm comm: Comm, object key: Hashable = None) -> Lock:
    "Create/get communicator lock"
    return PyMPI_Lock(comm.ob_mpi, key)

def _comm_lock_table(Comm comm: Comm) -> dict[Hashable, Lock]:
    "Internal communicator lock table"
    return PyMPI_Lock_table(comm.ob_mpi)

# -----------------------------------------------------------------------------
