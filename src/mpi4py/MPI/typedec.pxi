# -----------------------------------------------------------------------------

cdef inline str combinername(int combiner):
    if combiner == MPI_COMBINER_NAMED          : return 'NAMED'
    if combiner == MPI_COMBINER_DUP            : return 'DUP'
    if combiner == MPI_COMBINER_CONTIGUOUS     : return 'CONTIGUOUS'
    if combiner == MPI_COMBINER_VECTOR         : return 'VECTOR'
    if combiner == MPI_COMBINER_HVECTOR        : return 'HVECTOR'
    if combiner == MPI_COMBINER_INDEXED        : return 'INDEXED'
    if combiner == MPI_COMBINER_HINDEXED       : return 'HINDEXED'
    if combiner == MPI_COMBINER_INDEXED_BLOCK  : return 'INDEXED_BLOCK'
    if combiner == MPI_COMBINER_HINDEXED_BLOCK : return 'HINDEXED_BLOCK'
    if combiner == MPI_COMBINER_STRUCT         : return 'STRUCT'
    if combiner == MPI_COMBINER_SUBARRAY       : return 'SUBARRAY'
    if combiner == MPI_COMBINER_DARRAY         : return 'DARRAY'
    if combiner == MPI_COMBINER_RESIZED        : return 'RESIZED'
    if combiner == MPI_COMBINER_F90_INTEGER    : return 'F90_INTEGER'
    if combiner == MPI_COMBINER_F90_REAL       : return 'F90_REAL'
    if combiner == MPI_COMBINER_F90_COMPLEX    : return 'F90_COMPLEX'
    raise ValueError(f"unknown combiner value {combiner}")  #~> unreachable

cdef inline list makelist(integral_t *p, MPI_Count start, MPI_Count last):
    return [p[i] for i from start <= i <= last]

