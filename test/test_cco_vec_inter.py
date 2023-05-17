from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

@unittest.skipMPI('openmpi(<1.6.0)')
@unittest.skipMPI('MPICH1')
@unittest.skipIf(MPI.ROOT == MPI.PROC_NULL, 'mpi-root')
@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
class BaseTestCCOVecInter:

    BASECOMM  = MPI.COMM_NULL
    INTRACOMM = MPI.COMM_NULL
    INTERCOMM = MPI.COMM_NULL

    def setUp(self):
        size = self.BASECOMM.Get_size()
        rank = self.BASECOMM.Get_rank()
        if rank < size // 2:
            self.COLOR = 0
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = size // 2
        else:
            self.COLOR = 1
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = 0
        self.INTRACOMM = self.BASECOMM.Split(self.COLOR, key=0)
        Create_intercomm = MPI.Intracomm.Create_intercomm
        self.INTERCOMM = Create_intercomm(
            self.INTRACOMM,
            self.LOCAL_LEADER,
            self.BASECOMM,
            self.REMOTE_LEADER,
        )

    def tearDown(self):
        self.INTRACOMM.Free()
        self.INTERCOMM.Free()

    def testGatherv(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rbuf = array(-1, typecode, (rsize, root+color))
                            comm.Gatherv(None, rbuf.as_mpi(), root=MPI.ROOT)
                            check = arrayimpl.scalar(root)
                            for value in rbuf.flat:
                                self.assertEqual(value, check)
                        else:
                            comm.Gatherv(None, None, root=MPI.PROC_NULL)
                else:
                    for root in range(rsize):
                        sbuf = array(root, typecode, root+color)
                        comm.Gatherv(sbuf.as_mpi(), None, root=root)

    def testScatterv(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            sbuf = array(root, typecode, (rsize, root+color))
                            comm.Scatterv(sbuf.as_mpi(), None, root=MPI.ROOT)
                        else:
                            comm.Scatterv(None, None, root=MPI.PROC_NULL)
                else:
                    for root in range(rsize):
                        rbuf = array(root, typecode, root+color)
                        comm.Scatterv(None, rbuf.as_mpi(), root=root)
                        check = arrayimpl.scalar(root)
                        for value in rbuf:
                            self.assertEqual(value, check)

    def testAllgatherv(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for n in range(size):
                        sbuf = array( n, typecode, color)
                        rbuf = array(-1, typecode, (rsize, n+color))
                        comm.Allgatherv(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)
                else:
                    for n in range(rsize):
                        sbuf = array( n, typecode, n+color)
                        rbuf = array(-1, typecode, (rsize, color))
                        comm.Allgatherv(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)

    def testAlltoallv(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for n in range(size):
                        sbuf = array( n, typecode, (rsize, (n+1)*color))
                        rbuf = array(-1, typecode, (rsize, n+3*color))
                        comm.Alltoallv(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)
                else:
                    for n in range(rsize):
                        sbuf = array( n, typecode, (rsize, n+3*color))
                        rbuf = array(-1, typecode, (rsize, (n+1)*color))
                        comm.Alltoallv(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)

    def testAlltoallw(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for n in range(size):
                        sbuf = array( n, typecode, (rsize, (n+1)*color))
                        rbuf = array(-1, typecode, (rsize, n+3*color))
                        comm.Alltoallv(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)
                else:
                    for n in range(rsize):
                        sbuf = array( n, typecode, (rsize, n+3*color))
                        rbuf = array(-1, typecode, (rsize, (n+1)*color))
                        comm.Alltoallv(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)

    def testAlltoallw(self):
        comm = self.INTERCOMM
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for n in range(5):
                check = arrayimpl.scalar(n)
                sbuf = array( n, typecode, (rsize, n))
                rbuf = array(-1, typecode, (rsize, n))
                sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                sex, rex = sdt.extent, rdt.extent
                sdsp = [i*n*sex for i in range(rsize)]
                rdsp = [i*n*rex for i in range(rsize)]
                smsg = (sbuf.as_raw(), ([n]*rsize, sdsp), [sdt]*rsize)
                rmsg = (rbuf.as_raw(), ([n]*rsize, rdsp), [rdt]*rsize)
                try:
                    comm.Alltoallw(smsg, rmsg)
                except NotImplementedError:
                    self.skipTest('mpi-alltoallw')
                for value in rbuf.flat:
                    self.assertEqual(value, check)


class TestCCOVecInter(BaseTestCCOVecInter, unittest.TestCase):
    BASECOMM = MPI.COMM_WORLD


class TestCCOVecInterDup(TestCCOVecInter):
    def setUp(self):
        self.BASECOMM = self.BASECOMM.Dup()
        super().setUp()
    def tearDown(self):
        self.BASECOMM.Free()
        super().tearDown()


if __name__ == '__main__':
    unittest.main()
