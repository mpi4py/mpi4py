# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Pickle-based communication using protocol 5."""

import struct as _struct

from .. import MPI
from ..MPI import (
    ROOT,
    PROC_NULL,
    ANY_SOURCE,
    ANY_TAG,
    Status,
)

from ..MPI import (
    Pickle,
    _comm_lock,
    _commctx_intra,
    _commctx_inter,
)

pickle = Pickle()


def _pickle_dumps(obj):
    return pickle.dumps_oob(obj)


def _pickle_loads(data, bufs):
    return pickle.loads_oob(data, bufs)


def _bigmpi_create_type(basetype, count, blocksize):
    qsize, rsize = divmod(count, blocksize)
    qtype = basetype.Create_vector(
        qsize, blocksize, blocksize)
    rtype = basetype.Create_contiguous(rsize)
    rdisp = qtype.Get_extent()[1]
    bigtype = MPI.Datatype.Create_struct(
        (1, 1), (0, rdisp), (qtype, rtype))
    qtype.Free()
    rtype.Free()
    return bigtype


class _BigMPI:
    """Support for large message counts."""

    blocksize = 1024**3  # 1 GiB
    if MPI.VERSION >= 4:  # pragma: no cover
        blocksize = 1024**6  # 1 EiB

    def __init__(self):
        self.cache = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        cache = self.cache
        for dtype in cache.values():
            dtype.Free()
        cache.clear()

    def __call__(self, buf):
        buf = memoryview(buf)
        count = buf.nbytes
        blocksize = self.blocksize
        if count < blocksize:
            return (buf, count, MPI.BYTE)
        cache = self.cache
        dtype = cache.get(count)
        if dtype is not None:
            return (buf, 1, dtype)
        dtype = _bigmpi_create_type(MPI.BYTE, count, blocksize)
        cache[count] = dtype.Commit()
        return (buf, 1, dtype)


_bigmpi = _BigMPI()


def _info_typecode():
    return 'q'


def _info_datatype():
    code = _info_typecode()
    return MPI.Datatype.fromcode(code)


def _info_pack(info):
    code = _info_typecode()
    size = len(info)
    return _struct.pack(f"{size}{code}", *info)


def _info_alloc(size):
    code = _info_typecode()
    itemsize = _struct.calcsize(code)
    return bytearray(size * itemsize)


def _info_unpack(info):
    code = _info_typecode()
    itemsize = _struct.calcsize(code)
    size = len(info) // itemsize
    return _struct.unpack(f"{size}{code}", info)


def _new_buffer(size):
    return MPI.buffer.allocate(size)


def _send_raw(comm, send, data, bufs, dest, tag):
    # pylint: disable=too-many-arguments
    info = [len(data)]
    info.extend(len(sbuf) for sbuf in bufs)
    infotype = _info_datatype()
    info = _info_pack(info)
    send(comm, (info, infotype), dest, tag)
    with _bigmpi as bigmpi:
        send(comm, bigmpi(data), dest, tag)
        for sbuf in bufs:
            send(comm, bigmpi(sbuf), dest, tag)


def _send(comm, send, obj, dest, tag):
    if dest == PROC_NULL:
        send(comm, (None, 0, MPI.BYTE), dest, tag)
        return
    data, bufs = _pickle_dumps(obj)
    with _comm_lock(comm, 'send'):
        _send_raw(comm, send, data, bufs, dest, tag)


def _isend(comm, isend, obj, dest, tag):
    def send(comm, buf, dest, tag):
        sreqs.append(isend(comm, buf, dest, tag))
    sreqs = []
    _send(comm, send, obj, dest, tag)
    request = Request(sreqs)
    return request


def _recv_raw(comm, recv, buf, source, tag, status=None):
    # pylint: disable=too-many-arguments
    if status is None:
        status = Status()
    MPI.Comm.Probe(comm, source, tag, status)
    source = status.Get_source()
    tag = status.Get_tag()
    infotype = _info_datatype()
    infosize = status.Get_elements(infotype)
    info = _info_alloc(infosize)
    MPI.Comm.Recv(comm, (info, infotype), source, tag, status)
    info = _info_unpack(info)
    if buf is not None:
        buf = memoryview(buf).cast('B')
        if len(buf) > info[0]:
            buf = buf[:info[0]]
        if len(buf) < info[0]:
            buf = None
    data = _new_buffer(info[0]) if buf is None else buf
    bufs = list(map(_new_buffer, info[1:]))
    with _bigmpi as bigmpi:
        recv(comm, bigmpi(data), source, tag)
        for rbuf in bufs:
            recv(comm, bigmpi(rbuf), source, tag)
    status.Set_elements(MPI.BYTE, sum(info))
    return data, bufs


