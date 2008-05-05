from mpi4py import MPI
import mpiunittest as unittest

class TestCommNull(unittest.TestCase):

    def testContructor(self):
        comm = MPI.Comm()
        self.assertFalse(comm is MPI.COMM_NULL)
        self.assertEqual(comm, MPI.COMM_NULL)

    def testNull(self):
        COMM_NULL = MPI.COMM_NULL
        COMM_SELF = MPI.COMM_SELF
        COMM_WORLD = MPI.COMM_WORLD
        comm_null = MPI.Comm()
        self.assertEqual(comm_null, COMM_NULL)
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.Comm.Compare, COMM_NULL,  COMM_NULL)
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.Comm.Compare, COMM_SELF,  COMM_NULL)
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.Comm.Compare, COMM_WORLD, COMM_NULL)
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.Comm.Compare, COMM_NULL,  COMM_SELF)
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.Comm.Compare, COMM_NULL,  COMM_WORLD)
        for method in ('Get_size', 'Get_rank',
                       'Is_inter', 'Is_intra',
                       'Get_group', 'Get_topology',
                       'Clone',):
            self.assertRaisesMPI(MPI.ERR_COMM, getattr(COMM_NULL, method))

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.COMM_NULL.Free)

    def testGetErrhandler(self):
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.COMM_NULL.Get_errhandler)

    def testSetErrhandler(self):
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.COMM_NULL.Set_errhandler, MPI.ERRORS_RETURN)

    def testAbort(self):
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.COMM_NULL.Abort)

    def testIntraNull(self):
        comm_null = MPI.Intracomm()
        self.assertFalse(comm_null is MPI.COMM_NULL)
        self.assertEqual(comm_null, MPI.COMM_NULL)

    def testInterNull(self):
        comm_null = MPI.Intercomm()
        self.assertFalse(comm_null is MPI.COMM_NULL)
        self.assertEqual(comm_null, MPI.COMM_NULL)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Get_remote_group)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Get_remote_size)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Dup)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Create, MPI.GROUP_EMPTY)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Split, color=0, key=0)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Merge, high=True)

class TestCommBase(object):

    def testPyProps(self):
        comm = self.COMM
        self.assertEqual(comm.Get_size(), comm.size)
        self.assertEqual(comm.Get_rank(), comm.rank)
        self.assertEqual(comm.Is_intra(), comm.is_intra)
        self.assertEqual(comm.Is_inter(), comm.is_inter)
        self.assertEqual(comm.Get_topology(), comm.topology)

    def testGroup(self):
        comm  = self.COMM
        group = self.COMM.Get_group()
        self.assertEqual(comm.Get_size(), group.Get_size())
        self.assertEqual(comm.Get_rank(), group.Get_rank())
        group.Free()
        self.assertEqual(group, MPI.GROUP_NULL)

    def testCloneFree(self):
        comm = self.COMM.Clone()
        comm.Free()
        self.assertEqual(comm, MPI.COMM_NULL)

    def testCompare(self):
        results = (MPI.IDENT, MPI.CONGRUENT, MPI.SIMILAR, MPI.UNEQUAL)
        ccmp = MPI.Comm.Compare(self.COMM, MPI.COMM_WORLD)
        self.assertTrue(ccmp in results)
        ccmp = MPI.Comm.Compare(self.COMM, self.COMM)
        self.assertEqual(ccmp, MPI.IDENT)
        comm = self.COMM.Dup()
        ccmp = MPI.Comm.Compare(self.COMM, comm)
        comm.Free()
        self.assertEqual(ccmp, MPI.CONGRUENT)
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.Comm.Compare, self.COMM, MPI.COMM_NULL)

    def testBarrier(self):
        self.COMM.Barrier()

##     def testBcast(self):
##         messages = [ None, 7, 3.14, 1+2j, 'mpi4py',
##                     [None, 7, 3.14, 1+2j, 'mpi4py'],
##                     (None, 7, 3.14, 1+2j, 'mpi4py'),
##                      dict(k1=None,k2=7,k3=3.14,k4=1+2j,k5='mpi4py')]
##         for smess in messages:
##             rmess = self.COMM.Bcast(smess)
##             self.assertEqual(smess, rmess)
##             for root in range(self.COMM.Get_size()):
##                 rmess = self.COMM.Bcast(smess, root)
##                 self.assertEqual(smess, rmess)

##     def testGather(self):
##         size = self.COMM.Get_size()
##         rank = self.COMM.Get_rank()
##         for root in range(size):
##             rmess = self.COMM.Gather(rank, None, root)
##             if rank == root:
##                 self.assertEqual(rmess, list(range(size)))
##             else:
##                 self.assertEqual(rmess, None)

##     def testScatter(self):
##         size = self.COMM.Get_size()
##         rank = self.COMM.Get_rank()
##         for root in range(size):
##             smess = [rank + root] * size
##             rmess = self.COMM.Scatter(smess, None, root)
##             self.assertEqual(rmess, root * 2)

##     def testAllgather(self):
##         size = self.COMM.Get_size()
##         rank = self.COMM.Get_rank()
##         rmess = self.COMM.Allgather(rank, None)
##         self.assertEqual(rmess, list(range(size)))

##     def testAlltoall(self):
##         size = self.COMM.Get_size()
##         rank = self.COMM.Get_rank()
##         smess = [rank] * size
##         rmess = self.COMM.Alltoall(smess, None)
##         self.assertEqual(rmess, list(range(size)))


    def testIsInter(self):
        is_inter = self.COMM.Is_inter()
        self.assertTrue(type(is_inter) is bool)

    def testGetSetName(self):
        name = self.COMM.Get_name()
        self.COMM.Set_name('comm')
        self.assertEqual(self.COMM.Get_name(), 'comm')
        self.COMM.Set_name(name)
        self.assertEqual(self.COMM.Get_name(), name)

    def testGetParent(self):
        try:
            parent = MPI.Comm.Get_parent()
        except NotImplementedError:
            return
        if parent == MPI.COMM_NULL:
            self.assertRaisesMPI(MPI.ERR_COMM, parent.Disconnect)


class TestCommSelf(TestCommBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF
    def testSize(self):
        size = self.COMM.Get_size()
        self.assertEqual(size, 1)
    def testRank(self):
        rank = self.COMM.Get_rank()
        self.assertEqual(rank, 0)
    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.COMM_SELF.Free)

class TestCommWorld(TestCommBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD
    def testSize(self):
        size = self.COMM.Get_size()
        self.assertTrue(size >= 1)
    def testRank(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        self.assertTrue(rank >= 0 and rank < size)
    def testFree(self):
        self.assertRaises(MPI.Exception, MPI.COMM_WORLD.Free)

class TestCommSelfDup(TestCommSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()
    def testFree(self): pass

class TestCommWorldDup(TestCommWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()
    def testFree(self): pass


_name, _version = MPI.get_vendor()
_name, _version
if _name == 'Open MPI':
    del TestCommNull.testAbort
elif _name == 'LAM/MPI':
    del TestCommNull.testAbort

if __name__ == '__main__':
    unittest.main()
