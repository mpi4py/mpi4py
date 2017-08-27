from mpi4py import MPI
import mpiunittest as unittest

class TestCommNull(unittest.TestCase):

    def testContructor(self):
        comm = MPI.Comm()
        self.assertEqual(comm, MPI.COMM_NULL)
        self.assertFalse(comm is MPI.COMM_NULL)
        def construct(): MPI.Comm((1,2,3))
        self.assertRaises(TypeError, construct)

    def testContructorIntra(self):
        comm_null = MPI.Intracomm()
        self.assertFalse(comm_null is MPI.COMM_NULL)
        self.assertEqual(comm_null, MPI.COMM_NULL)

    def testContructorInter(self):
        comm_null = MPI.Intercomm()
        self.assertFalse(comm_null is MPI.COMM_NULL)
        self.assertEqual(comm_null, MPI.COMM_NULL)

class BaseTestComm(object):

    def testContructor(self):
        comm = MPI.Comm(self.COMM)
        self.assertEqual(comm, self.COMM)
        self.assertFalse(comm is self.COMM)

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
        try:
            name = self.COMM.Get_name()
            self.COMM.Set_name('comm')
            self.assertEqual(self.COMM.Get_name(), 'comm')
            self.COMM.Set_name(name)
            self.assertEqual(self.COMM.Get_name(), name)
        except NotImplementedError:
            self.skipTest('mpi-comm-name')

    def testGetParent(self):
        try:
            parent = MPI.Comm.Get_parent()
        except NotImplementedError:
            self.skipTest('mpi-comm-get_parent')

    def testDupWithInfo(self):
        info = None
        self.COMM.Dup(info).Free()
        info = MPI.INFO_NULL
        self.COMM.Dup(info).Free()
        self.COMM.Dup_with_info(info).Free()
        info = MPI.Info.Create()
        self.COMM.Dup(info).Free()
        self.COMM.Dup_with_info(info).Free()
        info.Free()

    @unittest.skipMPI('mpich(<=3.1.0)', MPI.Query_thread() > MPI.THREAD_SINGLE)
    def testIDup(self):
        try:
            comm, request = self.COMM.Idup()
        except NotImplementedError:
            self.skipTest('mpi-comm-idup')
        request.Wait()
        ccmp = MPI.Comm.Compare(self.COMM, comm)
        comm.Free()
        self.assertEqual(ccmp, MPI.CONGRUENT)

    def testGetSetInfo(self):
        #info = MPI.INFO_NULL
        #self.COMM.Set_info(info)
        info = MPI.Info.Create()
        self.COMM.Set_info(info)
        info.Free()
        info = self.COMM.Get_info()
        self.COMM.Set_info(info)
        info.Free()

    def testCreate(self):
        group = self.COMM.Get_group()
        comm = self.COMM.Create(group)
        ccmp = MPI.Comm.Compare(self.COMM, comm)
        self.assertEqual(ccmp, MPI.CONGRUENT)
        comm.Free()
        group.Free()

    @unittest.skipMPI('openmpi(<=1.8.1)')
    def testCreateGroup(self):
        group = self.COMM.Get_group()
        try:
            try:
                comm = self.COMM.Create_group(group)
                ccmp = MPI.Comm.Compare(self.COMM, comm)
                self.assertEqual(ccmp, MPI.CONGRUENT)
                comm.Free()
            finally:
                group.Free()
        except NotImplementedError:
            self.skipTest('mpi-comm-create_group')


    @unittest.skipMPI('openmpi(==2.0.0)')
    def testSplitType(self):
        try:
            MPI.COMM_SELF.Split_type(MPI.COMM_TYPE_SHARED).Free()
        except NotImplementedError:
            self.skipTest('mpi-comm-split_type')
        #comm = self.COMM.Split_type(MPI.UNDEFINED)
        #self.assertEqual(comm, MPI.COMM_NULL)
        comm = self.COMM.Split_type(MPI.COMM_TYPE_SHARED)
        self.assertNotEqual(comm, MPI.COMM_NULL)
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        if size == 1:
            self.assertEqual(comm.size, 1)
            self.assertEqual(comm.rank, 0)
        comm.Free()
        for root in range(size):
            if rank == root:
                split_type = MPI.COMM_TYPE_SHARED
            else:
                split_type = MPI.UNDEFINED
            comm = self.COMM.Split_type(split_type)
            if rank == root:
                self.assertNotEqual(comm, MPI.COMM_NULL)
                self.assertEqual(comm.size, 1)
                self.assertEqual(comm.rank, 0)
                comm.Free()
            else:
                self.assertEqual(comm, MPI.COMM_NULL)


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

@unittest.skipMPI('openmpi(<1.4.0)', MPI.Query_thread() > MPI.THREAD_SINGLE)
class TestCommWorldDup(TestCommWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    unittest.main()
