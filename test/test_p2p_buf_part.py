from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl


class BaseTestP2PBufPart:

    COMM = MPI.COMM_NULL

    def testSelf(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                for s in range(0, size):
                    for p in range(1, 4):
                        with self.subTest(p=p, s=s):
                            sbuf = array( s, typecode, s*p)
                            rbuf = array(-1, typecode, s*p)
                            sreq = self.COMM.Psend_init(sbuf.as_mpi(), p, rank, 0)
                            rreq = self.COMM.Precv_init(rbuf.as_mpi(), p, rank, 0)
                            for _ in range(3):
                                rreq.Start()
                                for i in range(p):
                                    flag = rreq.Parrived(i)
                                    self.assertFalse(flag)
                                sreq.Start()
                                for i in range(p):
                                    sreq.Pready(i)
                                    for j in range(i+1, p):
                                        flag = rreq.Parrived(j)
                                        self.assertFalse(flag)
                                for i in range(p):
                                    while not rreq.Parrived(i): pass
                                    flag = rreq.Parrived(i)
                                    self.assertTrue(flag)
                                rreq.Wait()
                                sreq.Wait()
                                self.assertNotEqual(sreq, MPI.REQUEST_NULL)
                                self.assertNotEqual(rreq, MPI.REQUEST_NULL)
                                check = arrayimpl.scalar(s)
                                for value in rbuf:
                                    self.assertEqual(value, check)
                            rreq.Free()
                            sreq.Free()
                            self.assertEqual(sreq, MPI.REQUEST_NULL)
                            self.assertEqual(rreq, MPI.REQUEST_NULL)

    def testRing(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        dest = (rank + 1) % size
        source = (rank - 1) % size
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                for s in range(0, size):
                    for p in range(1, 4):
                        with self.subTest(p=p, s=s):
                            sbuf = array( s, typecode, s*p)
                            rbuf = array(-1, typecode, s*p)
                            sreq = self.COMM.Psend_init(sbuf.as_mpi(), p, dest, 0)
                            rreq = self.COMM.Precv_init(rbuf.as_mpi(), p, source, 0)
                            for _ in range(3):
                                self.COMM.Barrier()
                                rreq.Start()
                                for i in range(p):
                                    flag = rreq.Parrived(i)
                                    self.assertFalse(flag)
                                self.COMM.Barrier()
                                sreq.Start()
                                for i in range(p):
                                    sreq.Pready(i)
                                self.COMM.Barrier()
                                for i in range(p):
                                    while not rreq.Parrived(i): pass
                                    flag = rreq.Parrived(i)
                                    self.assertTrue(flag)
                                rreq.Wait()
                                sreq.Wait()
                                self.assertNotEqual(sreq, MPI.REQUEST_NULL)
                                self.assertNotEqual(rreq, MPI.REQUEST_NULL)
                                self.COMM.Barrier()
                                check = arrayimpl.scalar(s)
                                for value in rbuf:
                                    self.assertEqual(value, check)
                            rreq.Free()
                            sreq.Free()
                            self.assertEqual(sreq, MPI.REQUEST_NULL)
                            self.assertEqual(rreq, MPI.REQUEST_NULL)


class TestP2PBufPartSelf(BaseTestP2PBufPart, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PBufPartWorld(BaseTestP2PBufPart, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestP2PBufPartSelfDup(TestP2PBufPartSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestP2PBufPartWorldDup(TestP2PBufPartWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


def have_feature():
    info = MPI.Get_library_version()
    if 'MPICH' in info and 'ch3:' in info:
        raise NotImplementedError
    sreq = MPI.COMM_SELF.Psend_init(bytearray(1), 1, 0, 0)
    rreq = MPI.COMM_SELF.Precv_init(bytearray(1), 1, 0, 0)
    sreq.Start(); rreq.Start();
    sreq.Pready(0); rreq.Parrived(0);
    rreq.Wait(); rreq.Free(); del rreq;
    sreq.Wait(); sreq.Free(); del sreq;
try:
    have_feature()
except NotImplementedError:
    unittest.disable(BaseTestP2PBufPart, 'mpi-p2p-part')

if __name__ == '__main__':
    unittest.main()
