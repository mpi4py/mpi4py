from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl


class BaseTestP2PBuf(object):

    COMM = MPI.COMM_NULL

    def testSendrecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for s in range(0, size):
                    sbuf = array( s, typecode, s)
                    rbuf = array(-1, typecode, s+1)
                    self.COMM.Sendrecv(sbuf.as_mpi(), dest,   0,
                                       rbuf.as_mpi(), source, 0)
                    for value in rbuf[:-1]:
                        self.assertEqual(value, s)
                    self.assertEqual(rbuf[-1], -1)

    def testSendrecvReplace(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for s in range(0, size):
                    buf = array(rank, typecode, s);
                    self.COMM.Sendrecv_replace(buf.as_mpi(), dest, 0, source, 0)
                    for value in buf:
                        self.assertEqual(value, source)

    def testSendRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for s in range(0, size):
                    #
                    sbuf = array( s, typecode, s)
                    rbuf = array(-1, typecode, s)
                    mem  = array( 0, typecode, 2*(s+MPI.BSEND_OVERHEAD)).as_raw()
                    if size == 1:
                        MPI.Attach_buffer(mem)
                        rbuf = sbuf
                        MPI.Detach_buffer()
                    elif rank == 0:
                        MPI.Attach_buffer(mem)
                        self.COMM.Ibsend(sbuf.as_mpi(), 1, 0).Wait()
                        self.COMM.Bsend(sbuf.as_mpi(), 1, 0)
                        MPI.Detach_buffer()
                        self.COMM.Send(sbuf.as_mpi(), 1, 0)
                        self.COMM.Ssend(sbuf.as_mpi(), 1, 0)
                        self.COMM.Recv(rbuf.as_mpi(),  1, 0)
                        self.COMM.Recv(rbuf.as_mpi(),  1, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 1, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 1, 0)
                    elif rank == 1:
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        MPI.Attach_buffer(mem)
                        self.COMM.Ibsend(sbuf.as_mpi(), 0, 0).Wait()
                        self.COMM.Bsend(sbuf.as_mpi(), 0, 0)
                        MPI.Detach_buffer()
                        self.COMM.Send(sbuf.as_mpi(), 0, 0)
                        self.COMM.Ssend(sbuf.as_mpi(), 0, 0)
                    else:
                        rbuf = sbuf
                    for value in rbuf:
                        self.assertEqual(value, s)
                    #
                    rank = self.COMM.Get_rank()
                    sbuf = array( s, typecode, s)
                    rbuf = array(-1, typecode, s)
                    rreq = self.COMM.Irecv(rbuf.as_mpi(), rank, 0)
                    self.COMM.Rsend(sbuf.as_mpi(), rank, 0)
                    rreq.Wait()
                    for value in rbuf:
                        self.assertEqual(value, s)
                    rbuf = array(-1, typecode, s)
                    rreq = self.COMM.Irecv(rbuf.as_mpi(), rank, 0)
                    self.COMM.Irsend(sbuf.as_mpi(), rank, 0).Wait()
                    rreq.Wait()
                    for value in rbuf:
                        self.assertEqual(value, s)

    def testProcNull(self):
        comm = self.COMM
        #
        comm.Sendrecv(None, MPI.PROC_NULL, 0,
                      None, MPI.PROC_NULL, 0)
        comm.Sendrecv_replace(None,
                              MPI.PROC_NULL, 0,
                              MPI.PROC_NULL, 0)
        #
        comm.Send (None, MPI.PROC_NULL)
        comm.Isend (None, MPI.PROC_NULL).Wait()
        req = comm.Send_init(None, MPI.PROC_NULL)
        req.Start(); req.Wait(); req.Free()
        #
        comm.Ssend(None, MPI.PROC_NULL)
        comm.Issend(None, MPI.PROC_NULL).Wait()
        req = comm.Ssend_init(None, MPI.PROC_NULL)
        req.Start(); req.Wait(); req.Free()
        #
        buf = MPI.Alloc_mem(MPI.BSEND_OVERHEAD)
        MPI.Attach_buffer(buf)
        comm.Bsend(None, MPI.PROC_NULL)
        comm.Ibsend(None, MPI.PROC_NULL).Wait()
        req = comm.Bsend_init(None, MPI.PROC_NULL)
        req.Start(); req.Wait(); req.Free()
        MPI.Detach_buffer()
        MPI.Free_mem(buf)
        #
        comm.Rsend(None, MPI.PROC_NULL)
        comm.Irsend(None, MPI.PROC_NULL).Wait()
        req = comm.Rsend_init(None, MPI.PROC_NULL)
        req.Start(); req.Wait(); req.Free()
        #
        comm.Recv (None, MPI.PROC_NULL)
        comm.Irecv(None, MPI.PROC_NULL).Wait()
        req = comm.Recv_init(None, MPI.PROC_NULL)
        req.Start(); req.Wait(); req.Free()

    def testPersistent(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for s in range(size):
                    for xs in range(3):
                        #
                        sbuf = array( s, typecode, s)
                        rbuf = array(-1, typecode, s+xs)
                        sendreq = self.COMM.Send_init(sbuf.as_mpi(), dest, 0)
                        recvreq = self.COMM.Recv_init(rbuf.as_mpi(), source, 0)
                        sendreq.Start()
                        recvreq.Start()
                        sendreq.Wait()
                        recvreq.Wait()
                        self.assertNotEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertNotEqual(recvreq, MPI.REQUEST_NULL)
                        sendreq.Free()
                        recvreq.Free()
                        self.assertEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertEqual(recvreq, MPI.REQUEST_NULL)
                        for value in rbuf[:s]:
                            self.assertEqual(value, s)
                        for value in rbuf[s:]:
                            self.assertEqual(value, -1)
                        #
                        sbuf = array(s,  typecode, s)
                        rbuf = array(-1, typecode, s+xs)
                        sendreq = self.COMM.Send_init(sbuf.as_mpi(), dest, 0)
                        recvreq = self.COMM.Recv_init(rbuf.as_mpi(), source, 0)
                        reqlist = [sendreq, recvreq]
                        MPI.Prequest.Startall(reqlist)
                        index1 = MPI.Prequest.Waitany(reqlist)
                        self.assertTrue(index1 in [0, 1])
                        self.assertNotEqual(reqlist[index1], MPI.REQUEST_NULL)
                        index2 = MPI.Prequest.Waitany(reqlist)
                        self.assertTrue(index2 in [0, 1])
                        self.assertNotEqual(reqlist[index2], MPI.REQUEST_NULL)
                        self.assertTrue(index1 != index2)
                        index3 = MPI.Prequest.Waitany(reqlist)
                        self.assertEqual(index3, MPI.UNDEFINED)
                        for preq in reqlist:
                            self.assertNotEqual(preq, MPI.REQUEST_NULL)
                            preq.Free()
                            self.assertEqual(preq, MPI.REQUEST_NULL)
                        for value in rbuf[:s]:
                            self.assertEqual(value, s)
                        for value in rbuf[s:]:
                            self.assertEqual(value, -1)
                        #
                        sbuf = array( s, typecode, s)
                        rbuf = array(-1, typecode, s+xs)
                        sendreq = self.COMM.Ssend_init(sbuf.as_mpi(), dest, 0)
                        recvreq = self.COMM.Recv_init(rbuf.as_mpi(), source, 0)
                        sendreq.Start()
                        recvreq.Start()
                        sendreq.Wait()
                        recvreq.Wait()
                        self.assertNotEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertNotEqual(recvreq, MPI.REQUEST_NULL)
                        sendreq.Free()
                        recvreq.Free()
                        self.assertEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertEqual(recvreq, MPI.REQUEST_NULL)
                        for value in rbuf[:s]:
                            self.assertEqual(value, s)
                        for value in rbuf[s:]:
                            self.assertEqual(value, -1)
                        #
                        mem = array( 0, typecode, s+MPI.BSEND_OVERHEAD).as_raw()
                        sbuf = array( s, typecode, s)
                        rbuf = array(-1, typecode, s+xs)
                        MPI.Attach_buffer(mem)
                        sendreq = self.COMM.Bsend_init(sbuf.as_mpi(), dest, 0)
                        recvreq = self.COMM.Recv_init(rbuf.as_mpi(), source, 0)
                        sendreq.Start()
                        recvreq.Start()
                        sendreq.Wait()
                        recvreq.Wait()
                        MPI.Detach_buffer()
                        self.assertNotEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertNotEqual(recvreq, MPI.REQUEST_NULL)
                        sendreq.Free()
                        recvreq.Free()
                        self.assertEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertEqual(recvreq, MPI.REQUEST_NULL)
                        for value in rbuf[:s]:
                            self.assertEqual(value, s)
                        for value in rbuf[s:]:
                            self.assertEqual(value, -1)
                        #
                        rank = self.COMM.Get_rank()
                        sbuf = array( s, typecode, s)
                        rbuf = array(-1, typecode, s+xs)
                        recvreq = self.COMM.Recv_init (rbuf.as_mpi(), rank, 0)
                        sendreq = self.COMM.Rsend_init(sbuf.as_mpi(), rank, 0)
                        recvreq.Start()
                        sendreq.Start()
                        recvreq.Wait()
                        sendreq.Wait()
                        self.assertNotEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertNotEqual(recvreq, MPI.REQUEST_NULL)
                        sendreq.Free()
                        recvreq.Free()
                        self.assertEqual(sendreq, MPI.REQUEST_NULL)
                        self.assertEqual(recvreq, MPI.REQUEST_NULL)
                        for value in rbuf[:s]:
                            self.assertEqual(value, s)
                        for value in rbuf[s:]:
                            self.assertEqual(value, -1)

    def testProbe(self):
        comm = self.COMM.Dup()
        try:
            request = comm.Issend([None, 0, MPI.BYTE], comm.rank, 123)
            self.assertTrue(request)
            status = MPI.Status()
            comm.Probe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertEqual(status.source, comm.rank)
            self.assertEqual(status.tag, 123)
            self.assertTrue(request)
            flag = request.Test()
            self.assertTrue(request)
            self.assertFalse(flag)
            comm.Recv([None, 0, MPI.BYTE], comm.rank, 123)
            self.assertTrue(request)
            flag = request.Test()
            self.assertFalse(request)
            self.assertTrue(flag)
        finally:
            comm.Free()

    @unittest.skipMPI('MPICH1')
    @unittest.skipMPI('LAM/MPI')
    def testProbeCancel(self):
        comm = self.COMM.Dup()
        try:
            request = comm.Issend([None, 0, MPI.BYTE], comm.rank, 123)
            status = MPI.Status()
            comm.Probe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertEqual(status.source, comm.rank)
            self.assertEqual(status.tag, 123)
            request.Cancel()
            self.assertTrue(request)
            status = MPI.Status()
            request.Get_status(status)
            cancelled = status.Is_cancelled()
            if not cancelled:
                comm.Recv([None, 0, MPI.BYTE], comm.rank, 123)
                request.Wait()
            else:
                request.Free()
        finally:
            comm.Free()

    def testIProbe(self):
        comm = self.COMM.Dup()
        try:
            f = comm.Iprobe()
            self.assertFalse(f)
            f = comm.Iprobe(MPI.ANY_SOURCE)
            self.assertFalse(f)
            f = comm.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG)
            self.assertFalse(f)
            status = MPI.Status()
            f = comm.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertFalse(f)
            self.assertEqual(status.source, MPI.ANY_SOURCE)
            self.assertEqual(status.tag,    MPI.ANY_TAG)
            self.assertEqual(status.error,  MPI.SUCCESS)
        finally:
            comm.Free()


class TestP2PBufSelf(BaseTestP2PBuf, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PBufWorld(BaseTestP2PBuf, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestP2PBufSelfDup(TestP2PBufSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

@unittest.skipMPI('openmpi(<1.4.0)', MPI.Query_thread() > MPI.THREAD_SINGLE)
class TestP2PBufWorldDup(TestP2PBufWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    unittest.main()
