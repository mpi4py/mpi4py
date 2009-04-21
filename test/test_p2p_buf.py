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

    def testSendRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for s in range(0, size):
                    sbuf = array( s, typecode, s)
                    rbuf = array(-1, typecode, s)
                    mem  = array( 0, typecode, s+MPI.BSEND_OVERHEAD)
                    if size == 1:
                        MPI.Attach_buffer(mem)
                        rbuf = sbuf
                        MPI.Detach_buffer()
                    elif rank == 0:
                        MPI.Attach_buffer(mem)
                        self.COMM.Bsend(sbuf.as_mpi(), 1, 0)
                        MPI.Detach_buffer()
                        self.COMM.Send(sbuf.as_mpi(), 1, 0)
                        self.COMM.Ssend(sbuf.as_mpi(), 1, 0)
                        self.COMM.Recv(rbuf.as_mpi(),  1, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 1, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 1, 0)
                    elif rank == 1:
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        self.COMM.Recv(rbuf.as_mpi(), 0, 0)
                        MPI.Attach_buffer(mem)
                        self.COMM.Bsend(sbuf.as_mpi(), 0, 0)
                        MPI.Detach_buffer()
                        self.COMM.Send(sbuf.as_mpi(), 0, 0)
                        self.COMM.Ssend(sbuf.as_mpi(), 0, 0)
                    else:
                        rbuf = sbuf

                    for value in rbuf:
                        self.assertEqual(value, s)


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

class TestP2PBufSelfDup(BaseTestP2PBuf, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestP2PBufWorldDup(BaseTestP2PBuf, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()

name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestP2PBufWorldDup

if __name__ == '__main__':
    unittest.main()
