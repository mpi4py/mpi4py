# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    bint       PyBytes_CheckExact(object)
    char*      PyBytes_AsString(object) except NULL
    Py_ssize_t PyBytes_Size(object) except -1
    object     PyBytes_FromStringAndSize(char*,Py_ssize_t)

# -----------------------------------------------------------------------------

cdef object PyPickle_dumps = None
cdef object PyPickle_loads = None
cdef object PyPickle_PROTOCOL = None
cdef object PyPickle_THRESHOLD = 1024**2 // 4 # 0.25 MiB

from pickle import dumps as PyPickle_dumps
from pickle import loads as PyPickle_loads
from pickle import HIGHEST_PROTOCOL as PyPickle_PROTOCOL

if Py_GETENV(b"MPI4PY_PICKLE_PROTOCOL") != NULL:
    PyPickle_PROTOCOL = int(Py_GETENV(b"MPI4PY_PICKLE_PROTOCOL"))

if Py_GETENV(b"MPI4PY_PICKLE_THRESHOLD") != NULL:
    PyPickle_THRESHOLD = int(Py_GETENV(b"MPI4PY_PICKLE_THRESHOLD"))

cdef class Pickle:
    """
    Pickle/unpickle Python objects.
    """

    cdef object ob_dumps
    cdef object ob_loads
    cdef object ob_PROTO
    cdef object ob_THRES

    def __cinit__(self, *args, **kwargs):
        <void> args   # unused
        <void> kwargs # unused
        self.ob_dumps = PyPickle_dumps
        self.ob_loads = PyPickle_loads
        self.ob_PROTO = PyPickle_PROTOCOL
        self.ob_THRES = PyPickle_THRESHOLD

    def __init__(
        self,
        dumps: Callable[[Any, int], bytes] | None = None,
        loads: Callable[[Buffer], Any] | None = None,
        protocol: int | None = None,
        threshold: int | None = None,
    ) -> None:
        if dumps is None:
            dumps = PyPickle_dumps
        if loads is None:
            loads = PyPickle_loads
        if protocol is None:
            if dumps is PyPickle_dumps:
                protocol = PyPickle_PROTOCOL
        if threshold is None:
            threshold = PyPickle_THRESHOLD
        self.ob_dumps = dumps
        self.ob_loads = loads
        self.ob_PROTO = protocol
        self.ob_THRES = threshold

    def dumps(
        self,
        obj: Any,
    ) -> bytes:
        """
        Serialize object to pickle data stream.
        """
        return cdumps(self, obj)

    def loads(
        self,
        data: Buffer,
    ) -> Any:
        """
        Deserialize object from pickle data stream.
        """
        return cloads(self, data)

    def dumps_oob(
        self,
        obj: Any,
    ) -> tuple[bytes, list[buffer]]:
        """
        Serialize object to pickle data stream and out-of-band buffers.
        """
        return cdumps_oob(self, obj)

    def loads_oob(
        self,
        data: Buffer,
        buffers: Iterable[Buffer],
    ) -> Any:
        """
        Deserialize object from pickle data stream and out-of-band buffers.
        """
        return cloads_oob(self, data, buffers)

    property PROTOCOL:
        """Protocol version."""
        def __get__(self) -> int | None:
            return self.ob_PROTO
        def __set__(self, protocol: int | None):
            if protocol is None:
                if self.ob_dumps is PyPickle_dumps:
                    protocol = PyPickle_PROTOCOL
            self.ob_PROTO = protocol

    property THRESHOLD:
        """Out-of-band threshold."""
        def __get__(self) -> int:
            return self.ob_THRES
        def __set__(self, threshold: int | None):
            if threshold is None:
                threshold = PyPickle_THRESHOLD
            self.ob_THRES = threshold


cdef Pickle PyMPI_PICKLE = Pickle()
pickle = PyMPI_PICKLE

# -----------------------------------------------------------------------------

cdef int have_pickle5 = -1                                #~> legacy
cdef object PyPickle5_dumps = None                        #~> legacy
cdef object PyPickle5_loads = None                        #~> legacy

cdef int import_pickle5() except -1:                      #~> legacy
    global have_pickle5                                   #~> legacy
    global PyPickle5_dumps                                #~> legacy
    global PyPickle5_loads                                #~> legacy
    if have_pickle5 < 0:                                  #~> legacy
        try:                                              #~> legacy
            from pickle5 import dumps as PyPickle5_dumps  #~> legacy
            from pickle5 import loads as PyPickle5_loads  #~> legacy
            have_pickle5 = 1                              #~> legacy
        except ImportError:                               #~> legacy
            PyPickle5_dumps = None                        #~> legacy
            PyPickle5_loads = None                        #~> legacy
            have_pickle5 = 0                              #~> legacy
    return have_pickle5                                   #~> legacy


cdef object get_buffer_callback(list buffers, Py_ssize_t threshold):
    def buffer_callback(ob):
        cdef buffer buf = getbuffer(ob, 1, 0)
        if buf.view.len >= threshold:
            buffers.append(buf)
            return False
        else:
            return True
    return buffer_callback

cdef object cdumps_oob(Pickle pkl, object obj):
    cdef object pkl_dumps = pkl.ob_dumps
    if PY_VERSION_HEX < 0x03080000:          #~> legacy
        if pkl_dumps is PyPickle_dumps:      #~> legacy
            if not import_pickle5():         #~> legacy
                return cdumps(pkl, obj), []  #~> legacy
            pkl_dumps = PyPickle5_dumps      #~> legacy
    cdef object protocol = pkl.ob_PROTO
    if protocol is None:
        protocol = PyPickle_PROTOCOL         #~> uncovered
    protocol = max(protocol, 5)
    cdef list buffers = []
    cdef Py_ssize_t threshold = pkl.ob_THRES
    cdef object buf_cb = get_buffer_callback(buffers, threshold)
    cdef object data = pkl_dumps(obj, protocol, buffer_callback=buf_cb)
    return data, buffers

