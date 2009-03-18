from mpi4py import MPI
import mpiunittest as unittest

class TestCommNull(unittest.TestCase):

    def testContructor(self):
        comm = MPI.Comm()
        self.assertFalse(comm is MPI.COMM_NULL)
        self.assertEqual(comm, MPI.COMM_NULL)

    def testContructorIntra(self):
        comm_null = MPI.Intracomm()
        self.assertFalse(comm_null is MPI.COMM_NULL)
        self.assertEqual(comm_null, MPI.COMM_NULL)

    def testContructorInter(self):
        comm_null = MPI.Intercomm()
        self.assertFalse(comm_null is MPI.COMM_NULL)
        self.assertEqual(comm_null, MPI.COMM_NULL)

class BaseTestComm(object):

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


class TestCommSelf(BaseTestComm, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF
    def testSize(self):
        size = self.COMM.Get_size()
        self.assertEqual(size, 1)
    def testRank(self):
        rank = self.COMM.Get_rank()
        self.assertEqual(rank, 0)

class TestCommWorld(BaseTestComm, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD
    def testSize(self):
        size = self.COMM.Get_size()
        self.assertTrue(size >= 1)
    def testRank(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        self.assertTrue(rank >= 0 and rank < size)

class TestCommSelfDup(TestCommSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCommWorldDup(TestCommWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestCommWorldDup


if __name__ == '__main__':
    unittest.main()
