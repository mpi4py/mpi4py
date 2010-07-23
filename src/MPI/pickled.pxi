# -----------------------------------------------------------------------------

cdef extern from *:
    char*      PyMPIBytes_AsString(object) except NULL
    Py_ssize_t PyMPIBytes_Size(object) except -1
    object     PyMPIBytes_FromStringAndSize(char*,Py_ssize_t)

# -----------------------------------------------------------------------------

cdef object PyPickle_dumps = None
cdef object PyPickle_loads = None
cdef object PyPickle_PROTOCOL = -1

try:
    from cPickle import dumps as PyPickle_dumps
    from cPickle import loads as PyPickle_loads
    from cPickle import HIGHEST_PROTOCOL as PyPickle_PROTOCOL
except ImportError:
    from pickle import dumps as PyPickle_dumps
    from pickle import loads as PyPickle_loads
    from pickle import HIGHEST_PROTOCOL as PyPickle_PROTOCOL

cdef class _p_Pickle:

    cdef object ob_dumps
    cdef object ob_loads
    cdef object ob_PROTOCOL

    def __cinit__(self):
        self.ob_dumps = PyPickle_dumps
        self.ob_loads = PyPickle_loads
        self.ob_PROTOCOL = PyPickle_PROTOCOL

    property dumps:
        def __get__(self):
            return self.ob_dumps
        def __set__(self, dumps):
            self.ob_dumps = dumps

    property loads:
        def __get__(self):
            return self.ob_loads
        def __set__(self, loads):
            self.ob_loads = loads

    property PROTOCOL:
        def __get__(self):
            return self.ob_PROTOCOL
        def __set__(self, PROTOCOL):
            self.ob_PROTOCOL = PROTOCOL

    cdef object dump(self, object obj, void **p, int *n):
        if obj is None:
            p[0] = NULL
            n[0] = 0
            return None
        cdef object buf = self.ob_dumps(obj, self.ob_PROTOCOL)
        p[0] = <void*> PyMPIBytes_AsString(buf)
        n[0] = <int>   PyMPIBytes_Size(buf) # XXX overflow?
        return buf

    cdef object alloc(self, void **p, int n):
        if n == 0:
            p[0] = NULL
            return None
        cdef object buf = PyMPIBytes_FromStringAndSize(NULL, n)
        p[0] = PyMPIBytes_AsString(buf)
        return buf

    cdef object load(self, object buf):
        if buf is None:
            return None
        cdef object obj = self.ob_loads(buf)
        return obj

    cdef object dumpv(self, object obj, void **p,
                      int n, int cnt[], int dsp[]):
        cdef Py_ssize_t i=0, m=n
        if obj is None:
            p[0] = NULL
            for i from 0 <= i < m:
                cnt[i] = 0
                dsp[i] = 0
            return None
        cdef object items = list(obj)
        m = len(items)
        if m != n: raise ValueError(
            "expecting %d items, got %d" % (n, m))
        cdef int d=0, c=0
        for i from 0 <= i < m:
            items[i] = self.dump(items[i], p, &c)
            if c == 0: items[i] = b''
            cnt[i] = c
            dsp[i] = d
            d += c
        cdef object buf = b''.join(items) # XXX use _PyBytes_Join() ?
        p[0] = PyMPIBytes_AsString(buf)
        return buf

    cdef object allocv(self, void **p,
                       int n, int cnt[], int dsp[]):
        cdef int i=0, d=0
        for i from 0 <= i < n:
            dsp[i] = d
            d += cnt[i]
        return self.alloc(p, d)

    cdef object loadv(self, object obj,
                      int n, int cnt[], int dsp[]):
        cdef Py_ssize_t i=0, m=n
        cdef object items = [None] * m
        if obj is None: return items
        cdef Py_ssize_t d=0, c=0
        for i from 0 <= i < m:
            c = cnt[i]
            d = dsp[i]
            if c == 0: continue
            items[i] = self.load(obj[d:d+c])
        return items


cdef _p_Pickle PyMPI_PICKLE = _p_Pickle()

cdef inline _p_Pickle PyMPI_pickle():
    return PyMPI_PICKLE

_p_pickle = PyMPI_PICKLE