cdef object cloads_oob(Pickle pkl, object data, object buffers):
    cdef object pkl_loads = pkl.ob_loads
    if PY_VERSION_HEX < 0x03080000:       #~> legacy
        if pkl_loads is PyPickle_loads:   #~> legacy
            if not import_pickle5():      #~> legacy
                return cloads(pkl, data)  #~> legacy
            pkl_loads = PyPickle5_loads   #~> legacy
    return pkl_loads(data, buffers=buffers)


# -----------------------------------------------------------------------------

cdef object cdumps(Pickle pkl, object obj):
    if pkl.ob_PROTO is not None:
        return pkl.ob_dumps(obj, pkl.ob_PROTO)
    else:
        return pkl.ob_dumps(obj)

cdef object cloads(Pickle pkl, object buf):
    return pkl.ob_loads(buf)


cdef object pickle_dump(Pickle pkl, object obj, void **p, MPI_Count *n):
    cdef object buf = cdumps(pkl, obj)
    p[0] = PyBytes_AsString(buf)
    n[0] = PyBytes_Size(buf)
    return buf

cdef object pickle_load(Pickle pkl, void *p, MPI_Count n):
    if p == NULL or n == 0: return None
    return cloads(pkl, mpibuf(p, n))


cdef object pickle_dumpv(Pickle pkl, object obj, void **p, int n, MPI_Count cnt[], MPI_Aint dsp[]):
    cdef Py_ssize_t m=n
    cdef object items
    if obj is None: items = [None] * m
    else:           items = list(obj)
    m = len(items)
    if m != n:
        raise ValueError(f"expecting {n} items, got {m}")
    cdef MPI_Count c=0
    cdef MPI_Aint  d=0
    for i in range(m):
        items[i] = pickle_dump(pkl, items[i], p, &c)
        cnt[i] = c; dsp[i] = d; d = d + <MPI_Aint>c
    cdef object buf = b''.join(items)
    p[0] = PyBytes_AsString(buf)
    return buf

cdef object pickle_loadv(Pickle pkl, void *p, int n, MPI_Count cnt[], MPI_Aint dsp[]):
    cdef Py_ssize_t m=n
    cdef object items = [None] * m
    if p == NULL: return items
    for i in range(m):
        items[i] = pickle_load(pkl, <char*>p + dsp[i], cnt[i])
    return items


cdef object pickle_alloc(void **p, MPI_Count n):
    cdef object buf = PyBytes_FromStringAndSize(NULL, <MPI_Aint>n)
    p[0] = PyBytes_AsString(buf)
    return buf

cdef object pickle_allocv(void **p, int n, MPI_Count cnt[], MPI_Aint dsp[]):
    cdef MPI_Count d=0
    for i in range(n):
        dsp[i] = <MPI_Aint> d
        d += cnt[i]
    return pickle_alloc(p, d)


cdef object allocate_count_displ(int n, MPI_Count **p, MPI_Aint **q):
    cdef object mem1 = allocate(n, sizeof(MPI_Count), p)
    cdef object mem2 = allocate(n, sizeof(MPI_Aint),  q)
    return (mem1, mem2)

# -----------------------------------------------------------------------------

cdef object PyMPI_send(object obj, int dest, int tag,
                       MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object tmps = None
    if dest != MPI_PROC_NULL:
        tmps = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Send_c(
        sbuf, scount, stype,
        dest, tag, comm) )
    return None


cdef object PyMPI_bsend(object obj, int dest, int tag,
                        MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object tmps = None
    if dest != MPI_PROC_NULL:
        tmps = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Bsend_c(
        sbuf, scount, stype,
        dest, tag, comm) )
    return None


cdef object PyMPI_ssend(object obj, int dest, int tag,
                        MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object tmps = None
    if dest != MPI_PROC_NULL:
        tmps = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Ssend_c(
        sbuf, scount, stype,
            dest, tag, comm) )
    return None

# -----------------------------------------------------------------------------

cdef object PyMPI_recv_obarg(object obj, int source, int tag,
                             MPI_Comm comm, MPI_Status *status):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    cdef MPI_Status rsts
    cdef object   rmsg = None
    cdef MPI_Aint rlen = 0
    #
    PyErr_WarnFormat(
        UserWarning, 1, b"%s",
        b"the 'buf' argument is deprecated",
    )
    #
    if source != MPI_PROC_NULL:
        if is_integral(obj):
            rcount = <MPI_Count> PyNumber_Index(obj)
            rmsg = pickle_alloc(&rbuf, rcount)
        else:
            rmsg = asbuffer_w(obj, &rbuf, &rlen)
            rcount = <MPI_Count> rlen
        if status == MPI_STATUS_IGNORE:
            status = &rsts
        <void> rmsg
    with nogil:
        CHKERR( MPI_Recv_c(
            rbuf, rcount, rtype,
            source, tag, comm, status) )
        if source != MPI_PROC_NULL:
            CHKERR( MPI_Get_count_c(status, rtype, &rcount) )
    #
    if rcount <= 0: return None
    return pickle_load(pickle, rbuf, rcount)


cdef object PyMPI_recv_match(object obj, int source, int tag,
                             MPI_Comm comm, MPI_Status *status):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef MPI_Message match = MPI_MESSAGE_NULL
    cdef MPI_Status rsts
    <void> obj # unused
    #
    with nogil:
        CHKERR( MPI_Mprobe(source, tag, comm, &match, &rsts) )
        CHKERR( MPI_Get_count_c(&rsts, rtype, &rcount) )
    cdef object tmpr = pickle_alloc(&rbuf, rcount)
    with nogil:
        CHKERR( MPI_Mrecv_c(
            rbuf, rcount, rtype, &match, status) )
    #
    if rcount <= 0: return None
    return pickle_load(pickle, rbuf, rcount)