def _recv(comm, recv, buf, source, tag, status):
    # pylint: disable=too-many-arguments
    if source == PROC_NULL:
        recv(comm, (None, 0, MPI.BYTE), source, tag, status)
        return None
    with _comm_lock(comm, 'recv'):
        data, bufs = _recv_raw(comm, recv, buf, source, tag, status)
    return _pickle_loads(data, bufs)


def _mprobe(comm, mprobe, source, tag, status):
    if source == PROC_NULL:
        rmsg = MPI.Comm.Mprobe(comm, source, tag, status)
        return Message([rmsg])
    if status is None:
        status = Status()
    with _comm_lock(comm, 'recv'):
        message = []
        numbytes = 0
        rmsg = mprobe(comm, source, tag, status)
        if rmsg is None:
            return None
        message.append(rmsg)
        source = status.Get_source()
        tag = status.Get_tag()
        infotype = _info_datatype()
        infosize = status.Get_elements(infotype)
        for _ in range(infosize):
            rmsg = MPI.Comm.Mprobe(comm, source, tag, status)
            message.append(rmsg)
            numbytes += status.Get_elements(MPI.BYTE)
        status.Set_elements(MPI.BYTE, numbytes)
        return Message(message)


def _mrecv_info(rmsg, size, status=None):
    mrecv = MPI.Message.Recv
    infotype = _info_datatype()
    info = _info_alloc(size)
    mrecv(rmsg, (info, infotype), status)
    info = _info_unpack(info)
    return info


def _mrecv_none(rmsg, mrecv, status):
    _mrecv_info(rmsg, 0, status)
    noproc = MPI.MESSAGE_NO_PROC
    mrecv(noproc, (None, 0, MPI.BYTE))
    data, bufs = _pickle_dumps(None)
    return (bytearray(data), bufs)


def _mrecv_data(message, mrecv, status=None):
    if message[0] == MPI.MESSAGE_NO_PROC:
        rmsg = message[0]
        return _mrecv_none(rmsg, mrecv, status)
    rmsg = iter(message)
    icnt = len(message) - 1
    info = _mrecv_info(next(rmsg), icnt, status)
    data = _new_buffer(info[0])
    bufs = list(map(_new_buffer, info[1:]))
    with _bigmpi as bigmpi:
        mrecv(next(rmsg), bigmpi(data))
        for rbuf in bufs:
            mrecv(next(rmsg), bigmpi(rbuf))
    if status is not None:
        status.Set_elements(MPI.BYTE, sum(info))
    return (data, bufs)


def _mrecv(message, status):
    def mrecv(rmsg, buf):
        MPI.Message.Recv(rmsg, buf)
    data, bufs = _mrecv_data(message, mrecv, status)
    return _pickle_loads(data, bufs)


def _imrecv(message):
    def mrecv(rmsg, buf):
        rreqs.append(MPI.Message.Irecv(rmsg, buf))
    rreqs = []
    data, bufs = _mrecv_data(message, mrecv)
    request = Request(rreqs)
    setattr(request, '_data_bufs', (data, bufs))  # noqa: B010
    return request


def _req_load(request):
    data_bufs = getattr(request, '_data_bufs', None)
    if request == MPI.REQUEST_NULL and data_bufs is not None:
        delattr(request, '_data_bufs')
    if data_bufs is not None:
        data, bufs = data_bufs
        obj = _pickle_loads(data, bufs)
        return obj
    return None


def _test(request, test, status):
    statuses = None if status is None else [status]
    flag = test(request, statuses)
    if flag:
        obj = _req_load(request)
        return (flag, obj)
    return (flag, None)


def _testall(requests, testall, statuses):
    if isinstance(statuses, list):
        for _ in range(len(requests) - len(statuses)):
            statuses.append(Status())
    reqarray = []
    stsarray = None
    for req in requests:
        reqarray.extend(req)
    if statuses is not None:
        stsarray = []
        for req, sts in zip(requests, statuses):
            stsarray.extend([sts] * len(req))
    flag = testall(reqarray, stsarray)
    if flag:
        objs = [_req_load(req) for req in requests]
        return (flag, objs)
    return (flag, None)