# -----------------------------------------------------------------------------

cdef object PyMPI_send(object obj, int dest, int tag,
                       MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef int dosend = (dest != MPI_PROC_NULL)
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dump(obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Send(sbuf, scount, stype,
                                 dest, tag, comm) )
    return None


cdef object PyMPI_bsend(object obj, int dest, int tag,
                        MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef int dosend = (dest != MPI_PROC_NULL)
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dump(obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Bsend(sbuf, scount, stype,
                                  dest, tag, comm) )
    return None


cdef object PyMPI_ssend(object obj, int dest, int tag,
                        MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef int dosend = (dest != MPI_PROC_NULL)
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dump(obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Ssend(sbuf, scount, stype,
                                  dest, tag, comm) )
    return None


cdef object PyMPI_recv(object obj, int source, int tag,
                       MPI_Comm comm, MPI_Status *status):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *rbuf = NULL
    cdef int rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int dorecv = (source != MPI_PROC_NULL)
    #
    cdef MPI_Status rsts
    with nogil: CHKERR( MPI_Probe(source, tag, comm, &rsts) )
    with nogil: CHKERR( MPI_Get_count(&rsts, rtype, &rcount) )
    source = rsts.MPI_SOURCE
    tag = rsts.MPI_TAG
    #
    cdef object rmsg = None
    if dorecv: rmsg = pickle.alloc(&rbuf, rcount)
    with nogil: CHKERR( MPI_Recv(rbuf, rcount, rtype,
                                 source, tag, comm, status) )
    if dorecv: rmsg = pickle.load(rmsg)
    return rmsg


cdef object PyMPI_sendrecv(object sobj, int dest,   int sendtag,
                           object robj, int source, int recvtag,
                           MPI_Comm comm, MPI_Status *status):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef int rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int dosend = (dest   != MPI_PROC_NULL)
    cdef int dorecv = (source != MPI_PROC_NULL)
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dump(sobj, &sbuf, &scount)
    cdef MPI_Request sreq = MPI_REQUEST_NULL
    with nogil: CHKERR( MPI_Isend(sbuf, scount, stype,
                                  dest, sendtag, comm, &sreq) )
    #
    cdef MPI_Status rsts
    with nogil: CHKERR( MPI_Probe(source, recvtag, comm, &rsts) )
    with nogil: CHKERR( MPI_Get_count(&rsts, rtype, &rcount) )
    source  = rsts.MPI_SOURCE
    recvtag = rsts.MPI_TAG
    #
    cdef object rmsg = None
    if dorecv: rmsg = pickle.alloc(&rbuf, rcount)
    with nogil: CHKERR( MPI_Recv(rbuf, rcount, rtype,
                                 source, recvtag, comm, status) )
    #
    with nogil: CHKERR( MPI_Wait(&sreq, MPI_STATUS_IGNORE) )
    if dorecv: rmsg = pickle.load(rmsg)
    return rmsg

# -----------------------------------------------------------------------------

cdef object PyMPI_isend(object obj, int dest, int tag,
                        MPI_Comm comm, MPI_Request *request):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object smsg = None
    cdef int dosend = (dest != MPI_PROC_NULL)
    if dosend: smsg = pickle.dump(obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Isend(sbuf, scount, stype,
                                  dest, tag, comm, request) )
    return smsg


cdef object PyMPI_ibsend(object obj, int dest, int tag,
                         MPI_Comm comm, MPI_Request *request):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object smsg = None
    cdef int dosend = (dest != MPI_PROC_NULL)
    if dosend: smsg = pickle.dump(obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Ibsend(sbuf, scount, stype,
                                   dest, tag, comm, request) )
    return smsg


cdef object PyMPI_issend(object obj, int dest, int tag,
                         MPI_Comm comm, MPI_Request *request):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object smsg = None
    cdef int dosend = (dest != MPI_PROC_NULL)
    if dosend: smsg = pickle.dump(obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Issend(sbuf, scount, stype,
                                   dest, tag, comm, request) )
    return smsg

# -----------------------------------------------------------------------------

cdef object PyMPI_barrier(MPI_Comm comm):
    with nogil: CHKERR( MPI_Barrier(comm) )
    return None


cdef object PyMPI_bcast(object obj,
                        int root, MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *buf = NULL
    cdef int count = 0
    cdef MPI_Datatype dtype = MPI_BYTE
    #
    cdef int dosend=0, dorecv=0
    cdef int inter=0, rank=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        if root == <int>MPI_PROC_NULL:
            dosend=0; dorecv=0;
        elif root == <int>MPI_ROOT:
            dosend=1; dorecv=0;
        else:
            dosend=0; dorecv=1;
    else:
        CHKERR( MPI_Comm_rank(comm, &rank) )
        if root == rank:
            dosend=1; dorecv=1;
        else:
            dosend=0; dorecv=1;
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dump(obj, &buf, &count)
    with nogil: CHKERR( MPI_Bcast(&count, 1, MPI_INT,
                                  root, comm) )
    cdef object rmsg = None
    if dorecv and dosend: rmsg = smsg
    elif dorecv: rmsg = pickle.alloc(&buf, count)
    with nogil: CHKERR( MPI_Bcast(buf, count, dtype,
                                  root, comm) )
    if dorecv: rmsg = pickle.load(rmsg)
    return rmsg


cdef object PyMPI_gather(object sendobj, object recvobj,
                         int root, MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef int *rcounts = NULL
    cdef int *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int dosend=0, dorecv=0
    cdef int inter=0, size=0, rank=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
        if root == <int>MPI_PROC_NULL:
            dosend=0; dorecv=0;
        elif root == <int>MPI_ROOT:
            dosend=0; dorecv=1;
        else:
            dosend=1; dorecv=0;
    else:
        CHKERR( MPI_Comm_size(comm, &size) )
        CHKERR( MPI_Comm_rank(comm, &rank) )
        if root == rank:
            dosend=1; dorecv=1;
        else:
            dosend=1; dorecv=0;
    #
    cdef object tmp1=None, tmp2=None
    if dorecv: tmp1 = allocate_int(size, &rcounts)
    if dorecv: tmp2 = allocate_int(size, &rdispls)
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dump(sendobj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Gather(&scount, 1, MPI_INT,
                                   rcounts, 1, MPI_INT,
                                   root, comm) )
    cdef object rmsg = None
    if dorecv: rmsg = pickle.allocv(&rbuf, size, rcounts, rdispls)
    with nogil: CHKERR( MPI_Gatherv(sbuf, scount,           stype,
                                    rbuf, rcounts, rdispls, rtype,
                                    root, comm) )
    if dorecv: rmsg = pickle.loadv(rmsg, size, rcounts, rdispls)
    return rmsg


cdef object PyMPI_scatter(object sendobj, object recvobj,
                          int root, MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int *scounts = NULL
    cdef int *sdispls = NULL
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef int rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int dosend=0, dorecv=0
    cdef int inter=0, size=0, rank=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
        if root == <int>MPI_PROC_NULL:
            dosend=1; dorecv=0;
        elif root == <int>MPI_ROOT:
            dosend=1; dorecv=0;
        else:
            dosend=0; dorecv=1;
    else:
        CHKERR( MPI_Comm_size(comm, &size) )
        CHKERR( MPI_Comm_rank(comm, &rank) )
        if root == rank:
            dosend=1; dorecv=1;
        else:
            dosend=0; dorecv=1;
    #
    cdef object tmp1=None, tmp2=None
    if dosend: tmp1 = allocate_int(size, &scounts)
    if dosend: tmp2 = allocate_int(size, &sdispls)
    #
    cdef object smsg = None
    if dosend: smsg = pickle.dumpv(sendobj, &sbuf, size, scounts, sdispls)
    with nogil: CHKERR( MPI_Scatter(scounts, 1, MPI_INT,
                                    &rcount, 1, MPI_INT,
                                    root, comm) )
    cdef object rmsg = None
    if dorecv: rmsg = pickle.alloc(&rbuf, rcount)
    with nogil: CHKERR( MPI_Scatterv(sbuf, scounts, sdispls, stype,
                                     rbuf, rcount,           rtype,
                                     root, comm) )
    if dorecv: rmsg = pickle.load(rmsg)
    return rmsg


cdef object PyMPI_allgather(object sendobj, object recvobj,
                            MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef int *rcounts = NULL
    cdef int *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int inter=0, size=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
    else:
        CHKERR( MPI_Comm_size(comm, &size) )
    #
    cdef object tmp1 = allocate_int(size, &rcounts)
    cdef object tmp2 = allocate_int(size, &rdispls)
    #
    cdef object smsg = pickle.dump(sendobj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Allgather(&scount, 1, MPI_INT,
                                      rcounts, 1, MPI_INT,
                                      comm) )
    cdef object rmsg = pickle.allocv(&rbuf, size, rcounts, rdispls)
    with nogil: CHKERR( MPI_Allgatherv(sbuf, scount,           stype,
                                       rbuf, rcounts, rdispls, rtype,
                                       comm) )
    rmsg = pickle.loadv(rmsg, size, rcounts, rdispls)
    return rmsg


cdef object PyMPI_alltoall(object sendobj, object recvobj,
                           MPI_Comm comm):
    cdef _p_Pickle pickle = PyMPI_pickle()
    #
    cdef void *sbuf = NULL
    cdef int *scounts = NULL
    cdef int *sdispls = NULL
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef int *rcounts = NULL
    cdef int *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int inter=0, size=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
    else:
        CHKERR( MPI_Comm_size(comm, &size) )
    #
    cdef object stmp1 = allocate_int(size, &scounts)
    cdef object stmp2 = allocate_int(size, &sdispls)
    cdef object rtmp1 = allocate_int(size, &rcounts)
    cdef object rtmp2 = allocate_int(size, &rdispls)
    #
    cdef object smsg = pickle.dumpv(sendobj, &sbuf, size, scounts, sdispls)
    with nogil: CHKERR( MPI_Alltoall(scounts, 1, MPI_INT,
                                     rcounts, 1, MPI_INT,
                                     comm) )
    cdef object rmsg = pickle.allocv(&rbuf, size, rcounts, rdispls)
    with nogil: CHKERR( MPI_Alltoallv(sbuf, scounts, sdispls, stype,
                                      rbuf, rcounts, rdispls, rtype,
                                      comm) )
    rmsg = pickle.loadv(rmsg, size, rcounts, rdispls)
    return rmsg

# -----------------------------------------------------------------------------

cdef inline object _py_reduce(object seq, object op):
    if seq is None: return None
    cdef Py_ssize_t i=0, n=len(seq)
    if op is __MAXLOC__ or op is __MINLOC__:
        seq = list(zip(seq, range(n)))
    cdef object res = seq[0]
    for i from 1 <= i < n:
        res = op(res, seq[i])
    return res

cdef inline object _py_scan(object seq, object op):
    if seq is None: return None
    cdef Py_ssize_t i=0, n=len(seq)
    if op is __MAXLOC__ or op is __MINLOC__:
        seq = list(zip(seq, range(n)))
    for i from 1 <= i < n:
        seq[i] = op(seq[i-1], seq[i])
    return seq

cdef inline object _py_exscan(object seq, object op):
    if seq is None: return None
    seq = _py_scan(seq, op)
    seq.pop(-1)
    seq.insert(0, None)
    return seq


cdef object PyMPI_reduce(object sendobj, object recvobj,
                         object op, int root, MPI_Comm comm):
    cdef object items = PyMPI_gather(sendobj, recvobj, root, comm)
    return _py_reduce(items, op)


cdef object PyMPI_allreduce(object sendobj, object recvobj,
                            object op, MPI_Comm comm):
    cdef object items = PyMPI_allgather(sendobj, recvobj, comm)
    return _py_reduce(items, op)


cdef object PyMPI_scan(object sendobj, object recvobj,
                       object op, MPI_Comm comm):
    cdef object items = PyMPI_gather(sendobj, None, 0, comm)
    items = _py_scan(items, op)
    return PyMPI_scatter(items, None, 0, comm)


cdef object PyMPI_exscan(object sendobj, object recvobj,
                         object op, MPI_Comm comm):
    cdef object items = PyMPI_gather(sendobj, None, 0, comm)
    items = _py_exscan(items, op)
    return PyMPI_scatter(items, None, 0, comm)

# -----------------------------------------------------------------------------
