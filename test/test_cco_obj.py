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

class BaseTestCCOObj(object):

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

class BaseTestCCOObjDup(BaseTestCCOObj):
    def setUp(self):
        self.COMM = self.COMM.Dup()
    def tearDown(self):
        self.COMM.Free()
        del self.COMM


class TestCCOObjSelf(BaseTestCCOObj, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOObjWorld(BaseTestCCOObj, unittest.TestCase):
    COMM = MPI.COMM_WORLD


class TestCCOObjSelfDup(BaseTestCCOObjDup, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOObjWorldDup(BaseTestCCOObjDup, unittest.TestCase):
    COMM = MPI.COMM_WORLD


_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestCCOObjWorldDup


if __name__ == '__main__':
    unittest.main()