cdef object PyMPI_recv_probe(object obj, int source, int tag,
                             MPI_Comm comm, MPI_Status *status):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef MPI_Status rsts
    cdef object tmpr
    <void> obj # unused
    #
    with PyMPI_Lock(comm, "recv"):
        with nogil:
            CHKERR( MPI_Probe(source, tag, comm, &rsts) )
            CHKERR( MPI_Get_count_c(&rsts, rtype, &rcount) )
            CHKERR( MPI_Status_get_source(&rsts, &source) )
            CHKERR( MPI_Status_get_tag(&rsts, &tag) )
        tmpr = pickle_alloc(&rbuf, rcount)
        with nogil:
            CHKERR( MPI_Recv_c(
                rbuf, rcount, rtype,
                source, tag, comm, status) )
    #
    if rcount <= 0: return None
    return pickle_load(pickle, rbuf, rcount)


cdef object PyMPI_recv(object obj, int source, int tag,
                       MPI_Comm comm, MPI_Status *status):
    if obj is not None:
        return PyMPI_recv_obarg(obj, source, tag, comm, status)
    elif options.recv_mprobe:
        return PyMPI_recv_match(obj, source, tag, comm, status)
    else:
        return PyMPI_recv_probe(obj, source, tag, comm, status)

# -----------------------------------------------------------------------------

cdef object PyMPI_isend(object obj, int dest, int tag,
                        MPI_Comm comm, MPI_Request *request):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object smsg = None
    if dest != MPI_PROC_NULL:
        smsg = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Isend_c(
        sbuf, scount, stype,
        dest, tag, comm, request) )
    return smsg


cdef object PyMPI_ibsend(object obj, int dest, int tag,
                         MPI_Comm comm, MPI_Request *request):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object smsg = None
    if dest != MPI_PROC_NULL:
        smsg = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Ibsend_c(
        sbuf, scount, stype,
        dest, tag, comm, request) )
    return smsg


cdef object PyMPI_issend(object obj, int dest, int tag,
                         MPI_Comm comm, MPI_Request *request):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    #
    cdef object smsg = None
    if dest != MPI_PROC_NULL:
        smsg = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Issend_c(
        sbuf, scount, stype,
        dest, tag, comm, request) )
    return smsg


cdef object PyMPI_irecv(object obj, int source, int tag,
                        MPI_Comm comm, MPI_Request *request):
    #
    cdef void *rbuf = NULL
    cdef MPI_Aint rlen = 0
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef object rmsg = None
    if source != MPI_PROC_NULL:
        if obj is None:
            rcount = options.irecv_bufsz
            obj = pickle_alloc(&rbuf, rcount)
            rmsg = asbuffer_r(obj, NULL, NULL)
        elif is_integral(obj):
            rcount = <MPI_Count> PyNumber_Index(obj)
            obj = pickle_alloc(&rbuf, rcount)
            rmsg = asbuffer_r(obj, NULL, NULL)
        else:
            rmsg = asbuffer_w(obj, &rbuf, &rlen)
            rcount = <MPI_Count> rlen
    with nogil: CHKERR( MPI_Irecv_c(
        rbuf, rcount, rtype,
        source, tag, comm, request) )
    return rmsg

# -----------------------------------------------------------------------------

cdef object PyMPI_sendrecv(object sobj, int dest,   int sendtag,
                           object robj, int source, int recvtag,
                           MPI_Comm comm, MPI_Status *status):
    cdef MPI_Request request = MPI_REQUEST_NULL
    sobj = PyMPI_isend(sobj, dest,   sendtag, comm, &request)
    robj = PyMPI_recv (robj, source, recvtag, comm, status)
    with nogil: CHKERR( MPI_Wait(&request, MPI_STATUS_IGNORE) )
    return robj

# -----------------------------------------------------------------------------

cdef object PyMPI_load(MPI_Status *status, object ob):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    if type(ob) is not buffer: return None
    CHKERR( MPI_Get_count_c(status, rtype, &rcount) )
    if rcount <= 0: return None
    cdef void *rbuf = (<buffer>ob).view.buf
    return pickle_load(pickle, rbuf, rcount)


cdef object PyMPI_wait(Request request, Status status):
    cdef object buf
    #
    cdef MPI_Status rsts
    with nogil: CHKERR( MPI_Wait(&request.ob_mpi, &rsts) )
    buf = request.ob_buf
    if status is not None:
        status.ob_mpi = rsts
    if request.ob_mpi == MPI_REQUEST_NULL:
        request.ob_buf = None
    #
    return PyMPI_load(&rsts, buf)


cdef object PyMPI_test(Request request, int *flag, Status status):
    cdef object buf = None
    #
    cdef MPI_Status rsts
    with nogil: CHKERR( MPI_Test(&request.ob_mpi, flag, &rsts) )
    if flag[0]:
        buf = request.ob_buf
    if status is not None:
        status.ob_mpi = rsts
    if request.ob_mpi == MPI_REQUEST_NULL:
        request.ob_buf = None
    #
    if not flag[0]: return None
    return PyMPI_load(&rsts, buf)


cdef object PyMPI_waitany(requests, int *index, Status status):
    cdef object buf = None
    cdef object obj = None
    cdef MPI_Status rsts
    cdef _p_rs rs = _p_rs.__new__(_p_rs)
    rs.acquire(requests)
    try:
        with nogil: CHKERR( MPI_Waitany(
            rs.count, rs.requests, index, &rsts) )
        if index[0] != MPI_UNDEFINED:
            buf = (<Request>requests[index[0]]).ob_buf
            obj = PyMPI_load(&rsts, buf)
        if status is not None:
            status.ob_mpi = rsts
    finally:
        rs.release()
    return obj


cdef object PyMPI_testany(requests, int *index, int *flag, Status status):
    cdef object buf = None
    cdef object obj = None
    cdef MPI_Status rsts
    cdef _p_rs rs = _p_rs.__new__(_p_rs)
    rs.acquire(requests)
    try:
        with nogil: CHKERR( MPI_Testany(
            rs.count, rs.requests, index, flag, &rsts) )
        if index[0] != MPI_UNDEFINED and flag[0]:
            buf = (<Request>requests[index[0]]).ob_buf
            obj = PyMPI_load(&rsts, buf)
        if status is not None:
            status.ob_mpi = rsts
    finally:
        rs.release()
    return obj