cdef inline tuple datatype_decode(
    Datatype self,
    bint mark,
):
    # get the datatype envelope
    cdef int combiner = MPI_UNDEFINED
    cdef MPI_Count ni = 0, na = 0, nc = 0, nd = 0
    CHKERR( MPI_Type_get_envelope_c(
        self.ob_mpi, &ni, &na, &nc, &nd, &combiner) )
    # return self immediately for named datatypes
    if combiner == MPI_COMBINER_NAMED:
        return (self, combinername(combiner), {})
    # get the datatype contents
    cdef int *i = NULL
    cdef MPI_Aint *a = NULL
    cdef MPI_Count *c = NULL
    cdef MPI_Datatype *d = NULL
    cdef tmp1 = allocate(ni, sizeof(int), &i)
    cdef tmp2 = allocate(na, sizeof(MPI_Aint), &a)
    cdef tmp3 = allocate(nc, sizeof(MPI_Count), &c)
    cdef tmp4 = allocate(nd, sizeof(MPI_Datatype), &d)
    CHKERR( MPI_Type_get_contents_c(
        self.ob_mpi, ni, na, nc, nd, i, a, c, d) )
    # process datatypes in advance
    cdef Datatype oldtype = __DATATYPE_NULL__
    cdef dict params = {}
    cdef list datatypes = []
    if combiner == MPI_COMBINER_STRUCT:
        datatypes = [ref_Datatype(d[k]) for k in range(nd)]
    elif nd == 1:
        oldtype = ref_Datatype(d[0])
        datatypes = [oldtype]
    # dispatch depending on the combiner value
    cdef int use_count = 1 if (nc > 0) else 0
    cdef MPI_Count s1, e1, s2, e2, s3, e3, s4, e4
    cdef object count, blklen, stride, displs
    cdef object sizes, subsizes, starts, order
    cdef object lbound, extent
    if combiner == MPI_COMBINER_DUP:
        params = {}
    elif combiner == MPI_COMBINER_CONTIGUOUS:
        count = c[0] if use_count else i[0]
        params = {
            ('count') : count,
        }
    elif combiner == MPI_COMBINER_VECTOR:
        count  = c[0] if use_count else i[0]
        blklen = c[1] if use_count else i[1]
        stride = c[2] if use_count else i[2]
        params = {
            ('count')       : count,
            ('blocklength') : blklen,
            ('stride')      : stride,
        }
    elif combiner == MPI_COMBINER_HVECTOR:
        count  = c[0] if use_count else i[0]
        blklen = c[1] if use_count else i[1]
        stride = c[2] if use_count else a[0]
        params = {
            ('count')       : count ,
            ('blocklength') : blklen,
            ('stride')      : stride,
        }
    elif combiner == MPI_COMBINER_INDEXED:
        if use_count:
            s1 =      1; e1 =   c[0]
            s2 = c[0]+1; e2 = 2*c[0]
            blklen = makelist(c, s1, e1)
            displs = makelist(c, s2, e2)
        else:
            s1 =      1; e1 =   i[0]      #~> uncovered
            s2 = i[0]+1; e2 = 2*i[0]      #~> uncovered
            blklen = makelist(i, s1, e1)  #~> uncovered
            displs = makelist(i, s2, e2)  #~> uncovered
        params = {
            ('blocklengths')  : blklen,
            ('displacements') : displs,
        }
    elif combiner == MPI_COMBINER_HINDEXED:
        if use_count:
            s1 =      1; e1 =   c[0]
            s2 = c[0]+1; e2 = 2*c[0]
            blklen = makelist(c, s1, e1)
            displs = makelist(c, s2, e2)
        else:
            s1 = 1; e1 = i[0]             #~> uncovered
            s2 = 0; e2 = i[0]-1           #~> uncovered
            blklen = makelist(i, s1, e1)  #~> uncovered
            displs = makelist(a, s2, e2)  #~> uncovered
        params = {
            ('blocklengths')  : blklen,
            ('displacements') : displs,
        }
    elif combiner == MPI_COMBINER_INDEXED_BLOCK:
        if use_count:
            s2 = 2; e2 = c[0]+1
            blklen = c[1]
            displs = makelist(c, s2, e2)
        else:
            s2 = 2; e2 = i[0]+1          #~> uncovered
            blklen = i[1]                #~> uncovered
            displs = makelist(i, s2, e2) #~> uncovered
        params = {
            ('blocklength')   : blklen,
            ('displacements') : displs,
        }
    elif combiner == MPI_COMBINER_HINDEXED_BLOCK:
        if use_count:
            s2 = 2; e2 = c[0]+1
            blklen = c[1]
            displs = makelist(c, s2, e2)
        else:
            s2 = 0; e2 = i[0]-1          #~> uncovered
            blklen = i[1]                #~> uncovered
            displs = makelist(a, s2, e2) #~> uncovered
        params = {
            ('blocklength')   : blklen,
            ('displacements') : displs,
        }
    elif combiner == MPI_COMBINER_STRUCT:
        if use_count:
            s1 =      1; e1 =   c[0]
            s2 = c[0]+1; e2 = 2*c[0]
            blklen = makelist(c, s1, e1)
            displs = makelist(c, s2, e2)
        else:
            s1 = 1; e1 = i[0]             #~> uncovered
            s2 = 0; e2 = i[0]-1           #~> uncovered
            blklen = makelist(i, s1, e1)  #~> uncovered
            displs = makelist(a, s2, e2)  #~> uncovered
        params = {
            ('blocklengths')  : blklen,
            ('displacements') : displs,
            ('datatypes')     : datatypes,
        }
    elif combiner == MPI_COMBINER_SUBARRAY:
        if use_count:
            s1 = 0*i[0]; e1 = 1*i[0]-1
            s2 = 1*i[0]; e2 = 2*i[0]-1
            s3 = 2*i[0]; e3 = 3*i[0]-1
            sizes    = makelist(c, s1, e1)
            subsizes = makelist(c, s2, e2)
            starts   = makelist(c, s3, e3)
            order    = i[1]
        else:
            s1 = 0*i[0]+1; e1 = 1*i[0]      #~> uncovered
            s2 = 1*i[0]+1; e2 = 2*i[0]      #~> uncovered
            s3 = 2*i[0]+1; e3 = 3*i[0]      #~> uncovered
            sizes    = makelist(i, s1, e1)  #~> uncovered
            subsizes = makelist(i, s2, e2)  #~> uncovered
            starts   = makelist(i, s3, e3)  #~> uncovered
            order    = i[3*i[0]+1]          #~> uncovered
        params = {
            ('sizes')    : sizes,
            ('subsizes') : subsizes,
            ('starts')   : starts,
            ('order')    : order,
        }
    elif combiner == MPI_COMBINER_DARRAY:
        if use_count:
            s1 = 0*i[2]+0; e1 = 1*i[2]+0-1
            s2 = 0*i[2]+3; e2 = 1*i[2]+3-1
            s3 = 1*i[2]+3; e3 = 2*i[2]+3-1
            s4 = 2*i[2]+3; e4 = 3*i[2]+3-1
            sizes = makelist(c, s1, e1)
            order = i[3*i[2]+3]
        else:
            s1 = 0*i[2]+3; e1 = 1*i[2]+3-1  #~> uncovered
            s2 = 1*i[2]+3; e2 = 2*i[2]+3-1  #~> uncovered
            s3 = 2*i[2]+3; e3 = 3*i[2]+3-1  #~> uncovered
            s4 = 3*i[2]+3; e4 = 4*i[2]+3-1  #~> uncovered
            sizes = makelist(i, s1, e1)     #~> uncovered
            order = i[4*i[2]+3]             #~> uncovered
        params = {
            ('size')     : i[0],
            ('rank')     : i[1],
            ('gsizes')   : sizes,
            ('distribs') : makelist(i, s2, e2),
            ('dargs')    : makelist(i, s3, e3),
            ('psizes')   : makelist(i, s4, e4),
            ('order')    : order,
        }
    elif combiner == MPI_COMBINER_RESIZED:
        lbound = c[0] if use_count else a[0]
        extent = c[1] if use_count else a[1]
        params = {
            ('lb')     : lbound,
            ('extent') : extent,
        }
    elif combiner == MPI_COMBINER_F90_INTEGER:
        params = {
            ('r') : i[0],
        }
    elif combiner == MPI_COMBINER_F90_REAL:
        params = {
            ('p') : i[0],
            ('r') : i[1],
        }
    elif combiner == MPI_COMBINER_F90_COMPLEX:
        params = {
            ('p') : i[0],
            ('r') : i[1],
        }
    if mark:
        datatype_visit(marktemp, datatypes)
    return (oldtype, combinername(combiner), params)