def _bcast_intra_raw(comm, bcast, data, bufs, root):
    rank = comm.Get_rank()
    if rank == root:
        info = [len(data)]
        info.extend(len(sbuf) for sbuf in bufs)
        infotype = _info_datatype()
        infosize = _info_pack([len(info)])
        bcast(comm, (infosize, infotype), root)
        info = _info_pack(info)
        bcast(comm, (info, infotype), root)
    else:
        infotype = _info_datatype()
        infosize = _info_alloc(1)
        bcast(comm, (infosize, infotype), root)
        infosize = _info_unpack(infosize)[0]
        info = _info_alloc(infosize)
        bcast(comm, (info, infotype), root)
        info = _info_unpack(info)
        data = _new_buffer(info[0])
        bufs = list(map(_new_buffer, info[1:]))
    with _bigmpi as bigmpi:
        bcast(comm, bigmpi(data), root)
        for rbuf in bufs:
            bcast(comm, bigmpi(rbuf), root)
    return data, bufs


def _bcast_intra(comm, bcast, obj, root):
    rank = comm.Get_rank()
    if rank == root:
        data, bufs = _pickle_dumps(obj)
    else:
        data, bufs = _pickle_dumps(None)
    with _comm_lock(comm, 'bcast'):
        data, bufs = _bcast_intra_raw(comm, bcast, data, bufs, root)
    return _pickle_loads(data, bufs)


def _bcast_inter(comm, bcast, obj, root):
    rank = comm.Get_rank()
    size = comm.Get_remote_size()
    comm, tag, localcomm, _ = _commctx_inter(comm)
    if root == PROC_NULL:
        return None
    elif root == ROOT:
        send = MPI.Comm.Send
        data, bufs = _pickle_dumps(obj)
        _send_raw(comm, send, data, bufs, 0, tag)
        return None
    elif 0 <= root < size:
        if rank == 0:
            recv = MPI.Comm.Recv
            data, bufs = _recv_raw(comm, recv, None, root, tag)
        else:
            data, bufs = _pickle_dumps(None)
        with _comm_lock(localcomm, 'bcast'):
            data, bufs = _bcast_intra_raw(localcomm, bcast, data, bufs, 0)
        return _pickle_loads(data, bufs)
    comm.Call_errhandler(MPI.ERR_ROOT)
    raise MPI.Exception(MPI.ERR_ROOT)


def _bcast(comm, bcast, obj, root):
    if comm.Is_inter():
        return _bcast_inter(comm, bcast, obj, root)
    else:
        return _bcast_intra(comm, bcast, obj, root)


def _get_p2p_backend():
    reqs = []

    def send(comm, buf, dest, tag):
        reqs.append(MPI.Comm.Isend(comm, buf, dest, tag))

    def recv(comm, buf, source, tag):
        MPI.Comm.Recv(comm, buf, source, tag)

    return reqs, send, recv


def _gather(comm, obj, root):
    reqs, send, recv = _get_p2p_backend()
    if comm.Is_inter():
        comm, tag, *_ = _commctx_inter(comm)
        size = comm.Get_remote_size()
        if root == PROC_NULL:
            send = recv = None
        elif root == MPI.ROOT:
            send = None
        elif 0 <= root < size:
            recv = None
        else:
            comm.Call_errhandler(MPI.ERR_ROOT)
            raise MPI.Exception(MPI.ERR_ROOT)
    else:
        comm, tag = _commctx_intra(comm)
        size = comm.Get_size()
        if root != comm.Get_rank():
            recv = None
        if root < 0 or root >= size:
            comm.Call_errhandler(MPI.ERR_ROOT)
            raise MPI.Exception(MPI.ERR_ROOT)

    if send:
        data, bufs = _pickle_dumps(obj)
        _send_raw(comm, send, data, bufs, root, tag)
    objs = None
    if recv:
        objs = []
        for source in range(size):
            data, bufs = _recv_raw(comm, recv, None, source, tag)
            obj = _pickle_loads(data, bufs)
            objs.append(obj)
    if send:
        MPI.Request.Waitall(reqs)
    return objs


def _scatter(comm, objs, root):
    # pylint: disable=too-many-branches
    reqs, send, recv = _get_p2p_backend()
    if comm.Is_inter():
        comm, tag, *_ = _commctx_inter(comm)
        size = comm.Get_remote_size()
        if root == PROC_NULL:
            send = recv = None
        elif root == ROOT:
            recv = None
        elif 0 <= root < size:
            send = None
        else:
            comm.Call_errhandler(MPI.ERR_ROOT)
            raise MPI.Exception(MPI.ERR_ROOT)
    else:
        comm, tag = _commctx_intra(comm)
        size = comm.Get_size()
        if root != comm.Get_rank():
            send = None
        if root < 0 or root >= size:
            comm.Call_errhandler(MPI.ERR_ROOT)
            raise MPI.Exception(MPI.ERR_ROOT)

    if send:
        if objs is None:
            objs = [None] * size
        elif not isinstance(objs, list):
            objs = list(objs)
        if len(objs) != size:
            raise ValueError(f"expecting {size} items, got {len(objs)}")
        for dest, obj in enumerate(objs):
            data, bufs = _pickle_dumps(obj)
            _send_raw(comm, send, data, bufs, dest, tag)
    obj = None
    if recv:
        data, bufs = _recv_raw(comm, recv, None, root, tag)
        obj = _pickle_loads(data, bufs)
    if send:
        MPI.Request.Waitall(reqs)
    return obj