cdef object PyMPI_waitall(requests, statuses):
    cdef object objects = None
    cdef _p_rs rs = _p_rs.__new__(_p_rs)
    rs.acquire(requests)
    rs.add_statuses()
    try:
        with nogil: CHKERR( MPI_Waitall(
            rs.count, rs.requests, rs.statuses) )
        objects = rs.get_objects()
    finally:
        rs.release(statuses)
    return objects


cdef object PyMPI_testall(requests, int *flag, statuses):
    cdef object objects = None
    cdef _p_rs rs = _p_rs.__new__(_p_rs)
    rs.acquire(requests)
    rs.add_statuses()
    try:
        with nogil: CHKERR( MPI_Testall(
            rs.count, rs.requests, flag, rs.statuses) )
        if flag[0]:
            objects = rs.get_objects()
    finally:
        rs.release(statuses)
    return objects


cdef object PyMPI_waitsome(requests, statuses):
    cdef object indices = None
    cdef object objects = None
    #
    cdef _p_rs rs = _p_rs.__new__(_p_rs)
    rs.acquire(requests)
    rs.add_indices()
    rs.add_statuses()
    try:
        with nogil: CHKERR( MPI_Waitsome(
            rs.count, rs.requests, &rs.outcount, rs.indices, rs.statuses) )
        indices = rs.get_indices()
        objects = rs.get_objects()
    finally:
        rs.release(statuses)
    #
    return (indices, objects)


cdef object PyMPI_testsome(requests, statuses):
    cdef object indices = None
    cdef object objects = None
    #
    cdef _p_rs rs = _p_rs.__new__(_p_rs)
    rs.acquire(requests)
    rs.add_indices()
    rs.add_statuses()
    try:
        with nogil: CHKERR( MPI_Testsome(
            rs.count, rs.requests, &rs.outcount, rs.indices, rs.statuses) )
        indices = rs.get_indices()
        objects = rs.get_objects()
    finally:
        rs.release(statuses)
    #
    return (indices, objects)

# -----------------------------------------------------------------------------

cdef object PyMPI_probe(int source, int tag,
                        MPI_Comm comm, MPI_Status *status):
    with nogil: CHKERR( MPI_Probe(source, tag, comm, status) )
    return True

cdef object PyMPI_iprobe(int source, int tag,
                         MPI_Comm comm, MPI_Status *status):
    cdef int flag = 0
    with nogil: CHKERR( MPI_Iprobe(source, tag, comm, &flag, status) )
    return <bint>flag

cdef object PyMPI_mprobe(int source, int tag, MPI_Comm comm,
                         MPI_Message *message, MPI_Status *status):
    cdef void* rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    cdef MPI_Status rsts
    if (status == MPI_STATUS_IGNORE): status = &rsts
    with nogil: CHKERR( MPI_Mprobe(source, tag, comm, message, status) )
    if message[0] == MPI_MESSAGE_NO_PROC: return None
    CHKERR( MPI_Get_count_c(status, rtype, &rcount) )
    cdef object rmsg = pickle_alloc(&rbuf, rcount)
    return rmsg

cdef object PyMPI_improbe(int source, int tag, MPI_Comm comm, int *flag,
                          MPI_Message *message, MPI_Status *status):
    cdef void* rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    cdef MPI_Status rsts
    if (status == MPI_STATUS_IGNORE): status = &rsts
    with nogil: CHKERR( MPI_Improbe(source, tag, comm, flag, message, status) )
    if flag[0] == 0 or message[0] == MPI_MESSAGE_NO_PROC: return None
    CHKERR( MPI_Get_count_c(status, rtype, &rcount) )
    cdef object rmsg = pickle_alloc(&rbuf, rcount)
    return rmsg

cdef object PyMPI_mrecv(object rmsg,
                        MPI_Message *message, MPI_Status *status):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef void* rbuf = NULL
    cdef MPI_Aint rlen = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    if message[0] == MPI_MESSAGE_NO_PROC:
        rmsg = None
    elif rmsg is None:
        pass
    elif PyBytes_CheckExact(rmsg):
        rmsg = asbuffer_r(rmsg, &rbuf, &rlen)
    else:
        rmsg = asbuffer_w(rmsg, &rbuf, &rlen)  #~> unreachable
    cdef MPI_Count rcount = <MPI_Count> rlen
    with nogil: CHKERR( MPI_Mrecv_c(
        rbuf, rcount, rtype, message, status) )
    rmsg = pickle_load(pickle, rbuf, rcount)
    return rmsg

cdef object PyMPI_imrecv(object rmsg,
                         MPI_Message *message, MPI_Request *request):
    cdef void* rbuf = NULL
    cdef MPI_Aint rlen = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    if message[0] == MPI_MESSAGE_NO_PROC:
        rmsg = None
    elif rmsg is None:
        pass
    elif PyBytes_CheckExact(rmsg):
        rmsg = asbuffer_r(rmsg, &rbuf, &rlen)
    else:
        rmsg = asbuffer_w(rmsg, &rbuf, &rlen)  #~> unreachable
    cdef MPI_Count rcount = <MPI_Count> rlen
    with nogil: CHKERR( MPI_Imrecv_c(
        rbuf, rcount, rtype, message, request) )
    return rmsg

# -----------------------------------------------------------------------------

cdef object PyMPI_barrier(MPI_Comm comm):
    with nogil: CHKERR( MPI_Barrier(comm) )
    return None


