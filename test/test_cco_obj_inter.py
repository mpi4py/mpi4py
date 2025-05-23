import operator
from functools import reduce

import mpiunittest as unittest

from mpi4py import MPI


def cumsum(seq):
    return reduce(operator.add, seq, 0)


def cumprod(seq):
    return reduce(operator.mul, seq, 1)


_basic = [
    None,
    True,
    False,
    -7,
    0,
    7,
    2**31,
    -(2**63) + 1,
    2**63 - 1,
    -2.17,
    0.0,
    +1.62,
    1 + 2j,
    2 - 3j,
    "mpi4py",
]
messages = list(_basic)
messages += [
    list(_basic),
    tuple(_basic),
    {f"k{k}": v for k, v in enumerate(_basic)},
]


@unittest.skipMPI("openmpi(<1.6.0)")
@unittest.skipMPI("msmpi", MPI.COMM_WORLD.Get_size() >= 3)
@unittest.skipMPI("MPICH1")
@unittest.skipIf(MPI.ROOT == MPI.PROC_NULL, "mpi-root")
@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, "mpi-world-size<2")
class BaseTestCCOObjInter:
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

    @unittest.skipMPI("MPICH2(<1.0.8)")
    def testBarrier(self):
        self.INTERCOMM.barrier()

    def testBcast(self):
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in [*messages, messages]:
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = self.INTERCOMM.bcast(smess, root=MPI.ROOT)
                        else:
                            rmess = self.INTERCOMM.bcast(
                                None, root=MPI.PROC_NULL
                            )
                        self.assertIsNone(rmess)
                else:
                    for root in range(rsize):
                        rmess = self.INTERCOMM.bcast(None, root=root)
                        self.assertEqual(rmess, smess)

    def testGather(self):
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in [*messages, messages]:
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = self.INTERCOMM.gather(smess, root=MPI.ROOT)
                            self.assertEqual(rmess, [smess] * rsize)
                        else:
                            rmess = self.INTERCOMM.gather(
                                None, root=MPI.PROC_NULL
                            )
                            self.assertIsNone(rmess)
                else:
                    for root in range(rsize):
                        rmess = self.INTERCOMM.gather(smess, root=root)
                        self.assertIsNone(rmess)

    @unittest.skipMPI("msmpi(<8.0.0)")
    def testScatter(self):
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in [*messages, messages]:
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = self.INTERCOMM.scatter(
                                [smess] * rsize, root=MPI.ROOT
                            )
                        else:
                            rmess = self.INTERCOMM.scatter(
                                None, root=MPI.PROC_NULL
                            )
                        self.assertIsNone(rmess)
                else:
                    for root in range(rsize):
                        rmess = self.INTERCOMM.scatter(None, root=root)
                        self.assertEqual(rmess, smess)

    @unittest.skipMPI("MPICH2(<1.0.8)")
    def testAllgather(self):
        self.INTERCOMM.Get_rank()
        self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in [*messages, messages]:
            rmess = self.INTERCOMM.allgather(smess)
            self.assertEqual(rmess, [smess] * rsize)

    def testAlltoall(self):
        self.INTERCOMM.Get_rank()
        self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in [*messages, messages]:
            rmess = self.INTERCOMM.alltoall([smess] * rsize)
            self.assertEqual(rmess, [smess] * rsize)

    def testReduce(self):
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            value = self.INTERCOMM.reduce(
                                None, op=op, root=MPI.ROOT
                            )
                            if op == MPI.SUM:
                                self.assertEqual(value, cumsum(range(rsize)))
                            elif op == MPI.PROD:
                                self.assertEqual(value, cumprod(range(rsize)))
                            elif op == MPI.MAX:
                                self.assertEqual(value, rsize - 1)
                            elif op == MPI.MIN:
                                self.assertEqual(value, 0)
                        else:
                            value = self.INTERCOMM.reduce(
                                None, op=op, root=MPI.PROC_NULL
                            )
                            self.assertIsNone(value)
                else:
                    for root in range(rsize):
                        value = self.INTERCOMM.reduce(rank, op=op, root=root)
                        self.assertIsNone(value)
        badroots = {-3, -2, -1, rsize}.difference({MPI.ROOT, MPI.PROC_NULL})
        for root in badroots:
            with self.assertRaises(MPI.Exception) as cm:
                self.INTERCOMM.reduce(None, op=MPI.NO_OP, root=root)
            ierr = cm.exception.Get_error_class()
            self.assertEqual(ierr, MPI.ERR_ROOT)

    @unittest.skipMPI("MPICH2(<1.0.8)")
    def testAllreduce(self):
        rank = self.INTERCOMM.Get_rank()
        self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
            value = self.INTERCOMM.allreduce(rank, op)
            if op == MPI.SUM:
                self.assertEqual(value, cumsum(range(rsize)))
            elif op == MPI.PROD:
                self.assertEqual(value, cumprod(range(rsize)))
            elif op == MPI.MAX:
                self.assertEqual(value, rsize - 1)
            elif op == MPI.MIN:
                self.assertEqual(value, 0)


class TestCCOObjInter(BaseTestCCOObjInter, unittest.TestCase):
    #
    BASECOMM = MPI.COMM_WORLD


class TestCCOObjInterDup(TestCCOObjInter):
    #
    def setUp(self):
        self.BASECOMM = self.BASECOMM.Dup()
        super().setUp()

    def tearDown(self):
        self.BASECOMM.Free()
        super().tearDown()


class TestCCOObjInterDupDup(TestCCOObjInterDup):
    #
    BASECOMM = MPI.COMM_WORLD
    INTERCOMM_ORIG = MPI.COMM_NULL

    def setUp(self):
        super().setUp()
        self.INTERCOMM_ORIG = self.INTERCOMM
        self.INTERCOMM = self.INTERCOMM.Dup()

    def tearDown(self):
        super().tearDown()
        self.INTERCOMM_ORIG.Free()


if __name__ == "__main__":
    unittest.main()
