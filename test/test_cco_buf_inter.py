import arrayimpl
import mpiunittest as unittest

from mpi4py import MPI


def skip_op(typecode, op):
    if typecode == "?":
        return True
    if typecode in "FDG":
        if op in (MPI.MAX, MPI.MIN):
            return True
    return False


def maxvalue(a):
    try:
        typecode = a.typecode
    except AttributeError:
        typecode = a.dtype.char
    if typecode == ("f"):
        return 1e30
    elif typecode == ("d"):
        return 1e300
    else:
        return 2 ** (a.itemsize * 7) - 1


@unittest.skipMPI("openmpi(<1.6.0)")
@unittest.skipMPI("msmpi", MPI.COMM_WORLD.Get_size() >= 3)
@unittest.skipMPI("MPICH1")
@unittest.skipIf(MPI.ROOT == MPI.PROC_NULL, "mpi-root")
@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, "mpi-world-size<2")
class BaseTestCCOBufInter:
    #
    BASECOMM = MPI.COMM_NULL
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

    def testBarrier(self):
        self.INTERCOMM.Barrier()

    def testBcast(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            buf = array(root, typecode, root + color)
                            comm.Bcast(buf.as_mpi(), root=MPI.ROOT)
                        else:
                            comm.Bcast(None, root=MPI.PROC_NULL)
                else:
                    for root in range(rsize):
                        buf = array(-1, typecode, root + color)
                        comm.Bcast(buf.as_mpi(), root=root)
                        check = arrayimpl.scalar(root)
                        for value in buf:
                            self.assertEqual(value, check)

    def testGather(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rbuf = array(-1, typecode, (rsize, root + color))
                            comm.Gather(None, rbuf.as_mpi(), root=MPI.ROOT)
                            check = arrayimpl.scalar(root)
                            for value in rbuf.flat:
                                self.assertEqual(value, check)
                        else:
                            comm.Gather(None, None, root=MPI.PROC_NULL)
                else:
                    for root in range(rsize):
                        sbuf = array(root, typecode, root + color)
                        comm.Gather(sbuf.as_mpi(), None, root=root)

    def testScatter(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            sbuf = array(root, typecode, (rsize, root + color))
                            comm.Scatter(sbuf.as_mpi(), None, root=MPI.ROOT)
                        else:
                            comm.Scatter(None, None, root=MPI.PROC_NULL)
                else:
                    for root in range(rsize):
                        rbuf = array(root, typecode, root + color)
                        comm.Scatter(None, rbuf.as_mpi(), root=root)
                        check = arrayimpl.scalar(root)
                        for value in rbuf:
                            self.assertEqual(value, check)

    def testAllgather(self):
        comm = self.INTERCOMM
        comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for n in range(size):
                        sbuf = array(n, typecode, color)
                        rbuf = array(-1, typecode, (rsize, n + color))
                        comm.Allgather(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)
                else:
                    for n in range(rsize):
                        sbuf = array(n, typecode, n + color)
                        rbuf = array(-1, typecode, (rsize, color))
                        comm.Allgather(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)

    def testAlltoall(self):
        comm = self.INTERCOMM
        comm.Get_rank()
        size = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for color in (0, 1):
                if self.COLOR == color:
                    for n in range(size):
                        sbuf = array(n, typecode, (rsize, (n + 1) * color))
                        rbuf = array(-1, typecode, (rsize, n + 3 * color))
                        comm.Alltoall(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)
                else:
                    for n in range(rsize):
                        sbuf = array(n, typecode, (rsize, n + 3 * color))
                        rbuf = array(-1, typecode, (rsize, (n + 1) * color))
                        comm.Alltoall(sbuf.as_mpi(), rbuf.as_mpi())
                        check = arrayimpl.scalar(n)
                        for value in rbuf.flat:
                            self.assertEqual(value, check)

    @unittest.skipMPI("mvapich", MPI.COMM_WORLD.Get_size() > 2)
    def testReduce(self):
        comm = self.INTERCOMM
        rank = comm.Get_rank()
        lsize = comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op):
                    continue
                for color in (0, 1):
                    if self.COLOR == color:
                        for root in range(lsize):
                            if root == rank:
                                rbuf = array(-1, typecode, rsize)
                                comm.Reduce(
                                    None,
                                    rbuf.as_mpi(),
                                    op=op,
                                    root=MPI.ROOT,
                                )
                                max_val = maxvalue(rbuf)
                                for i, value in enumerate(rbuf):
                                    if op == MPI.SUM:
                                        if (i * rsize) < max_val:
                                            self.assertAlmostEqual(
                                                value, i * rsize
                                            )
                                    elif op == MPI.PROD:
                                        if (i**rsize) < max_val:
                                            self.assertAlmostEqual(
                                                value, i**rsize
                                            )
                                    elif op == MPI.MAX:
                                        self.assertEqual(value, i)
                                    elif op == MPI.MIN:
                                        self.assertEqual(value, i)
                            else:
                                comm.Reduce(
                                    None,
                                    None,
                                    op=op,
                                    root=MPI.PROC_NULL,
                                )
                    else:
                        for root in range(rsize):
                            sbuf = array(range(lsize), typecode)
                            comm.Reduce(
                                sbuf.as_mpi(),
                                None,
                                op=op,
                                root=root,
                            )

    def testAllreduce(self):
        comm = self.INTERCOMM
        comm.Get_rank()
        comm.Get_size()
        rsize = comm.Get_remote_size()
        for array, typecode in arrayimpl.loop():
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op):
                    continue
                sbuf = array(range(5), typecode)
                rbuf = array([-1] * 5, typecode)
                comm.Allreduce(sbuf.as_mpi(), rbuf.as_mpi(), op)
                max_val = maxvalue(rbuf)
                for i, value in enumerate(rbuf):
                    if op == MPI.SUM:
                        if (i * rsize) < max_val:
                            self.assertAlmostEqual(value, i * rsize)
                    elif op == MPI.PROD:
                        if (i**rsize) < max_val:
                            self.assertAlmostEqual(value, i**rsize)
                    elif op == MPI.MAX:
                        self.assertEqual(value, i)
                    elif op == MPI.MIN:
                        self.assertEqual(value, i)


class TestCCOBufInter(BaseTestCCOBufInter, unittest.TestCase):
    #
    BASECOMM = MPI.COMM_WORLD


class TestCCOBufInterDup(TestCCOBufInter):
    #
    def setUp(self):
        self.BASECOMM = self.BASECOMM.Dup()
        super().setUp()

    def tearDown(self):
        self.BASECOMM.Free()
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
