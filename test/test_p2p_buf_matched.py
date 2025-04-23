import arrayimpl
import mpiunittest as unittest

from mpi4py import MPI


@unittest.skipIf(MPI.MESSAGE_NULL == MPI.MESSAGE_NO_PROC, "mpi-message")
class TestMessage(unittest.TestCase):
    #
    def testMessageNull(self):
        null = MPI.MESSAGE_NULL
        self.assertFalse(null)
        null2 = MPI.Message()
        self.assertEqual(null, null2)
        null3 = MPI.Message(null)
        self.assertEqual(null, null3)

    def testMessageNoProc(self):
        #
        noproc = MPI.MESSAGE_NO_PROC
        self.assertTrue(noproc)
        noproc.Recv(None)
        self.assertTrue(noproc)
        noproc.Irecv(None).Wait()
        self.assertTrue(noproc)
        #
        noproc2 = MPI.Message(MPI.MESSAGE_NO_PROC)
        self.assertTrue(noproc2)
        self.assertEqual(noproc2, noproc)
        self.assertNotEqual(noproc, MPI.MESSAGE_NULL)
        #
        message = MPI.Message(MPI.MESSAGE_NO_PROC)
        message.Recv(None)
        self.assertEqual(message, MPI.MESSAGE_NULL)
        #
        message = MPI.Message(MPI.MESSAGE_NO_PROC)
        request = message.Irecv(None)
        self.assertEqual(message, MPI.MESSAGE_NULL)
        self.assertNotEqual(request, MPI.REQUEST_NULL)
        request.Wait()
        self.assertEqual(request, MPI.REQUEST_NULL)

    def testPickle(self):
        from pickle import dumps, loads

        for message in (
            MPI.MESSAGE_NULL,
            MPI.MESSAGE_NO_PROC,
        ):
            msg = loads(dumps(message))
            self.assertIs(msg, message)
            msg = loads(dumps(MPI.Message(message)))
            self.assertIsNot(msg, message)
            self.assertEqual(msg, message)
        comm = MPI.COMM_SELF
        request = comm.Isend(b"", 0, 0)
        with self.assertRaises(ValueError):
            loads(dumps(request))
        message = comm.Mprobe(0, 0)
        with self.assertRaises(ValueError):
            loads(dumps(message))
        message.Recv(bytearray(1))
        request.Wait()


@unittest.skipIf(MPI.MESSAGE_NULL == MPI.MESSAGE_NO_PROC, "mpi-message")
class BaseTestP2PMatched:
    #
    COMM = MPI.COMM_NULL

    def testIMProbe(self):
        comm = self.COMM.Dup()
        try:
            m = comm.Improbe()
            self.assertIsNone(m)
            m = comm.Improbe(MPI.ANY_SOURCE)
            self.assertIsNone(m)
            m = comm.Improbe(MPI.ANY_SOURCE, MPI.ANY_TAG)
            self.assertIsNone(m)
            status = MPI.Status()
            m = comm.Improbe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertIsNone(m)
            self.assertEqual(status.source, MPI.ANY_SOURCE)
            self.assertEqual(status.tag, MPI.ANY_TAG)
            self.assertEqual(status.error, MPI.SUCCESS)
            m = MPI.Message.Iprobe(comm)
            self.assertIsNone(m)
            buf = [None, 0, MPI.BYTE]
            s = comm.Isend(buf, comm.rank, 0)
            r = comm.Mprobe(comm.rank, 0).Irecv(buf)
            MPI.Request.Waitall([s, r])
        finally:
            comm.Free()

    def testProbeRecv(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                for s in range(size + 1):
                    with self.subTest(s=s):
                        sbuf = array(s, typecode, s)
                        rbuf = array(-1, typecode, s)
                        if size == 1:
                            n = comm.Improbe(0, 0)
                            self.assertIsNone(n)
                            sr = comm.Isend(sbuf.as_mpi(), 0, 0)
                            m = comm.Mprobe(0, 0)
                            self.assertIsInstance(m, MPI.Message)
                            self.assertTrue(m)
                            rr = m.Irecv(rbuf.as_raw())
                            self.assertFalse(m)
                            self.assertTrue(sr)
                            self.assertTrue(rr)
                            MPI.Request.Waitall([sr, rr])
                            self.assertFalse(sr)
                            self.assertFalse(rr)
                            #
                            n = comm.Improbe(0, 0)
                            self.assertIsNone(n)
                            r = comm.Isend(sbuf.as_mpi(), 0, 0)
                            m = MPI.Message.Probe(comm, 0, 0)
                            self.assertIsInstance(m, MPI.Message)
                            self.assertTrue(m)
                            m.Recv(rbuf.as_raw())
                            self.assertFalse(m)
                            r.Wait()
                            #
                            n = MPI.Message.Iprobe(comm, 0, 0)
                            self.assertIsNone(n)
                            r = comm.Isend(sbuf.as_mpi(), 0, 0)
                            comm.Probe(0, 0)
                            m = MPI.Message.Iprobe(comm, 0, 0)
                            self.assertIsInstance(m, MPI.Message)
                            self.assertTrue(m)
                            m.Recv(rbuf.as_raw())
                            self.assertFalse(m)
                            r.Wait()
                            #
                            n = MPI.Message.Iprobe(comm, 0, 0)
                            self.assertIsNone(n)
                            r = comm.Isend(sbuf.as_mpi(), 0, 0)
                            m = comm.Mprobe(0, 0)
                            self.assertIsInstance(m, MPI.Message)
                            self.assertTrue(m)
                            m.Recv(rbuf.as_raw())
                            self.assertFalse(m)
                            r.Wait()
                        elif rank == 0:
                            n = comm.Improbe(0, 0)
                            self.assertIsNone(n)
                            #
                            comm.Send(sbuf.as_mpi(), 1, 0)
                            m = comm.Mprobe(1, 0)
                            self.assertTrue(m)
                            m.Recv(rbuf.as_raw())
                            self.assertFalse(m)
                            #
                            n = comm.Improbe(0, 0)
                            self.assertIsNone(n)
                            comm.Send(sbuf.as_mpi(), 1, 1)
                            m = None
                            while not m:
                                m = comm.Improbe(1, 1)
                            m.Irecv(rbuf.as_raw()).Wait()
                        elif rank == 1:
                            n = comm.Improbe(1, 0)
                            self.assertIsNone(n)
                            #
                            m = comm.Mprobe(0, 0)
                            self.assertTrue(m)
                            m.Recv(rbuf.as_raw())
                            self.assertFalse(m)
                            #
                            n = comm.Improbe(1, 0)
                            self.assertIsNone(n)
                            comm.Send(sbuf.as_mpi(), 0, 0)
                            m = None
                            while not m:
                                m = comm.Improbe(0, 1)
                            m.Irecv(rbuf.as_mpi()).Wait()
                            comm.Send(sbuf.as_mpi(), 0, 1)
                        else:
                            rbuf = sbuf
                        check = arrayimpl.scalar(s)
                        for value in rbuf:
                            self.assertEqual(value, check)


class TestP2PMatchedSelf(BaseTestP2PMatched, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestP2PMatchedWorld(BaseTestP2PMatched, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestP2PMatchedSelfDup(TestP2PMatchedSelf):
    #
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()

    def tearDown(self):
        self.COMM.Free()


class TestP2PMatchedWorldDup(TestP2PMatchedWorld):
    #
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()

    def tearDown(self):
        self.COMM.Free()


if __name__ == "__main__":
    unittest.main()