def _allgather(comm, obj):
    reqs, send, recv = _get_p2p_backend()
    if comm.Is_inter():
        comm, tag, *_ = _commctx_inter(comm)
        size = comm.Get_remote_size()
    else:
        comm, tag = _commctx_intra(comm)
        size = comm.Get_size()

    data, bufs = _pickle_dumps(obj)
    for dest in range(size):
        _send_raw(comm, send, data, bufs, dest, tag)
    objs = []
    for source in range(size):
        data, bufs = _recv_raw(comm, recv, None, source, tag)
        obj = _pickle_loads(data, bufs)
        objs.append(obj)
    MPI.Request.Waitall(reqs)
    return objs


def _alltoall(comm, objs):
    reqs, send, recv = _get_p2p_backend()
    if comm.Is_inter():
        comm, tag, *_ = _commctx_inter(comm)
        size = comm.Get_remote_size()
    else:
        comm, tag = _commctx_intra(comm)
        size = comm.Get_size()

    if objs is None:
        objs = [None] * size
    elif not isinstance(objs, list):
        objs = list(objs)
    if len(objs) != size:
        raise ValueError(f"expecting {size} items, got {len(objs)}")
    for dest, obj in enumerate(objs):
        data, bufs = _pickle_dumps(obj)
        _send_raw(comm, send, data, bufs, dest, tag)
    objs = []
    for source in range(size):
        data, bufs = _recv_raw(comm, recv, None, source, tag)
        obj = _pickle_loads(data, bufs)
        objs.append(obj)
    MPI.Request.Waitall(reqs)
    return objs


class Request(tuple):
    """Request."""

    def __new__(cls, request=None):
        """Create and return a new object."""
        if request is None:
            request = (MPI.REQUEST_NULL,)
        if isinstance(request, MPI.Request):
            request = (request,)
        return super().__new__(cls, request)

    def __eq__(self, other):
        """Return ``self==other``."""
        if isinstance(other, Request):
            return tuple(self) == tuple(other)
        if isinstance(other, MPI.Request):
            return all(req == other for req in self)
        return NotImplemented

    def __ne__(self, other):
        """Return ``self!=other``."""
        if isinstance(other, Request):
            return tuple(self) != tuple(other)
        if isinstance(other, MPI.Request):
            return any(req != other for req in self)
        return NotImplemented

    def __bool__(self):
        """Return ``bool(self)``."""
        return any(req for req in self)

    def Free(self) -> None:
        """Free a communication request."""
        # pylint: disable=invalid-name
        for req in self:
            req.Free()

    def cancel(self):
        """Cancel a communication request."""
        for req in self:
            req.Cancel()

    def get_status(self, status=None):
        """Non-destructive test for the completion of a request."""
        statuses = [status] + [None] * max(len(self) - 1, 0)
        return all(map(MPI.Request.Get_status, self, statuses))

    def test(self, status=None):
        """Test for the completion of a request."""
        return _test(self, MPI.Request.Testall, status)

    def wait(self, status=None):
        """Wait for a request to complete."""
        return _test(self, MPI.Request.Waitall, status)[1]

    @classmethod
    def get_status_all(cls, requests, statuses=None):
        """Non-destructive test for the completion of all requests."""
        arglist = [requests]
        if statuses is not None:
            ns, nr = len(statuses), len(requests)
            statuses += [Status() for _ in range(ns, nr)]
            arglist.append(statuses)
        return all(map(Request.get_status, *arglist))

    @classmethod
    def testall(cls, requests, statuses=None):
        """Test for the completion of all requests."""
        return _testall(requests, MPI.Request.Testall, statuses)

    @classmethod
    def waitall(cls, requests, statuses=None):
        """Wait for all requests to complete."""
        return _testall(requests, MPI.Request.Waitall, statuses)[1]


