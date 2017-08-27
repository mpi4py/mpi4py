from mpi4py import MPI
import mpiunittest as unittest


class BaseTestGroup(object):

    def testProperties(self):
        group = self.GROUP
        self.assertEqual(group.Get_size(), group.size)
        self.assertEqual(group.Get_rank(), group.rank)

    def testCompare(self):
        results = (MPI.IDENT, MPI.SIMILAR, MPI.UNEQUAL)
        group = MPI.COMM_WORLD.Get_group()
        gcmp = MPI.Group.Compare(self.GROUP, group)
        group.Free()
        self.assertTrue(gcmp in results)
        gcmp = MPI.Group.Compare(self.GROUP, self.GROUP)
        self.assertEqual(gcmp, MPI.IDENT)

    def testDup(self):
        group = self.GROUP.Dup()
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()

    def testUnion(self):
        group = MPI.Group.Union(MPI.GROUP_EMPTY, self.GROUP)
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()
        group = MPI.Group.Union(self.GROUP, MPI.GROUP_EMPTY)
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()
        group = MPI.Group.Union(self.GROUP, self.GROUP)
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()

    def testDifference(self):
        group = MPI.Group.Difference(MPI.GROUP_EMPTY, self.GROUP)
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()
        group = MPI.Group.Difference(self.GROUP, MPI.GROUP_EMPTY)
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()
        group = MPI.Group.Difference(self.GROUP, self.GROUP)
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()

    def testIntersection(self):
        group = MPI.Group.Intersection(MPI.GROUP_EMPTY, self.GROUP)
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()
        group = MPI.Group.Intersection(self.GROUP, MPI.GROUP_EMPTY)
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()
        group = MPI.Group.Intersection(self.GROUP, self.GROUP)
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()

    def testIncl(self):
        group = self.GROUP.Incl([])
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()

    def testExcl(self):
        group = self.GROUP.Excl([])
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()

    def testRangeIncl(self):
        if self.GROUP == MPI.GROUP_EMPTY: return
        group = self.GROUP.Range_incl([])
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()
        ranges = [ (0, self.GROUP.Get_size()-1, 1), ]
        group = self.GROUP.Range_incl(ranges)
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()

    def testRangeExcl(self):
        if self.GROUP == MPI.GROUP_EMPTY: return
        group = self.GROUP.Range_excl([])
        self.assertEqual(MPI.Group.Compare(group, self.GROUP), MPI.IDENT)
        group.Free()
        ranges = [ (0, self.GROUP.Get_size()-1, 1), ]
        group = self.GROUP.Range_excl(ranges)
        self.assertEqual(MPI.Group.Compare(group, MPI.GROUP_EMPTY), MPI.IDENT)
        group.Free()

    def testTranslRanks(self):
        group1 = self.GROUP
        group2 = self.GROUP
        ranks1 = list(range(group1.Get_size())) * 3
        ranks2 = MPI.Group.Translate_ranks(group1, ranks1)
        ranks2 = MPI.Group.Translate_ranks(group1, ranks1, group2)
        self.assertEqual(list(ranks1), list(ranks2))

    @unittest.skipMPI('PlatformMPI')
    @unittest.skipMPI('MPICH1')
    @unittest.skipMPI('LAM/MPI')
    def testTranslRanksProcNull(self):
        if self.GROUP == MPI.GROUP_EMPTY: return
        group1 = self.GROUP
        group2 = self.GROUP
        ranks1 = [MPI.PROC_NULL] * 10
        ranks2 = MPI.Group.Translate_ranks(group1, ranks1, group2)
        self.assertEqual(list(ranks1), list(ranks2))

    def testTranslRanksGroupEmpty(self):
        if self.GROUP == MPI.GROUP_EMPTY: return
        group1 = self.GROUP
        group2 = MPI.GROUP_EMPTY
        ranks1 = list(range(group1.Get_size())) * 2
        ranks2 = MPI.Group.Translate_ranks(group1, ranks1, group2)
        for rank in ranks2:
            self.assertEqual(rank, MPI.UNDEFINED)


class TestGroupNull(unittest.TestCase):

    def testContructor(self):
        group = MPI.Group()
        self.assertFalse(group is MPI.GROUP_NULL)
        self.assertEqual(group, MPI.GROUP_NULL)

    def testNull(self):
        GROUP_NULL = MPI.GROUP_NULL
        group_null = MPI.Group()
        self.assertFalse(GROUP_NULL)
        self.assertFalse(group_null)
        self.assertEqual(group_null, GROUP_NULL)

class TestGroupEmpty(BaseTestGroup, unittest.TestCase):
    def setUp(self):
        self.GROUP = MPI.GROUP_EMPTY
    def testEmpty(self):
        self.assertTrue(self.GROUP)
    def testSize(self):
        size = self.GROUP.Get_size()
        self.assertEqual(size, 0)
    def testRank(self):
        rank = self.GROUP.Get_rank()
        self.assertEqual(rank, MPI.UNDEFINED)
    @unittest.skipMPI('MPICH1')
    def testTranslRanks(self):
        super(TestGroupEmpty, self).testTranslRanks()

class TestGroupSelf(BaseTestGroup, unittest.TestCase):
    def setUp(self):
        self.GROUP = MPI.COMM_SELF.Get_group()
    def tearDown(self):
        self.GROUP.Free()
    def testSize(self):
        size = self.GROUP.Get_size()
        self.assertEqual(size, 1)
    def testRank(self):
        rank = self.GROUP.Get_rank()
        self.assertEqual(rank, 0)

class TestGroupWorld(BaseTestGroup, unittest.TestCase):
    def setUp(self):
        self.GROUP = MPI.COMM_WORLD.Get_group()
    def tearDown(self):
        self.GROUP.Free()
    def testSize(self):
        size = self.GROUP.Get_size()
        self.assertTrue(size >= 1)
    def testRank(self):
        size = self.GROUP.Get_size()
        rank = self.GROUP.Get_rank()
        self.assertTrue(rank >= 0 and rank < size)


if __name__ == '__main__':
    unittest.main()