cdef object PyMPI_bcast(object obj, int root, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *buf = NULL
    cdef MPI_Count count = 0
    cdef MPI_Datatype dtype = MPI_BYTE
    #
    cdef int dosend=0, dorecv=0
    cdef int inter=0, rank=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        if root == MPI_PROC_NULL:
            dosend=0; dorecv=0;
        elif root == MPI_ROOT:
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
    cdef object rmsg = None
    #
    if dosend: smsg = pickle_dump(pickle, obj, &buf, &count)
    if dosend and dorecv: rmsg = smsg
    with PyMPI_Lock(comm, "bcast"):
        with nogil: CHKERR( MPI_Bcast_c(
            &count, 1, MPI_COUNT,
            root, comm) )
        if dorecv and not dosend:
            rmsg = pickle_alloc(&buf, count)
        with nogil: CHKERR( MPI_Bcast_c(
            buf, count, dtype,
            root, comm) )
    if dorecv: rmsg = pickle_load(pickle, buf, count)
    #
    return rmsg


cdef object PyMPI_gather(object sendobj, int root, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef MPI_Count *rcounts = NULL
    cdef MPI_Aint  *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int dosend=0, dorecv=0
    cdef int inter=0, size=0, rank=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
        if root == MPI_PROC_NULL:
            dosend=0; dorecv=0;
        elif root == MPI_ROOT:
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
    cdef object tmps = None
    cdef object rmsg = None
    cdef object tmp1
    #
    if dorecv: tmp1 = allocate_count_displ(size, &rcounts, &rdispls)
    if dosend: tmps = pickle_dump(pickle, sendobj, &sbuf, &scount)
    with PyMPI_Lock(comm, "gather"):
        with nogil: CHKERR( MPI_Gather_c(
            &scount, 1, MPI_COUNT,
            rcounts, 1, MPI_COUNT,
            root, comm) )
        if dorecv: rmsg = pickle_allocv(&rbuf, size, rcounts, rdispls)
        with nogil: CHKERR( MPI_Gatherv_c(
            sbuf, scount,           stype,
            rbuf, rcounts, rdispls, rtype,
            root, comm) )
    if dorecv: rmsg = pickle_loadv(pickle, rbuf, size, rcounts, rdispls)
    #
    return rmsg


cdef object PyMPI_scatter(object sendobj, int root, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count *scounts = NULL
    cdef MPI_Aint  *sdispls = NULL
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int dosend=0, dorecv=0
    cdef int inter=0, size=0, rank=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
        if root == MPI_PROC_NULL:
            dosend=0; dorecv=0;
        elif root == MPI_ROOT:
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
    cdef object tmps = None
    cdef object rmsg = None
    cdef object tmp1
    #
    if dosend: tmp1 = allocate_count_displ(size, &scounts, &sdispls)
    if dosend: tmps = pickle_dumpv(pickle, sendobj, &sbuf, size, scounts, sdispls)
    with PyMPI_Lock(comm, "scatter"):
        with nogil: CHKERR( MPI_Scatter_c(
            scounts, 1, MPI_COUNT,
            &rcount, 1, MPI_COUNT,
            root, comm) )
        if dorecv: rmsg = pickle_alloc(&rbuf, rcount)
        with nogil: CHKERR( MPI_Scatterv_c(
            sbuf, scounts, sdispls, stype,
            rbuf, rcount,           rtype,
            root, comm) )
    if dorecv: rmsg = pickle_load(pickle, rbuf, rcount)
    #
    return rmsg


cdef object PyMPI_allgather(object sendobj, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef MPI_Count *rcounts = NULL
    cdef MPI_Aint  *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int inter=0, size=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
    else:
        CHKERR( MPI_Comm_size(comm, &size) )
    #
    cdef object tmps = None
    cdef object rmsg = None
    cdef object tmp1
    #
    tmp1 = allocate_count_displ(size, &rcounts, &rdispls)
    tmps = pickle_dump(pickle, sendobj, &sbuf, &scount)
    with PyMPI_Lock(comm, "allgather"):
        with nogil: CHKERR( MPI_Allgather_c(
            &scount, 1, MPI_COUNT,
            rcounts, 1, MPI_COUNT,
            comm) )
        rmsg = pickle_allocv(&rbuf, size, rcounts, rdispls)
        with nogil: CHKERR( MPI_Allgatherv_c(
            sbuf, scount,           stype,
            rbuf, rcounts, rdispls, rtype,
            comm) )
    rmsg = pickle_loadv(pickle, rbuf, size, rcounts, rdispls)
    #
    return rmsg


cdef object PyMPI_alltoall(object sendobj, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count *scounts = NULL
    cdef MPI_Aint  *sdispls = NULL
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef MPI_Count *rcounts = NULL
    cdef MPI_Aint  *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int inter=0, size=0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter:
        CHKERR( MPI_Comm_remote_size(comm, &size) )
    else:
        CHKERR( MPI_Comm_size(comm, &size) )
    #
    cdef object tmps = None
    cdef object rmsg = None
    cdef object tmp1, tmp2
    #
    tmp1 = allocate_count_displ(size, &scounts, &sdispls)
    tmp2 = allocate_count_displ(size, &rcounts, &rdispls)
    tmps = pickle_dumpv(pickle, sendobj, &sbuf, size, scounts, sdispls)
    with PyMPI_Lock(comm, "alltoall"):
        with nogil: CHKERR( MPI_Alltoall_c(
            scounts, 1, MPI_COUNT,
            rcounts, 1, MPI_COUNT,
            comm) )
        rmsg = pickle_allocv(&rbuf, size, rcounts, rdispls)
        with nogil: CHKERR( MPI_Alltoallv_c(
            sbuf, scounts, sdispls, stype,
            rbuf, rcounts, rdispls, rtype,
            comm) )
    rmsg = pickle_loadv(pickle, rbuf, size, rcounts, rdispls)
    #
    return rmsg


cdef object PyMPI_neighbor_allgather(object sendobj, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef MPI_Count *rcounts = NULL
    cdef MPI_Aint  *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int rsize=0
    comm_neighbors_count(comm, &rsize, NULL)
    #
    cdef object tmps = None
    cdef object rmsg = None
    cdef object tmp1
    #
    tmp1 = allocate_count_displ(rsize, &rcounts, &rdispls)
    for i in range(rsize): rcounts[i] = 0
    tmps = pickle_dump(pickle, sendobj, &sbuf, &scount)
    with PyMPI_Lock(comm, "neighbor_allgather"):
        with nogil: CHKERR( MPI_Neighbor_allgather_c(
            &scount, 1, MPI_COUNT,
            rcounts, 1, MPI_COUNT,
            comm) )
        rmsg = pickle_allocv(&rbuf, rsize, rcounts, rdispls)
        with nogil: CHKERR( MPI_Neighbor_allgatherv_c(
            sbuf, scount,           stype,
            rbuf, rcounts, rdispls, rtype,
            comm) )
    rmsg = pickle_loadv(pickle, rbuf, rsize, rcounts, rdispls)
    #
    return rmsg


cdef object PyMPI_neighbor_alltoall(object sendobj, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    #
    cdef void *sbuf = NULL
    cdef MPI_Count *scounts = NULL
    cdef MPI_Aint  *sdispls = NULL
    cdef MPI_Datatype stype = MPI_BYTE
    cdef void *rbuf = NULL
    cdef MPI_Count *rcounts = NULL
    cdef MPI_Aint  *rdispls = NULL
    cdef MPI_Datatype rtype = MPI_BYTE
    #
    cdef int ssize=0, rsize=0
    comm_neighbors_count(comm, &rsize, &ssize)
    #
    cdef object tmps = None
    cdef object rmsg = None
    cdef object tmp1, tmp2
    #
    tmp1 = allocate_count_displ(ssize, &scounts, &sdispls)
    tmp2 = allocate_count_displ(rsize, &rcounts, &rdispls)
    for i in range(rsize): rcounts[i] = 0
    tmps = pickle_dumpv(pickle, sendobj, &sbuf, ssize, scounts, sdispls)
    with PyMPI_Lock(comm, "neighbor_alltoall"):
        with nogil: CHKERR( MPI_Neighbor_alltoall_c(
            scounts, 1, MPI_COUNT,
            rcounts, 1, MPI_COUNT,
            comm) )
        rmsg = pickle_allocv(&rbuf, rsize, rcounts, rdispls)
        with nogil: CHKERR( MPI_Neighbor_alltoallv_c(
            sbuf, scounts, sdispls, stype,
            rbuf, rcounts, rdispls, rtype,
            comm) )
    rmsg = pickle_loadv(pickle, rbuf, rsize, rcounts, rdispls)
    #
    return rmsg

# -----------------------------------------------------------------------------

cdef inline object _py_reduce(object seq, object op):
    if seq is None: return None
    cdef Py_ssize_t i, n = len(seq)
    cdef object res = seq[0]
    for i in range(1, n):
        res = op(res, seq[i])
    return res

cdef inline object _py_scan(object seq, object op):
    if seq is None: return None
    cdef Py_ssize_t i, n = len(seq)
    for i in range(1, n):
        seq[i] = op(seq[i-1], seq[i])
    return seq

cdef inline object _py_exscan(object seq, object op):
    if seq is None: return None
    seq = _py_scan(seq, op)
    seq.pop(-1)
    seq.insert(0, None)
    return seq

cdef object PyMPI_reduce_naive(object sendobj, object op,
                               int root, MPI_Comm comm):
    cdef object items = PyMPI_gather(sendobj, root, comm)
    return _py_reduce(items, op)

cdef object PyMPI_allreduce_naive(object sendobj, object op, MPI_Comm comm):
    cdef object items = PyMPI_allgather(sendobj, comm)
    return _py_reduce(items, op)

cdef object PyMPI_scan_naive(object sendobj, object op, MPI_Comm comm):
    cdef object items = PyMPI_gather(sendobj, 0, comm)
    items = _py_scan(items, op)
    return PyMPI_scatter(items, 0, comm)

cdef object PyMPI_exscan_naive(object sendobj, object op, MPI_Comm comm):
    cdef object items = PyMPI_gather(sendobj, 0, comm)
    items = _py_exscan(items, op)
    return PyMPI_scatter(items, 0, comm)

# ---

cdef object PyMPI_copy(object obj):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef void *buf = NULL
    cdef MPI_Count count = 0
    obj = pickle_dump(pickle, obj, &buf, &count)
    return pickle_load(pickle, buf, count)

cdef object PyMPI_send_p2p(object obj, int dst, int tag, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef void *sbuf = NULL
    cdef MPI_Count scount = 0
    cdef MPI_Datatype stype = MPI_BYTE
    cdef object tmps = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Send_c(&scount, 1, MPI_COUNT, dst, tag, comm) )
    with nogil: CHKERR( MPI_Send_c(sbuf, scount, stype, dst, tag, comm) )
    return None

cdef object PyMPI_recv_p2p(int src, int tag, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef void *rbuf = NULL
    cdef MPI_Count rcount = 0
    cdef MPI_Datatype rtype = MPI_BYTE
    cdef MPI_Status *status = MPI_STATUS_IGNORE
    with nogil: CHKERR( MPI_Recv_c(&rcount, 1, MPI_COUNT, src, tag, comm, status) )
    cdef object tmpr = pickle_alloc(&rbuf, rcount)
    with nogil: CHKERR( MPI_Recv_c(rbuf, rcount, rtype, src, tag, comm, status) )
    return pickle_load(pickle, rbuf, rcount)

cdef object PyMPI_sendrecv_p2p(object obj,
                               int dst, int stag,
                               int src, int rtag,
                               MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef void *sbuf = NULL, *rbuf = NULL
    cdef MPI_Count scount = 0, rcount = 0
    cdef MPI_Datatype dtype = MPI_BYTE
    cdef object tmps = pickle_dump(pickle, obj, &sbuf, &scount)
    with nogil: CHKERR( MPI_Sendrecv_c(
            &scount, 1, MPI_COUNT, dst, stag,
            &rcount, 1, MPI_COUNT, src, rtag,
            comm, MPI_STATUS_IGNORE) )
    cdef object tmpr = pickle_alloc(&rbuf, rcount)
    with nogil: CHKERR( MPI_Sendrecv_c(
            sbuf, scount, dtype, dst, stag,
            rbuf, rcount, dtype, src, rtag,
            comm, MPI_STATUS_IGNORE) )
    return pickle_load(pickle, rbuf, rcount)

cdef object PyMPI_bcast_p2p(object obj, int root, MPI_Comm comm):
    cdef Pickle pickle = PyMPI_PICKLE
    cdef void *buf = NULL
    cdef MPI_Count count = 0
    cdef MPI_Datatype dtype = MPI_BYTE
    cdef int rank = MPI_PROC_NULL
    CHKERR( MPI_Comm_rank(comm, &rank) )
    if root == rank: obj = pickle_dump(pickle, obj, &buf, &count)
    with PyMPI_Lock(comm, "@bcast_p2p@"):
        with nogil: CHKERR( MPI_Bcast_c(&count, 1, MPI_COUNT, root, comm) )
        if root != rank: obj = pickle_alloc(&buf, count)
        with nogil: CHKERR( MPI_Bcast_c(buf, count, dtype, root, comm) )
    return pickle_load(pickle, buf, count)

cdef object PyMPI_reduce_p2p(object sendobj, object op, int root,
                             MPI_Comm comm, int tag):
    # Get communicator size and rank
    cdef int size = MPI_UNDEFINED
    cdef int rank = MPI_PROC_NULL
    CHKERR( MPI_Comm_size(comm, &size) )
    CHKERR( MPI_Comm_rank(comm, &rank) )
    # Check root argument
    if root < 0 or root >= size:
        <void>MPI_Comm_call_errhandler(comm, MPI_ERR_ROOT)
        raise MPIException(MPI_ERR_ROOT)
    #
    cdef object result = PyMPI_copy(sendobj)
    cdef object tmp
    # Compute reduction at process 0
    cdef unsigned int umask = <unsigned int> 1
    cdef unsigned int usize = <unsigned int> size
    cdef unsigned int urank = <unsigned int> rank
    cdef int target = 0
    while umask < usize:
        if (umask & urank) != 0:
            target = <int> ((urank & ~umask) % usize)
            PyMPI_send_p2p(result, target, tag, comm)
        else:
            target = <int> (urank | umask)
            if target < size:
                tmp = PyMPI_recv_p2p(target, tag, comm)
                result = op(result, tmp)
        umask <<= 1
    # Send reduction to root
    if root != 0:
        if rank == 0:
            PyMPI_send_p2p(result, root, tag, comm)
        elif rank == root:
            result = PyMPI_recv_p2p(0, tag, comm)
    if rank != root:
        result = None
    #
    return result

cdef object PyMPI_scan_p2p(object sendobj, object op,
                           MPI_Comm comm, int tag):
    # Get communicator size and rank
    cdef int size = MPI_UNDEFINED
    cdef int rank = MPI_PROC_NULL
    CHKERR( MPI_Comm_size(comm, &size) )
    CHKERR( MPI_Comm_rank(comm, &rank) )
    #
    cdef object result  = PyMPI_copy(sendobj)
    cdef object partial = result
    cdef object tmp
    # Compute prefix reduction
    cdef unsigned int umask = <unsigned int> 1
    cdef unsigned int usize = <unsigned int> size
    cdef unsigned int urank = <unsigned int> rank
    cdef int target = 0
    while umask < usize:
        target = <int> (urank ^ umask)
        if target < size:
            tmp = PyMPI_sendrecv_p2p(partial, target, tag,
                                     target, tag, comm)
            if rank > target:
                partial = op(tmp, partial)
                result = op(tmp, result)
            else:
                tmp = op(partial, tmp)
                partial = tmp
        umask <<= 1
    #
    return result

cdef object PyMPI_exscan_p2p(object sendobj, object op,
                             MPI_Comm comm, int tag):
    # Get communicator size and rank
    cdef int size = MPI_UNDEFINED
    cdef int rank = MPI_PROC_NULL
    CHKERR( MPI_Comm_size(comm, &size) )
    CHKERR( MPI_Comm_rank(comm, &rank) )
    #
    cdef object result  = PyMPI_copy(sendobj)
    cdef object partial = result
    cdef object tmp
    # Compute prefix reduction
    cdef unsigned int umask = <unsigned int> 1
    cdef unsigned int usize = <unsigned int> size
    cdef unsigned int urank = <unsigned int> rank
    cdef unsigned int uflag = <unsigned int> 0
    cdef int target = 0
    while umask < usize:
        target = <int> (urank ^ umask)
        if target < size:
            tmp = PyMPI_sendrecv_p2p(partial, target, tag,
                                     target, tag, comm)
            if rank > target:
                partial = op(tmp, partial)
                if uflag == 0:
                    result = tmp; uflag = 1
                else:
                    result = op(tmp, result)
            else:
                tmp = op(partial, tmp)
                partial = tmp
        umask <<= 1
    #
    if rank == 0:
        result = None
    return result

# ---

cdef extern from * nogil:
    int PyMPI_Commctx_intra(MPI_Comm,MPI_Comm*,int*)
    int PyMPI_Commctx_inter(MPI_Comm,MPI_Comm*,int*,MPI_Comm*,int*)
    int PyMPI_Commctx_finalize()

cdef int PyMPI_Commctx_INTRA(
    MPI_Comm comm,
    MPI_Comm *dupcomm, int *tag,
) except -1:
    with PyMPI_Lock(comm, "@commctx_intra"):
        CHKERR( PyMPI_Commctx_intra(comm, dupcomm, tag) )
    return 0

cdef int PyMPI_Commctx_INTER(
    MPI_Comm comm,
    MPI_Comm *dupcomm, int *tag,
    MPI_Comm *localcomm, int *low_group,
) except -1:
    with PyMPI_Lock(comm, "@commctx_inter"):
        CHKERR( PyMPI_Commctx_inter(comm, dupcomm, tag,
                                    localcomm, low_group) )
    return 0


def _commctx_intra(
    Intracomm comm: Intracomm,
) -> tuple[Intracomm, int]:
    """
    Create/get intracommunicator duplicate.
    """
    cdef int tag = MPI_UNDEFINED
    cdef Intracomm dupcomm = <Intracomm>New(Intracomm)
    PyMPI_Commctx_INTRA(comm.ob_mpi, &dupcomm.ob_mpi, &tag)
    return (dupcomm, tag)

def _commctx_inter(
    Intercomm comm: Intercomm,
) -> tuple[Intercomm, int, Intracomm, bool]:
    """
    Create/get intercommunicator duplicate.
    """
    cdef int tag = MPI_UNDEFINED, low_group = 0
    cdef Intercomm dupcomm = <Intercomm>New(Intercomm)
    cdef Intracomm localcomm = <Intracomm>New(Intracomm)
    PyMPI_Commctx_INTER(comm.ob_mpi, &dupcomm.ob_mpi, &tag,
                        &localcomm.ob_mpi, &low_group)
    return (dupcomm, tag, localcomm, <bint>low_group)

# ---

cdef object PyMPI_reduce_intra(object sendobj, object op,
                               int root, MPI_Comm comm):
    cdef int tag = MPI_UNDEFINED
    PyMPI_Commctx_INTRA(comm, &comm, &tag)
    return PyMPI_reduce_p2p(sendobj, op, root, comm, tag)

cdef object PyMPI_reduce_inter(object sendobj, object op,
                               int root, MPI_Comm comm):
    cdef int tag = MPI_UNDEFINED
    cdef MPI_Comm localcomm = MPI_COMM_NULL
    PyMPI_Commctx_INTER(comm, &comm, &tag, &localcomm, NULL)
    # Get communicator remote size and rank
    cdef int size = MPI_UNDEFINED
    cdef int rank = MPI_PROC_NULL
    CHKERR( MPI_Comm_remote_size(comm, &size) )
    CHKERR( MPI_Comm_rank(comm, &rank) )
    if root >= 0 and root < size:
        # Reduce in local group and send to remote root
        sendobj = PyMPI_reduce_p2p(sendobj, op, 0, localcomm, tag)
        if rank == 0: PyMPI_send_p2p(sendobj, root, tag, comm)
        return None
    elif root == MPI_ROOT: # Receive from remote group
        return PyMPI_recv_p2p(0, tag, comm)
    elif root == MPI_PROC_NULL: # This process does nothing
        return None
    else: # Wrong root argument
        <void>MPI_Comm_call_errhandler(comm, MPI_ERR_ROOT)
        raise MPIException(MPI_ERR_ROOT)


cdef object PyMPI_allreduce_intra(object sendobj, object op, MPI_Comm comm):
    cdef int tag = MPI_UNDEFINED
    PyMPI_Commctx_INTRA(comm, &comm, &tag)
    sendobj = PyMPI_reduce_p2p(sendobj, op, 0, comm, tag)
    return PyMPI_bcast_p2p(sendobj, 0, comm)

cdef object PyMPI_allreduce_inter(object sendobj, object op, MPI_Comm comm):
    cdef int tag = MPI_UNDEFINED
    cdef int rank = MPI_PROC_NULL
    cdef MPI_Comm localcomm = MPI_COMM_NULL
    PyMPI_Commctx_INTER(comm, &comm, &tag, &localcomm, NULL)
    CHKERR( MPI_Comm_rank(comm, &rank) )
    # Reduce in local group, exchange, and broadcast in local group
    sendobj = PyMPI_reduce_p2p(sendobj, op, 0, localcomm, tag)
    if rank == 0:
        sendobj = PyMPI_sendrecv_p2p(sendobj, 0, tag, 0, tag, comm)
    return PyMPI_bcast_p2p(sendobj, 0, localcomm)


cdef object PyMPI_scan_intra(object sendobj, object op, MPI_Comm comm):
    cdef int tag = MPI_UNDEFINED
    PyMPI_Commctx_INTRA(comm, &comm, &tag)
    return PyMPI_scan_p2p(sendobj, op, comm, tag)

cdef object PyMPI_exscan_intra(object sendobj, object op, MPI_Comm comm):
    cdef int tag = MPI_UNDEFINED
    PyMPI_Commctx_INTRA(comm, &comm, &tag)
    return PyMPI_exscan_p2p(sendobj, op, comm, tag)

# ---

cdef inline bint comm_is_intra(MPI_Comm comm) except -1 nogil:
    cdef int inter = 0
    CHKERR( MPI_Comm_test_inter(comm, &inter) )
    if inter: return 0
    else:     return 1


cdef object PyMPI_reduce(object sendobj, object op, int root, MPI_Comm comm):
    if not options.fast_reduce:
        return PyMPI_reduce_naive(sendobj, op, root, comm)
    elif comm_is_intra(comm):
        return PyMPI_reduce_intra(sendobj, op, root, comm)
    else:
        return PyMPI_reduce_inter(sendobj, op, root, comm)


cdef object PyMPI_allreduce(object sendobj, object op, MPI_Comm comm):
    if not options.fast_reduce:
        return PyMPI_allreduce_naive(sendobj, op, comm)
    elif comm_is_intra(comm):
        return PyMPI_allreduce_intra(sendobj, op, comm)
    else:
        return PyMPI_allreduce_inter(sendobj, op, comm)


cdef object PyMPI_scan(object sendobj, object op, MPI_Comm comm):
    if not options.fast_reduce:
        return PyMPI_scan_naive(sendobj, op, comm)
    else:
        return PyMPI_scan_intra(sendobj, op, comm)


cdef object PyMPI_exscan(object sendobj, object op, MPI_Comm comm):
    if not options.fast_reduce:
        return PyMPI_exscan_naive(sendobj, op, comm)
    else:
        return PyMPI_exscan_intra(sendobj, op, comm)

# -----------------------------------------------------------------------------
