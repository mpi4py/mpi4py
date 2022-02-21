from mpi4py import MPI
import mpiunittest as unittest


@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
class BaseTestIntercomm(object):

    BASECOMM  = MPI.COMM_NULL
    INTRACOMM = MPI.COMM_NULL
    INTERCOMM = MPI.COMM_NULL

    def setUp(self):
        size = self.BASECOMM.Get_size()
        rank = self.BASECOMM.Get_rank()
        if rank < size // 2 :
            self.COLOR = 0
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = size // 2
        else:
            self.COLOR = 1
            self.LOCAL_LEADER = 0
            self.REMOTE_LEADER = 0
        self.INTRACOMM = self.BASECOMM.Split(self.COLOR, key=0)
        Create_intercomm = MPI.Intracomm.Create_intercomm
        self.INTERCOMM = Create_intercomm(self.INTRACOMM,
                                          self.LOCAL_LEADER,
                                          self.BASECOMM,
                                          self.REMOTE_LEADER)

    def tearDown(self):
        self.INTRACOMM.Free()
        self.INTERCOMM.Free()

    def testFortran(self):
        intercomm = self.INTERCOMM
        fint = intercomm.py2f()
        newcomm = MPI.Comm.f2py(fint)
        self.assertEqual(newcomm, intercomm)
        self.assertTrue(type(newcomm) is MPI.Intercomm)

    def testLocalGroupSizeRank(self):
        intercomm = self.INTERCOMM
        local_group = intercomm.Get_group()
        self.assertEqual(local_group.size, intercomm.Get_size())
        self.assertEqual(local_group.size, intercomm.size)
        self.assertEqual(local_group.rank, intercomm.Get_rank())
        self.assertEqual(local_group.rank, intercomm.rank)
        local_group.Free()

    def testRemoteGroupSize(self):
        intercomm = self.INTERCOMM
        remote_group = intercomm.Get_remote_group()
        self.assertEqual(remote_group.size, intercomm.Get_remote_size())
        self.assertEqual(remote_group.size, intercomm.remote_size)
        remote_group.Free()

    def testMerge(self):
        basecomm  = self.BASECOMM
        intercomm = self.INTERCOMM
        if basecomm.rank < basecomm.size // 2:
            high = False
        else:
            high = True
        intracomm = intercomm.Merge(high)
        self.assertEqual(intracomm.size, basecomm.size)
        self.assertEqual(intracomm.rank, basecomm.rank)
        intracomm.Free()

    def testCreateFromGroups(self):
        lgroup = self.INTERCOMM.Get_group()
        rgroup = self.INTERCOMM.Get_remote_group()
        try:
            try:
                Create_from_groups = MPI.Intercomm.Create_from_groups
                intercomm = Create_from_groups(lgroup, 0, rgroup, 0)
                ccmp = MPI.Comm.Compare(self.INTERCOMM, intercomm)
                intercomm.Free()
                self.assertEqual(ccmp, MPI.CONGRUENT)
            finally:
                lgroup.Free()
                rgroup.Free()
        except NotImplementedError:
            self.assertTrue(MPI.VERSION < 4)
            self.skipTest('mpi-comm-create_from_group')


class TestIntercomm(BaseTestIntercomm, unittest.TestCase):
    BASECOMM = MPI.COMM_WORLD

class TestIntercommDup(TestIntercomm):
    def setUp(self):
        self.BASECOMM = self.BASECOMM.Dup()
        super(TestIntercommDup, self).setUp()
    def tearDown(self):
        self.BASECOMM.Free()
        super(TestIntercommDup, self).tearDown()

class TestIntercommDupDup(TestIntercomm):
    def setUp(self):
        super(TestIntercommDupDup, self).setUp()
        INTERCOMM = self.INTERCOMM
        self.INTERCOMM = self.INTERCOMM.Dup()
        INTERCOMM.Free()


@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
class TestIntercommCreateFromGroups(unittest.TestCase):

    def testPair(self):
        done = True
        rank = MPI.COMM_WORLD.Get_rank()
        if rank < 2:
            world_group = MPI.COMM_WORLD.Get_group()
            local_group = world_group.Incl([rank])
            remote_group = world_group.Incl([1 - rank])
            world_group.Free()
            try:
                comm = MPI.Intercomm.Create_from_groups(
                    local_group, 0,
                    remote_group, 0,
                )
                self.assertEqual(comm.Get_size(), 1)
                self.assertEqual(comm.Get_remote_size(), 1)
                comm.Free()
            except NotImplementedError:
                done = False
            finally:
                local_group.Free()
                remote_group.Free()
        done = MPI.COMM_WORLD.allreduce(done, op=MPI.LAND)
        if not done:
            self.assertTrue(MPI.VERSION < 4)
            self.skipTest('mpi-intercomm-create_from_groups')

    def testHalf(self):
        done = True
        size = MPI.COMM_WORLD.Get_size()
        rank = MPI.COMM_WORLD.Get_rank()
        world_group = MPI.COMM_WORLD.Get_group()
        low_group = world_group.Range_incl([(0, size//2-1, 1)])
        high_group = world_group.Range_incl([(size//2, size-1, 1)])
        world_group.Free()
        if rank <= size//2-1:
            local_group, remote_group = low_group, high_group
            local_leader, remote_leader = 0, high_group.Get_size()-1
        else:
            local_group, remote_group = high_group, low_group
            local_leader, remote_leader = high_group.Get_size()-1, 0
        try:
            comm = MPI.Intercomm.Create_from_groups(
                local_group, local_leader,
                remote_group, remote_leader,
            )
            self.assertEqual(comm.Get_rank(), local_group.Get_rank())
            self.assertEqual(comm.Get_size(), local_group.Get_size())
            self.assertEqual(comm.Get_remote_size(), remote_group.Get_size())
            comm.Free()
        except NotImplementedError:
            done = False
        finally:
            local_group.Free()
            remote_group.Free()
        if not done:
            self.assertTrue(MPI.VERSION < 4)
            self.skipTest('mpi-intercomm-create_from_groups')


if __name__ == '__main__':
    unittest.main()