class Message(tuple):
    """Message."""

    def __new__(cls, message=None):
        """Create and return a new object."""
        if message is None:
            message = (MPI.MESSAGE_NULL,)
        if isinstance(message, MPI.Message):
            message = (message,)
        return super().__new__(cls, message)

    def __eq__(self, other):
        """Return ``self==other``."""
        if isinstance(other, Message):
            return tuple(self) == tuple(other)
        if isinstance(other, MPI.Message):
            return all(msg == other for msg in self)
        return NotImplemented

    def __ne__(self, other):
        """Return ``self!=other``."""
        if isinstance(other, Message):
            return tuple(self) != tuple(other)
        if isinstance(other, MPI.Message):
            return any(msg != other for msg in self)
        return NotImplemented

    def __bool__(self):
        """Return ``bool(self)``."""
        return any(msg for msg in self)

    def recv(self, status=None):
        """Blocking receive of matched message."""
        return _mrecv(self, status)

    def irecv(self):
        """Nonblocking receive of matched message."""
        return _imrecv(self)

    @classmethod
    def probe(cls, comm,
              source=ANY_SOURCE, tag=ANY_TAG,
              status=None):
        """Blocking test for a matched message."""
        return _mprobe(comm, MPI.Comm.Mprobe, source, tag, status)

    @classmethod
    def iprobe(cls, comm,
               source=ANY_SOURCE, tag=ANY_TAG,
               status=None):
        """Nonblocking test for a matched message."""
        return _mprobe(comm, MPI.Comm.Improbe, source, tag, status)


class Comm(MPI.Comm):
    """Communicator."""

    def send(self, obj, dest, tag=0):
        """Blocking send in standard mode."""
        _send(self, MPI.Comm.Send, obj, dest, tag)

    def bsend(self, obj, dest, tag=0):
        """Blocking send in buffered mode."""
        _send(self, MPI.Comm.Bsend, obj, dest, tag)

    def ssend(self, obj, dest, tag=0):
        """Blocking send in synchronous mode."""
        sreq = _isend(self, MPI.Comm.Issend, obj, dest, tag)
        MPI.Request.Waitall(sreq)

    def isend(self, obj, dest, tag=0):
        """Nonblocking send in standard mode."""
        return _isend(self, MPI.Comm.Isend, obj, dest, tag)

    def ibsend(self, obj, dest, tag=0):
        """Nonblocking send in buffered mode."""
        return _isend(self, MPI.Comm.Ibsend, obj, dest, tag)

    def issend(self, obj, dest, tag=0):
        """Nonblocking send in synchronous mode."""
        return _isend(self, MPI.Comm.Issend, obj, dest, tag)

    def recv(self,
             buf=None, source=ANY_SOURCE, tag=ANY_TAG,
             status=None):
        """Blocking receive."""
        return _recv(self, MPI.Comm.Recv, buf, source, tag, status)

    def irecv(self,
              buf=None, source=ANY_SOURCE, tag=ANY_TAG):  # noqa: ARG002
        """Nonblocking receive."""
        raise RuntimeError("unsupported")

    def sendrecv(self,
                 sendobj, dest, sendtag=0,
                 recvbuf=None, source=ANY_SOURCE, recvtag=ANY_TAG,
                 status=None):
        """Send and receive."""
        # pylint: disable=too-many-arguments
        sreq = _isend(self, MPI.Comm.Isend, sendobj, dest, sendtag)
        robj = _recv(self, MPI.Comm.Recv, recvbuf, source, recvtag, status)
        MPI.Request.Waitall(sreq)
        return robj

    def mprobe(self,
               source=ANY_SOURCE, tag=ANY_TAG,
               status=None):
        """Blocking test for a matched message."""
        return _mprobe(self, MPI.Comm.Mprobe, source, tag, status)

    def improbe(self,
                source=ANY_SOURCE, tag=ANY_TAG,
                status=None):
        """Nonblocking test for a matched message."""
        return _mprobe(self, MPI.Comm.Improbe, source, tag, status)

    def bcast(self, obj, root=0):
        """Broadcast."""
        return _bcast(self, MPI.Comm.Bcast, obj, root)

    def gather(self, sendobj, root=0):
        """Gather."""
        return _gather(self, sendobj, root)

    def scatter(self, sendobj, root=0):
        """Scatter."""
        return _scatter(self, sendobj, root)

    def allgather(self, sendobj):
        """Gather to All."""
        return _allgather(self, sendobj)

    def alltoall(self, sendobj):
        """All to All Scatter/Gather."""
        return _alltoall(self, sendobj)


class Intracomm(Comm, MPI.Intracomm):
    """Intracommunicator."""


class Intercomm(Comm, MPI.Intercomm):
    """Intercommunicator."""
