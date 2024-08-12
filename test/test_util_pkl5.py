from mpi4py import MPI
from mpi4py.util import pkl5
import sys, os
try:
    import mpiunittest as unittest
except ImportError:
    sys.path.append(
        os.path.dirname(
            os.path.abspath(__file__)))
    import mpiunittest as unittest

_basic = [
    None,
    True, False,
    -7, 0, 7,
    -2**63+1, 2**63-1,
    -2.17, 0.0, 3.14,
    1+2j, 2-3j,
    'mpi4py',
]
messages = list(_basic)
messages += [
    list(_basic),
    tuple(_basic),
    set(_basic),
    frozenset(_basic),
    {f'k{k}': v for k, v in enumerate(_basic)},
]

try:
    import numpy
    array1 = numpy.arange(1, dtype='i')
    array2 = numpy.arange(1, dtype='f')
    messages.append(array1)
    messages.append(array2)
    messages.append([array1, array1])
    messages.append([array2, array2])
    messages.append((array1, array2))
except ImportError:
    numpy = None


class BaseTest:

    COMM = MPI.COMM_NULL
    CommType = MPI.Intracomm
    MessageType = MPI.Message
    RequestType = MPI.Request

    def setUp(self):
        self.COMM = self.CommType(self.COMM)
        self.bigmpi_prev = pkl5._bigmpi
        self.bigmpi = pkl5._BigMPI()
        pkl5._bigmpi = self.bigmpi

    def tearDown(self):
        pkl5._bigmpi = self.bigmpi_prev

    def testSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.send(smess, MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.send(smess, rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.recv(None, rank-1, 0)
            else:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.send(rmess, rank+1, 0)
            self.assertEqual(rmess, smess)

    def testISendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        buf = None
        for smess in messages:
            req = self.COMM.isend(smess, MPI.PROC_NULL)
            self.assertTrue(req)
            req.wait()
            self.assertFalse(req)
            rmess = self.COMM.recv(buf, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        for smess in messages:
            req = self.COMM.isend(smess, rank, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(buf, rank, 0)
            self.assertTrue(req)
            flag, _ = req.test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            req = self.COMM.isend(smess, dst, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(buf, src, 0)
            req.wait()
            self.assertFalse(req)
            self.assertEqual(rmess, smess)

    def testSSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.ssend(smess, MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.ssend(smess, rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.recv(None, rank-1, 0)
            else:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.ssend(rmess, rank+1, 0)
            self.assertEqual(rmess, smess)

    def testISSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            req = self.COMM.issend(smess, MPI.PROC_NULL)
            self.assertTrue(req)
            req.wait()
            self.assertFalse(req)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        for smess in messages:
            req = self.COMM.issend(smess, rank, 0)
            self.assertTrue(req)
            flag, _ = req.test()
            self.assertFalse(flag)
            self.assertTrue(req)
            rmess = self.COMM.recv(None, rank, 0)
            self.assertTrue(req)
            req.wait()
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            req = self.COMM.issend(smess, dst, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(None, src, 0)
            req.wait()
            self.assertFalse(req)
            self.assertEqual(rmess, smess)

    def testBSendAndRecv(self):
        buf = MPI.Alloc_mem((1<<16)+MPI.BSEND_OVERHEAD)
        MPI.Attach_buffer(buf)
        try:
            size = self.COMM.Get_size()
            rank = self.COMM.Get_rank()
            for smess in messages:
                self.COMM.bsend(smess, MPI.PROC_NULL)
                rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
                self.assertIsNone(rmess)
            if size == 1: return
            for smess in messages:
                if rank == 0:
                    self.COMM.bsend(smess, rank+1, 0)
                    rmess = smess
                elif rank == size - 1:
                    rmess = self.COMM.recv(None, rank-1, 0)
                else:
                    rmess = self.COMM.recv(None, rank-1, 0)
                    self.COMM.bsend(rmess, rank+1, 0)
                self.assertEqual(rmess, smess)
        finally:
            MPI.Detach_buffer()
            MPI.Free_mem(buf)


    def testIBSendAndRecv(self):
        buf = MPI.Alloc_mem((1<<16)+MPI.BSEND_OVERHEAD)
        MPI.Attach_buffer(buf)
        try:
            size = self.COMM.Get_size()
            rank = self.COMM.Get_rank()
            for smess in messages:
                req = self.COMM.ibsend(smess, MPI.PROC_NULL)
                self.assertTrue(req)
                req.wait()
                self.assertFalse(req)
                rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
                self.assertIsNone(rmess)
            for smess in messages:
                req = self.COMM.ibsend(smess, rank, 0)
                self.assertTrue(req)
                rmess = self.COMM.recv(None, rank, 0)
                self.assertTrue(req)
                flag, _ = req.test()
                self.assertTrue(flag)
                self.assertFalse(req)
                self.assertEqual(rmess, smess)
            for smess in messages:
                dst = (rank+1)%size
                src = (rank-1)%size
                req = self.COMM.ibsend(smess, dst, 0)
                self.assertTrue(req)
                rmess = self.COMM.recv(None, src, 0)
                req.wait()
                self.assertFalse(req)
                self.assertEqual(rmess, smess)
        finally:
            MPI.Detach_buffer()
            MPI.Free_mem(buf)

    def testISSendCancel(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            req = self.COMM.issend(smess, rank, 0)
            self.assertTrue(req)
            flag, _ = req.test()
            self.assertFalse(flag)
            self.assertTrue(req)
            req.cancel()
            self.assertTrue(req)
            status = MPI.Status()
            req.get_status(status)
            if not status.Is_cancelled():
                rmess = self.COMM.recv(None, rank, 0)
                self.assertTrue(req)
                req.wait()
                self.assertFalse(req)
                self.assertEqual(rmess, smess)
            else:
                req.Free()
            self.assertFalse(req)

    def testGetStatusAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        requests = []
        for smess in messages:
            req = comm.issend(smess, rank)
            requests.append(req)
        with self.catchNotImplementedError(4, 1):
            flag = self.RequestType.get_status_all(requests)
            self.assertFalse(flag)
        comm.barrier()
        for smess in messages:
            rmess = comm.recv(None, rank)
            self.assertEqual(rmess, smess)
        with self.catchNotImplementedError(4, 1):
            flag = False
            statuses = []
            while not flag:
                flag = self.RequestType.get_status_all(requests, statuses)
            self.assertEqual(len(statuses), len(requests))
            for status in statuses:
                self.assertIsInstance(status, MPI.Status)
        if not flag:
            self.RequestType.waitall(requests)
        flag, obj = self.RequestType.testall(requests)
        self.assertTrue(flag)
        self.assertEqual(obj, [None]*len(messages))

    def testTestAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        requests = []
        for smess in messages:
            req = comm.issend(smess, rank)
            requests.append(req)
        flag, _ = self.RequestType.testall(requests)
        self.assertFalse(flag)
        flag, obj = self.RequestType.testall(requests)
        self.assertFalse(flag)
        self.assertIsNone(obj)
        comm.barrier()
        for smess in messages:
            rmess = comm.recv(None, rank)
            self.assertEqual(rmess, smess)
        flag = False
        while not flag:
            flag, obj = self.RequestType.testall(requests)
        self.assertEqual(obj, [None]*len(messages))
        flag, _ = self.RequestType.testall(requests)
        self.assertTrue(flag)

    @unittest.skipMPI('mvapich', MPI.COMM_WORLD.Get_size() > 1)
    def testWaitAll(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        #
        requests = []
        for smess in messages:
            req = comm.issend(smess, dest)
            requests.append(req)
        flag, _ = self.RequestType.testall(requests)
        self.assertFalse(flag)
        flag, obj = self.RequestType.testall(requests)
        self.assertFalse(flag)
        self.assertIsNone(obj)
        comm.barrier()
        for smess in messages:
            rmess = comm.recv(None, source)
            self.assertEqual(rmess, smess)
        obj = self.RequestType.waitall(requests)
        self.assertEqual(obj, [None]*len(messages))
        #
        requests1 = []
        for smess in messages:
            req = comm.issend(smess, dest)
            requests1.append(req)
        requests2 = []
        for _ in messages:
            req = comm.mprobe(source).irecv()
            requests2.append(req)
        statuses = [MPI.Status()]
        obj = self.RequestType.waitall(requests2, statuses)
        self.assertEqual(obj, messages)
        self.assertEqual(len(statuses), len(requests2))
        for status in statuses:
            self.assertEqual(status.source, source)
            self.assertEqual(status.tag, 0)
            self.assertGreater(status.Get_count(), 0)
        comm.barrier()
        statuses = (MPI.Status(),)
        self.RequestType.waitall(requests1, statuses)
        self.assertEqual(statuses[0].error, 0)

    def testSendrecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            rmess = self.COMM.sendrecv(smess, MPI.PROC_NULL, 0,
                                       None,  MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if isinstance(self.COMM, pkl5.Comm):
            rbuf = MPI.Alloc_mem(32)
        else:
            rbuf = None
        for smess in messages:
            dest = (rank + 1) % size
            source = (rank - 1) % size
            rmess = self.COMM.sendrecv(None, dest,  0,
                                       None, source, 0)
            self.assertIsNone(rmess)
            rmess = self.COMM.sendrecv(smess, dest,  0,
                                       None, source, 0)
            self.assertEqual(rmess, smess)
            status = MPI.Status()
            rmess = self.COMM.sendrecv(smess, dest,  42,
                                       rbuf, source, 42,
                                       status)
            self.assertEqual(status.source, source)
            self.assertEqual(status.tag, 42)
            self.assertEqual(status.error, 0)
        if rbuf is not None:
            MPI.Free_mem(rbuf)

    def testPingPong01(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.send(smess, MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if size == 1: return
        smess = None
        if rank == 0:
            self.COMM.send(smess, rank+1, 0)
            rmess = self.COMM.recv(None, rank+1, 0)
        elif rank == 1:
            rmess = self.COMM.recv(None, rank-1, 0)
            self.COMM.send(smess, rank-1, 0)
        else:
            rmess = smess
        self.assertEqual(rmess, smess)
        for smess in messages:
            if rank == 0:
                self.COMM.send(smess, rank+1, 0)
                rmess = self.COMM.recv(None, rank+1, 0)
            elif rank == 1:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.send(smess, rank-1, 0)
            else:
                rmess = smess
            self.assertEqual(rmess, smess)

    def testIrecv(self):
        if isinstance(self.COMM, pkl5.Comm):
            self.assertRaises(
                RuntimeError,
                self.COMM.irecv,
                None,
                MPI.PROC_NULL,
                0,
            )

    def testProbe(self):
        comm = self.COMM.Dup()
        try:
            status = MPI.Status()
            flag = comm.iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertFalse(flag)
            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                self.assertIsInstance(request, self.RequestType)
                self.assertTrue (bool(request != MPI.REQUEST_NULL))
                self.assertFalse(bool(request == MPI.REQUEST_NULL))
                self.assertTrue (bool(request == self.RequestType(request)))
                self.assertFalse(bool(request != self.RequestType(request)))
                self.assertTrue (bool(request != None))
                self.assertFalse(bool(request == None))
                self.assertTrue (bool(request))
                while not comm.iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status): pass
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                comm.probe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(request)
                flag, obj = request.test()
                self.assertTrue(request)
                self.assertFalse(flag)
                self.assertIsNone(obj)
                obj = comm.recv(None, comm.rank, 123)
                self.assertEqual(obj, smess)
                self.assertTrue(request)
                obj = request.wait()
                self.assertFalse(request)
                self.assertIsNone(obj)
        finally:
            comm.Free()

    def testMProbe(self):
        comm = self.COMM.Dup()
        try:
            message = comm.mprobe(MPI.PROC_NULL)
            self.assertIsInstance(message, self.MessageType)
            self.assertTrue (bool(message == MPI.MESSAGE_NO_PROC))
            self.assertFalse(bool(message != MPI.MESSAGE_NO_PROC))
            self.assertTrue (bool(message != None))
            self.assertFalse(bool(message == None))
            rmess = message.recv()
            self.assertTrue (bool(message == MPI.MESSAGE_NULL))
            self.assertFalse(bool(message != MPI.MESSAGE_NULL))
            self.assertIsNone(rmess)

            message = comm.mprobe(MPI.PROC_NULL)
            self.assertIsInstance(message, self.MessageType)
            self.assertTrue (bool(message == MPI.MESSAGE_NO_PROC))
            self.assertFalse(bool(message != MPI.MESSAGE_NO_PROC))
            request = message.irecv()
            self.assertTrue (bool(message == MPI.MESSAGE_NULL))
            self.assertFalse(bool(message != MPI.MESSAGE_NULL))
            self.assertTrue (bool(request != MPI.REQUEST_NULL))
            self.assertFalse(bool(request == MPI.REQUEST_NULL))
            rmess = request.wait()
            self.assertTrue (bool(request == MPI.REQUEST_NULL))
            self.assertFalse(bool(request != MPI.REQUEST_NULL))
            self.assertIsNone(rmess)

            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                message = comm.mprobe(comm.rank, 123)
                self.assertIsInstance(message, self.MessageType)
                self.assertTrue (bool(message == self.MessageType(message)))
                self.assertFalse(bool(message != self.MessageType(message)))
                rmess = message.recv()
                self.assertEqual(rmess, smess)
                obj = request.wait()
                self.assertFalse(request)
                self.assertIsNone(obj)
                flag, obj = request.test()
                self.assertTrue(flag)
                self.assertIsNone(obj)
                message.free()
            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                status = MPI.Status()
                message = comm.mprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(message)
                status = MPI.Status()
                rmess = message.recv(status)
                self.assertFalse(message)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertEqual(rmess, smess)
                self.assertTrue(request)
                request.wait()
            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                status = MPI.Status()
                message = comm.mprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(message)
                rreq = message.irecv()
                self.assertFalse(message)
                self.assertTrue(rreq)
                status = MPI.Status()
                rmess = rreq.wait(status)
                self.assertFalse(rreq)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertEqual(rmess, smess)
                flag, obj = rreq.test()
                self.assertTrue(flag)
                self.assertIsNone(obj)
                self.assertTrue(request)
                obj = request.wait()
                self.assertFalse(request)
                self.assertIsNone(obj)
                flag, obj = request.test()
                self.assertTrue(flag)
                self.assertIsNone(obj)
            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                message = comm.mprobe(MPI.ANY_SOURCE, MPI.ANY_TAG)
                rreq = message.irecv()
                rreq.test()
                request.free()
        finally:
            comm.Free()

    def testIMProbe(self):
        comm = self.COMM.Dup()
        try:
            status = MPI.Status()
            for smess in messages:
                message = comm.improbe(MPI.PROC_NULL)
                self.assertIsInstance(message, self.MessageType)
                self.assertEqual(message, MPI.MESSAGE_NO_PROC)
            for smess in messages:
                message = comm.improbe(comm.rank, 123)
                self.assertIsNone(message)
                request = comm.issend(smess, comm.rank, 123)
                while not comm.iprobe(comm.rank, 123): pass
                message = comm.improbe(comm.rank, 123)
                self.assertIsInstance(message, self.MessageType)
                rmess = message.recv()
                self.assertEqual(rmess, smess)
                request.wait()
            for smess in messages:
                message = comm.improbe(comm.rank, 123)
                self.assertIsNone(message)
                request = comm.issend(smess, comm.rank, 123)
                while not comm.iprobe(comm.rank, 123): pass
                message = comm.improbe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(message)
                rmess = message.recv()
                self.assertFalse(message)
                self.assertEqual(rmess, smess)
                self.assertTrue(request)
                request.wait()
                self.assertFalse(request)
        finally:
            comm.Free()

    def testMessageProbeIProbe(self):
        comm = self.COMM.Dup()
        try:
            status = MPI.Status()
            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                message = self.MessageType.probe(comm, MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(message)
                rmess = message.recv()
                self.assertFalse(message)
                self.assertEqual(rmess, smess)
                self.assertTrue(request)
                request.wait()
                self.assertFalse(request)
            for smess in messages:
                message = self.MessageType.iprobe(comm, comm.rank, 123)
                self.assertIsNone(message)
                request = comm.issend(smess, comm.rank, 123)
                while not comm.iprobe(comm.rank, 123): pass
                message = self.MessageType.iprobe(comm, MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(message)
                rmess = message.recv()
                self.assertFalse(message)
                self.assertEqual(rmess, smess)
                self.assertTrue(request)
                request.wait()
                self.assertFalse(request)
        finally:
            comm.Free()

    def testSSendAndMProbe(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        if size == 1: return
        comm = self.COMM.Dup()
        try:
            for smess in messages:
                if rank == 0:
                    comm.ssend(smess, 1)
                    message = comm.mprobe(1)
                    rmess = message.recv()
                    self.assertEqual(rmess, smess)
                if rank == 1:
                    message = comm.mprobe(0)
                    rmess = message.recv()
                    comm.ssend(rmess, 0)
                    self.assertEqual(rmess, smess)
        finally:
            comm.Free()

    def testRequest(self):
        req = self.RequestType()
        self.assertFalse(req)
        self.assertEqual(req, self.RequestType())
        req = self.RequestType(MPI.REQUEST_NULL)
        self.assertFalse(req)
        self.assertEqual(req, MPI.REQUEST_NULL)
        self.assertEqual(req, self.RequestType())

    def testMessage(self):
        msg = self.MessageType()
        self.assertFalse(msg)
        self.assertEqual(msg, self.MessageType())
        msg = self.MessageType(MPI.MESSAGE_NULL)
        self.assertFalse(msg)
        self.assertEqual(msg, self.MessageType())
        msg = self.MessageType(MPI.MESSAGE_NO_PROC)
        self.assertTrue(msg)
        self.assertEqual(msg, MPI.MESSAGE_NO_PROC)
        self.assertEqual(msg, self.MessageType(MPI.MESSAGE_NO_PROC))
        self.assertNotEqual(msg, MPI.MESSAGE_NULL)

    @staticmethod
    def make_intercomm(basecomm):
        if unittest.is_mpi('msmpi') and MPI.COMM_WORLD.Get_size() >= 3:
            raise unittest.SkipTest("msmpi")
        size = basecomm.Get_size()
        rank = basecomm.Get_rank()
        if size == 1:
            raise unittest.SkipTest("comm.size==1")
        if rank < size // 2 :
            COLOR = 0
            local_leader = 0
            remote_leader = size // 2
        else:
            COLOR = 1
            local_leader = 0
            remote_leader = 0
        basecomm.Barrier()
        intracomm = basecomm.Split(COLOR, key=0)
        intercomm = MPI.Intracomm.Create_intercomm(
            intracomm,
            local_leader,
            basecomm,
            remote_leader
        )
        intracomm.Free()
        if isinstance(basecomm, pkl5.Intracomm):
            intercomm = pkl5.Intercomm(intercomm)
        return intercomm, COLOR

    def testBcastIntra(self, msglist=None, check=None):
        comm = self.COMM
        size = comm.Get_size()
        for smess in (msglist or messages):
            for root in range(size):
                rmess = comm.bcast(smess, root)
                if msglist and check:
                    self.assertTrue(check(rmess))
                else:
                    self.assertEqual(rmess, smess)

    def testBcastInter(self, msglist=None, check=None):
        comm, COLOR = self.make_intercomm(self.COMM)
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for smess in (msglist or messages)[:1]:
            comm.barrier()
            for color in [0, 1]:
                if COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = comm.bcast(smess, root=MPI.ROOT)
                        else:
                            rmess = comm.bcast(None, root=MPI.PROC_NULL)
                        self.assertIsNone(rmess)
                else:
                    for root in range(rsize):
                        rmess = comm.bcast(None, root=root)
                        if msglist and check:
                            self.assertTrue(check(rmess))
                        else:
                            self.assertEqual(rmess, smess)
        if isinstance(comm, pkl5.Comm):
            bcast = comm.bcast
            rsize = comm.Get_remote_size()
            self.assertRaises(MPI.Exception, bcast, None, root=rsize)
        comm.Free()

    def testGatherIntra(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for smess in messages:
            for root in range(size):
                rmess = comm.gather(smess, root)
                if rank == root:
                    self.assertEqual(rmess, [smess]*size)
                else:
                    self.assertIsNone(rmess)
        self.assertRaises(MPI.Exception, comm.gather, None, root=-1)
        self.assertRaises(MPI.Exception, comm.gather, None, root=size)

    def testGatherInter(self):
        comm, COLOR = self.make_intercomm(self.COMM)
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for smess in messages:
            for color in [0, 1]:
                if color == COLOR:
                    for root in range(size):
                        if root == rank:
                            rmess = comm.gather(smess, root=MPI.ROOT)
                            self.assertEqual(rmess, [smess] * rsize)
                        else:
                            rmess = comm.gather(None, root=MPI.PROC_NULL)
                            self.assertIsNone(rmess)
                else:
                    for root in range(rsize):
                        rmess = comm.gather(smess, root=root)
                        self.assertIsNone(rmess)
        self.assertRaises(MPI.Exception, comm.gather, None, root=max(size,rsize))
        self.assertRaises(MPI.Exception, comm.gather, None, root=max(size,rsize))
        comm.Free()

    def testScatterIntra(self):
        comm = self.COMM
        size = comm.Get_size()
        for smess in messages:
            for root in range(size):
                rmess = comm.scatter(None, root)
                self.assertIsNone(rmess)
                rmess = comm.scatter([smess]*size, root)
                self.assertEqual(rmess, smess)
                rmess = comm.scatter(iter([smess]*size), root)
                self.assertEqual(rmess, smess)
        self.assertRaises(MPI.Exception, comm.scatter, [None]*size, root=-1)
        self.assertRaises(MPI.Exception, comm.scatter, [None]*size, root=size)
        if size == 1:
            self.assertRaises(ValueError, comm.scatter, [None]*(size-1), root=0)
            self.assertRaises(ValueError, comm.scatter, [None]*(size+1), root=0)

    def testScatterInter(self):
        comm, COLOR = self.make_intercomm(self.COMM)
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                if color == COLOR:
                    for root in range(size):
                        if root == rank:
                            rmess = comm.scatter([smess] * rsize, root=MPI.ROOT)
                        else:
                            rmess = comm.scatter(None, root=MPI.PROC_NULL)
                        self.assertIsNone(rmess)
                else:
                    for root in range(rsize):
                        rmess = comm.scatter(None, root=root)
                        self.assertEqual(rmess, smess)
        self.assertRaises(MPI.Exception, comm.scatter, None, root=max(size, rsize))
        self.assertRaises(MPI.Exception, comm.scatter, None, root=max(size, rsize))
        comm.Free()

    def testAllgatherIntra(self):
        comm = self.COMM
        size = comm.Get_size()
        for smess in messages:
            rmess = comm.allgather(None)
            self.assertEqual(rmess, [None]*size)
            rmess = comm.allgather(smess)
            self.assertEqual(rmess, [smess]*size)

    def testAllgatherInter(self):
        comm, COLOR = self.make_intercomm(self.COMM)
        size = comm.Get_remote_size()
        for smess in messages:
            rmess = comm.allgather(None)
            self.assertEqual(rmess, [None]*size)
            rmess = comm.allgather(smess)
            self.assertEqual(rmess, [smess]*size)
        comm.Free()

    def testAlltoallIntra(self):
        comm = self.COMM
        size = comm.Get_size()
        for smess in messages:
            rmess = comm.alltoall(None)
            self.assertEqual(rmess, [None]*size)
            rmess = comm.alltoall([smess]*size)
            self.assertEqual(rmess, [smess]*size)
            rmess = comm.alltoall(iter([smess]*size))
            self.assertEqual(rmess, [smess]*size)
        self.assertRaises(ValueError, comm.alltoall, [None]*(size-1))
        self.assertRaises(ValueError, comm.alltoall, [None]*(size+1))

    def testAlltoallInter(self):
        comm, COLOR = self.make_intercomm(self.COMM)
        size = comm.Get_remote_size()
        for smess in messages:
            rmess = comm.alltoall(None)
            self.assertEqual(rmess, [None]*size)
            rmess = comm.alltoall([smess]*size)
            self.assertEqual(rmess, [smess]*size)
            rmess = comm.alltoall(iter([smess]*size))
            self.assertEqual(rmess, [smess]*size)
        self.assertRaises(ValueError, comm.alltoall, [None]*(size-1))
        self.assertRaises(ValueError, comm.alltoall, [None]*(size+1))
        comm.Free()

    @unittest.skipIf(numpy is None, 'numpy')
    def testBigMPI(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        bigmpi = self.bigmpi
        blocksizes = (
            63, 64, 65,
            (1<<12)-1,
            (1<<12),
            (1<<12)+1,
        )
        for blocksize in blocksizes:
            bigmpi.blocksize = blocksize
            a = numpy.empty(1024, dtype='i')
            b = numpy.empty(1024, dtype='i')
            c = numpy.empty(1024, dtype='i')
            a.fill(rank)
            b.fill(dest)
            c.fill(42)
            status = MPI.Status()
            smess = (a, b)
            rmess = comm.sendrecv(
                smess, dest,  42,
                None, source, 42,
                status,
            )
            self.assertTrue(numpy.all(rmess[0] == source))
            self.assertTrue(numpy.all(rmess[1] == rank))
            self.assertGreater(status.Get_elements(MPI.BYTE), 0)
            comm.barrier()
            status = MPI.Status()
            smess = (a, b)
            request = comm.issend(smess, dest, 123)
            rmess = comm.mprobe(source, 123).irecv().wait(status)
            self.assertTrue(numpy.all(rmess[0] == source))
            self.assertTrue(numpy.all(rmess[1] == rank))
            self.assertGreater(status.Get_elements(MPI.BYTE), 0)
            request.Free()
            comm.barrier()
            check = lambda x: numpy.all(x == 42)
            self.testBcastIntra([c, c], check)
            self.testBcastInter([c, c], check)
            check2 = lambda x: check(x[0]) and check(x[1])
            self.testBcastIntra([(c, c.copy())], check2)
            self.testBcastInter([(c, c.copy())], check2)


class BaseTestPKL5:
    CommType = pkl5.Intracomm
    MessageType = pkl5.Message
    RequestType = pkl5.Request

    def setUp(self):
        super().setUp()
        self.pickle_prev = pkl5.pickle
        self.pickle = pkl5.Pickle()
        self.pickle.THRESHOLD = 0
        pkl5.pickle = self.pickle

    def tearDown(self):
        super().tearDown()
        pkl5.pickle = self.pickle_prev

    @unittest.skipIf(numpy is None, 'numpy')
    def testPickle5(self):
        comm = self.COMM
        rank = comm.Get_rank()
        pickle = self.pickle
        protocols = list(range(-2, pickle.PROTOCOL+1))
        for protocol in [None] + protocols:
            pickle.PROTOCOL = protocol
            for threshold in (-1, 0, 64, 256, None):
                pickle.THRESHOLD = threshold
                threshold = pickle.THRESHOLD
                for slen in (0, 32, 64, 128, 256, 512):
                    sobj = numpy.empty(slen, dtype='i')
                    sobj.fill(rank)
                    #
                    robj = comm.sendrecv(
                        sobj, rank, 42,
                        None, rank, 42)
                    self.assertTrue(numpy.all(sobj==robj))
                    #
                    data, bufs = pickle.dumps_oob(sobj)
                    self.assertIs(type(data), bytes)
                    self.assertIs(type(bufs), list)
                    robj = pickle.loads_oob(data, bufs)
                    self.assertTrue(numpy.all(sobj==robj))
                    have_pickle5 = (
                        sys.version_info >= (3, 8) or
                        'pickle5' in sys.modules
                    )
                    if sobj.nbytes >= threshold and have_pickle5:
                        self.assertEqual(len(bufs), 1)
                        self.assertIs(type(bufs[0]), MPI.buffer)
                    else:
                        self.assertEqual(len(bufs), 0)


class TestMPISelf(BaseTest, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestMPIWorld(BaseTest, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestPKL5Self(BaseTestPKL5, TestMPISelf):
    pass

class TestPKL5World(BaseTestPKL5, TestMPIWorld):
    pass


if __name__ == '__main__':
    unittest.main()
