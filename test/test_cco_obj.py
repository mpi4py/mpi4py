from mpi4py import MPI
import mpiunittest as unittest

try:
    _reduce = reduce
except NameError:
    from functools import reduce as _reduce

cumsum  = lambda seq: _reduce(lambda x, y: x+y, seq, 0)

cumprod = lambda seq: _reduce(lambda x, y: x*y, seq, 1)

_basic = [None,
          True, False,
          -7, 0, 7, 2**31,
          -2**63, 2**63-1,
          -2.17, 0.0, 3.14,
          1+2j, 2-3j,
          'mpi4py',
          ]

messages = _basic
messages += [ list(_basic),
              tuple(_basic),
              dict([('k%d' % key, val)
                    for key, val in enumerate(_basic)])
              ]

class TestCCOObjBase(object):

    COMM = MPI.COMM_NULL

    def testBarrier(self):
        self.COMM.barrier()

    def testBcast(self):
        for smess in messages:
            for root in range(self.COMM.Get_size()):
                rmess = self.COMM.bcast(smess, root=root)
                self.assertEqual(smess, rmess)

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            for root in range(size):
                rmess = self.COMM.gather(smess, root=root)
                if rank == root:
                    self.assertEqual(rmess, [smess] * size)
                else:
                    self.assertEqual(rmess, None)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            for root in range(size):
                if rank == root:
                    rmess = self.COMM.scatter([smess] * size, root=root)
                else:
                    rmess = self.COMM.scatter(None, root=root)
                self.assertEqual(rmess, smess)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            rmess = self.COMM.allgather(smess, None)
            self.assertEqual(rmess, [smess] * size)

    def testAlltoall(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages + [messages]:
            rmess = self.COMM.alltoall([smess] * size, None)
            self.assertEqual(rmess, [smess] * size)

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for root in range(size):
            for op in (MPI.SUM, MPI.PROD,
                       MPI.MAX, MPI.MIN,
                       MPI.MAXLOC, MPI.MINLOC):
                value = self.COMM.reduce(rank, None, op=op, root=root)
                if rank != root:
                    self.assertTrue(value is None)
                else:
                    if op == MPI.SUM:
                        self.assertEqual(value, cumsum(range(size)))
                    elif op == MPI.PROD:
                        self.assertEqual(value, cumprod(range(size)))
                    elif op == MPI.MAX:
                        self.assertEqual(value, size-1)
                    elif op == MPI.MIN:
                        self.assertEqual(value, 0)
                    elif op == MPI.MAXLOC:
                        self.assertEqual(value[1], size-1)
                    elif op == MPI.MINLOC:
                        self.assertEqual(value[1], 0)

    def testAllreduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for op in (MPI.SUM, MPI.PROD,
                   MPI.MAX, MPI.MIN,
                   MPI.MAXLOC, MPI.MINLOC):
            value = self.COMM.allreduce(rank, None, op)
            if op == MPI.SUM:
                self.assertEqual(value, cumsum(range(size)))
            elif op == MPI.PROD:
                self.assertEqual(value, cumprod(range(size)))
            elif op == MPI.MAX:
                self.assertEqual(value, size-1)
            elif op == MPI.MIN:
                self.assertEqual(value, 0)
            elif op == MPI.MAXLOC:
                self.assertEqual(value[1], size-1)
            elif op == MPI.MINLOC:
                self.assertEqual(value[1], 0)


    def testScan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        sscan = self.COMM.scan(size, op=MPI.SUM)
        self.assertEqual(sscan, cumsum([size]*(rank+1)))
        # --
        rscan = self.COMM.scan(rank, op=MPI.SUM)
        self.assertEqual(rscan, cumsum(range(rank+1)))
        # --
        minloc = self.COMM.scan(rank, op=MPI.MINLOC)
        maxloc = self.COMM.scan(rank, op=MPI.MAXLOC)
        self.assertEqual(minloc, (0, 0))
        self.assertEqual(maxloc, (rank, rank))

    def testExscan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        sscan = self.COMM.exscan(size, op=MPI.SUM)
        if rank == 0:
            self.assertTrue(sscan is None)
        else:
            self.assertEqual(sscan, cumsum([size]*(rank)))
        # --
        rscan = self.COMM.exscan(rank, op=MPI.SUM)
        if rank == 0:
            self.assertTrue(rscan is None)
        else:
            self.assertEqual(rscan, cumsum(range(rank)))
        #
        minloc = self.COMM.exscan(rank, op=MPI.MINLOC)
        maxloc = self.COMM.exscan(rank, op=MPI.MAXLOC)
        if rank == 0:
            self.assertEqual(minloc, None)
            self.assertEqual(maxloc, None)
        else:
            self.assertEqual(minloc, (0, 0))
            self.assertEqual(maxloc, (rank-1, rank-1))

class TestCCOObjInterBase(object):

    BASECOMM  = MPI.COMM_NULL
    INTRACOMM = MPI.COMM_NULL
    INTERCOMM = MPI.COMM_NULL

    def setUp(self):
        BASE_SIZE = self.BASECOMM.Get_size()
        BASE_RANK = self.BASECOMM.Get_rank()
        if BASE_SIZE < 2:
            return
        if BASE_RANK < BASE_SIZE // 2 :
            self.COLOR = 0
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = BASE_SIZE // 2
        else:
            self.COLOR = 1
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = 0
        self.INTRACOMM = self.BASECOMM.Split(self.COLOR, key=0)
        self.INTERCOMM = self.INTRACOMM.Create_intercomm(self.LOCAL_LEADER,
                                                         self.BASECOMM,
                                                         self.REMOTE_LEADER)

    def tearDown(self):
        if self.INTRACOMM != MPI.COMM_NULL:
            self.INTRACOMM.Free()
        if self.INTERCOMM != MPI.COMM_NULL:
            self.INTERCOMM.Free()

    def testBarrier(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        self.INTERCOMM.Barrier()

    def testBcast(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = self.INTERCOMM.bcast(smess, root=MPI.ROOT)
                        else:
                            rmess = self.INTERCOMM.bcast(None, root=MPI.PROC_NULL)
                        self.assertEqual(rmess, None)
                else:
                    for root in range(rsize):
                        rmess = self.INTERCOMM.bcast(None, root=root)
                        self.assertEqual(rmess, smess)

    def testGather(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = self.INTERCOMM.gather(smess, root=MPI.ROOT)
                            self.assertEqual(rmess, [smess] * rsize)
                        else:
                            rmess = self.INTERCOMM.gather(None, root=MPI.PROC_NULL)
                            self.assertEqual(rmess, None)
                else:
                    for root in range(rsize):
                        rmess = self.INTERCOMM.gather(smess, root=root)
                        self.assertEqual(rmess, None)

    def testScatter(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            rmess = self.INTERCOMM.scatter([smess] * rsize, root=MPI.ROOT)
                        else:
                            rmess = self.INTERCOMM.scatter(None, root=MPI.PROC_NULL)
                        self.assertEqual(rmess, None)
                else:
                    for root in range(rsize):
                        rmess = self.INTERCOMM.scatter(None, root=root)
                        self.assertEqual(rmess, smess)

    def testAllgather(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            rmess = self.INTERCOMM.allgather(smess)
            self.assertEqual(rmess, [smess] * rsize)

    def testAlltoall(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for smess in messages + [messages]:
            rmess = self.INTERCOMM.alltoall([smess] * rsize)
            self.assertEqual(rmess, [smess] * rsize)

    def testReduce(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
            for color in [0, 1]:
                if self.COLOR == color:
                    for root in range(size):
                        if root == rank:
                            value = self.INTERCOMM.reduce(None, op=op, root=MPI.ROOT)
                            if op == MPI.SUM:
                                self.assertEqual(value, cumsum(range(rsize)))
                            elif op == MPI.PROD:
                                self.assertEqual(value, cumprod(range(rsize)))
                            elif op == MPI.MAX:
                                self.assertEqual(value, rsize-1)
                            elif op == MPI.MIN:
                                self.assertEqual(value, 0)
                        else:
                            value = self.INTERCOMM.reduce(None, op=op, root=MPI.PROC_NULL)
                            self.assertEqual(value, None)
                else:
                    for root in range(rsize):
                        value = self.INTERCOMM.reduce(rank, op=op, root=root)
                        self.assertEqual(value, None)

    def testAllreduce(self):
        if self.INTRACOMM == MPI.COMM_NULL: return
        if self.INTERCOMM == MPI.COMM_NULL: return
        rank = self.INTERCOMM.Get_rank()
        size = self.INTERCOMM.Get_size()
        rsize = self.INTERCOMM.Get_remote_size()
        for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
            value = self.INTERCOMM.allreduce(rank, None, op)
            if op == MPI.SUM:
                self.assertEqual(value, cumsum(range(rsize)))
            elif op == MPI.PROD:
                self.assertEqual(value, cumprod(range(rsize)))
            elif op == MPI.MAX:
                self.assertEqual(value, rsize-1)
            elif op == MPI.MIN:
                self.assertEqual(value, 0)


class TestCCOObjSelf(TestCCOObjBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOObjWorld(TestCCOObjBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD


class TestCCOObjDupBase(TestCCOObjBase):
    def setUp(self):
        self.COMM = self.COMM.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCOObjSelfDup(TestCCOObjDupBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOObjWorldDup(TestCCOObjDupBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD



class TestCCOObjInter(TestCCOObjInterBase, unittest.TestCase):
    BASECOMM = MPI.COMM_WORLD

class TestCCOObjInterDup(TestCCOObjInter):
    def setUp(self):
        self.BASECOMM = self.BASECOMM.Dup()
        super(TestCCOObjInterDup, self).setUp()
    def tearDown(self):
        self.BASECOMM.Free()
        super(TestCCOObjInterDup, self).tearDown()

class TestCCOObjInterDupDup(TestCCOObjInterDup):
    BASECOMM = MPI.COMM_WORLD
    def setUp(self):
        super(TestCCOObjInterDupDup, self).setUp()
        if self.INTERCOMM == MPI.COMM_NULL: return
        self.INTERCOMM = self.INTERCOMM.Dup()
    def tearDown(self):
        super(TestCCOObjInterDupDup, self).tearDown()
        if self.INTERCOMM == MPI.COMM_NULL: return
        self.INTERCOMM = self.INTERCOMM.Dup()


_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 2, 4):
        del TestCCOObjInter
        del TestCCOObjInterDup
        del TestCCOObjInterDupDup
elif _name == "MPICH2":
    if _version <= (1, 0, 7):
        def _SKIPPED(*args, **kwargs): pass
        TestCCOObjInterDupDup.testBarrier   = _SKIPPED
        TestCCOObjInterDupDup.testAllgather = _SKIPPED
        TestCCOObjInterDupDup.testAllreduce = _SKIPPED
elif MPI.ROOT == MPI.PROC_NULL:
    del TestCCOObjInterBase
    del TestCCOObjInter
    del TestCCOObjInterDup
    del TestCCOObjInterDupDup

if __name__ == '__main__':
    unittest.main()
