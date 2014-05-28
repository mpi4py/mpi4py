#import mpi4py
#mpi4py.profile("mpe")
from mpi4py import MPI

import unittest

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from reductions import Intracomm
del sys.path[0]

class BaseTest(object):

    def test_reduce(self):
        rank = self.comm.rank
        size = self.comm.size
        for root in range(size):
            msg = rank
            res = self.comm.reduce(sendobj=msg, root=root)
            if self.comm.rank == root:
                self.assertEqual(res, sum(range(size)))
            else:
                self.assertEqual(res, None)

    def test_reduce_min(self):
        rank = self.comm.rank
        size = self.comm.size
        for root in range(size):
            msg = rank
            res = self.comm.reduce(sendobj=msg, op=MPI.MIN, root=root)
            if self.comm.rank == root:
                self.assertEqual(res, 0)
            else:
                self.assertEqual(res, None)

    def test_reduce_max(self):
        rank = self.comm.rank
        size = self.comm.size
        for root in range(size):
            msg = rank
            res = self.comm.reduce(sendobj=msg, op=MPI.MAX, root=root)
            if self.comm.rank == root:
                self.assertEqual(res, size-1)
            else:
                self.assertEqual(res, None)

    def test_reduce_minloc(self):
        rank = self.comm.rank
        size = self.comm.size
        for root in range(size):
            msg = rank
            res = self.comm.reduce(sendobj=(msg, rank), op=MPI.MINLOC, root=root)
            if self.comm.rank == root:
                self.assertEqual(res, (0, 0))
            else:
                self.assertEqual(res, None)

    def test_reduce_maxloc(self):
        rank = self.comm.rank
        size = self.comm.size
        for root in range(size):
            msg = rank
            res = self.comm.reduce(sendobj=(msg, rank), op=MPI.MAXLOC, root=root)
            if self.comm.rank == root:
                self.assertEqual(res, (size-1, size-1))
            else:
                self.assertEqual(res, None)

    def test_allreduce(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.allreduce(sendobj=msg)
        self.assertEqual(res, sum(range(size)))

    def test_allreduce_min(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.allreduce(sendobj=msg, op=MPI.MIN)
        self.assertEqual(res, 0)

    def test_allreduce_max(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.allreduce(sendobj=msg, op=MPI.MAX)
        self.assertEqual(res, size-1)

    def test_allreduce_minloc(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.allreduce(sendobj=(msg, rank), op=MPI.MINLOC)
        self.assertEqual(res, (0, 0))

    def test_allreduce_maxloc(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.allreduce(sendobj=(msg, rank), op=MPI.MAXLOC)
        self.assertEqual(res, (size-1, size-1))

    def test_scan(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.scan(sendobj=msg)
        self.assertEqual(res, sum(list(range(size))[:rank+1]))

    def test_scan_min(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.scan(sendobj=msg, op=MPI.MIN)
        self.assertEqual(res, 0)

    def test_scan_max(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.scan(sendobj=msg, op=MPI.MAX)
        self.assertEqual(res, rank)

    def test_scan_minloc(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.scan(sendobj=(msg, rank), op=MPI.MINLOC)
        self.assertEqual(res, (0, 0))

    def test_scan_maxloc(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.scan(sendobj=(msg, rank), op=MPI.MAXLOC)
        self.assertEqual(res, (rank, rank))

    def test_exscan(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.exscan(sendobj=msg)
        if self.comm.rank == 0:
            self.assertEqual(res, None)
        else:
            self.assertEqual(res, sum(list(range(size))[:rank]))

    def test_exscan_min(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.exscan(sendobj=msg, op=MPI.MIN)
        if self.comm.rank == 0:
            self.assertEqual(res, None)
        else:
            self.assertEqual(res, 0)

    def test_exscan_max(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.exscan(sendobj=msg, op=MPI.MAX)
        if self.comm.rank == 0:
            self.assertEqual(res, None)
        else:
            self.assertEqual(res, rank-1)

    def test_exscan_minloc(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.exscan(sendobj=(msg, rank), op=MPI.MINLOC)
        if self.comm.rank == 0:
            self.assertEqual(res, None)
        else:
            self.assertEqual(res, (0, 0))

    def test_exscan_maxloc(self):
        rank = self.comm.rank
        size = self.comm.size
        msg = rank
        res = self.comm.exscan(sendobj=(msg, rank), op=MPI.MAXLOC)
        if self.comm.rank == 0:
            self.assertEqual(res, None)
        else:
            self.assertEqual(res, (rank-1, rank-1))

class TestS(BaseTest, unittest.TestCase):
    def setUp(self):
        self.comm = Intracomm(MPI.COMM_SELF)

class TestW(BaseTest, unittest.TestCase):
    def setUp(self):
        self.comm = Intracomm(MPI.COMM_WORLD)

class TestSD(BaseTest, unittest.TestCase):
    def setUp(self):
        self.comm = Intracomm(MPI.COMM_SELF.Dup())
    def tearDown(self):
        self.comm.Free()

class TestWD(BaseTest, unittest.TestCase):
    def setUp(self):
        self.comm = Intracomm(MPI.COMM_WORLD.Dup())
    def tearDown(self):
        self.comm.Free()

if __name__ == "__main__":
    unittest.main()