cdef inline Datatype datatype_create(
    Datatype datatype,
    str  combiner,
    dict params,
    bint free,
):
    cdef object factory
    cdef Datatype newtype
    cdef list datatypes = params.get('datatypes') or [datatype]
    try:
        combiner = combiner.lower()
        factory = getattr(datatype, f'Create_{combiner}')
        newtype = factory(**params).Commit()
    finally:
        if free:
            datatype_visit(freetemp, datatypes)
    return newtype


cdef inline int datatype_visit(
    int (*visit)(Datatype) except -1,
    list datatypes,
) except -1:
    cdef Datatype datatype
    for datatype in datatypes:
        visit(datatype)

# -----------------------------------------------------------------------------

def _datatype_create(
    Datatype datatype: Datatype,
    str combiner: str,
    dict params: dict[str, Any],
    bint free: bool = False,
) -> Datatype:
    """
    Create datatype from base datatype, combiner name, and parameters
    """
    return datatype_create(datatype, combiner, params, free)


def _datatype_decode(
    Datatype datatype: Datatype,
    bint mark: bool = False,
) -> tuple[Datatype, str, dict[str, Any]]:
    """
    Decode datatype to base datatype, combiner name, and parameters
    """
    return datatype_decode(datatype, mark)  #~> TODO

# -----------------------------------------------------------------------------
