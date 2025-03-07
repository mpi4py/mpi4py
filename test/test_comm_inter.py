from mpi4py import MPI
import mpiunittest as unittest


def ch3_nemesis():
    return 'ch3:nemesis' in MPI.Get_library_version()


@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
class BaseTestIntercomm:

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

    def testConstructor(self):
        with self.assertRaises(TypeError):
            MPI.Intercomm(self.INTRACOMM)
        with self.assertRaises(TypeError):
            MPI.Intracomm(self.INTERCOMM)

    def tearDown(self):
        self.INTRACOMM.Free()
        self.INTERCOMM.Free()

    def testHandle(self):
        intercomm = self.INTERCOMM
        cint = intercomm.toint()
        if cint != -1:
            newcomm = MPI.Comm.fromint(cint)
            self.assertEqual(newcomm, intercomm)
            self.assertIs(type(newcomm), MPI.Intercomm)
        fint = intercomm.py2f()
        if fint != -1:
            newcomm = MPI.Comm.f2py(fint)
            self.assertEqual(newcomm, intercomm)
            self.assertIs(type(newcomm), MPI.Intercomm)

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
            Create_from_groups = MPI.Intercomm.Create_from_groups
            intercomm = Create_from_groups(lgroup, 0, rgroup, 0)
        except NotImplementedError:
            self.assertLess(MPI.Get_version(), (4, 0))
            self.skipTest('mpi-comm-create_from_group')
        except MPI.Exception as exc:
            UNSUPPORTED = MPI.ERR_UNSUPPORTED_OPERATION
            if exc.Get_error_class() != UNSUPPORTED:
                raise
        else:
            ccmp = MPI.Comm.Compare(self.INTERCOMM, intercomm)
            intercomm.Free()
            self.assertEqual(ccmp, MPI.CONGRUENT)
        finally:
            lgroup.Free()
            rgroup.Free()

    def testSplit(self):
        base = self.INTERCOMM
        comm = base.Split(42, 42)
        self.assertEqual(comm.Get_rank(), base.Get_rank())
        self.assertEqual(comm.Get_size(), base.Get_size())
        self.assertEqual(comm.Get_remote_size(), base.Get_remote_size())
        comm.Free()
        color = base.Get_rank()
        comm = base.Split(color, 42)
        if comm != MPI.COMM_NULL:
            self.assertEqual(comm.Get_rank(), 0)
            self.assertEqual(comm.Get_size(), 1)
            self.assertEqual(comm.Get_remote_size(), 1)
            comm.Free()

    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('openmpi(<5.0.0)')
    @unittest.skipMPI('mpich(<4.2.0)', ch3_nemesis())
    @unittest.skipMPI('mvapich(<3.0.0)', MPI.COMM_WORLD.Get_size() > 2)
    def testSplitTypeShared(self):
        try:
            comm = self.INTERCOMM.Split_type(MPI.COMM_TYPE_SHARED)
        except NotImplementedError:
            self.skipTest('mpi-comm-split_type')
        if comm != MPI.COMM_NULL:
            comm.Free()
        comm = self.INTERCOMM.Split_type(MPI.UNDEFINED)
        self.assertEqual(comm, MPI.COMM_NULL)

    def testPyProps(self):
        comm = self.INTERCOMM
        #
        self.assertEqual(comm.rank, comm.Get_rank())
        self.assertEqual(comm.size, comm.Get_size())
        self.assertEqual(comm.remote_size, comm.Get_remote_size())
        #
        group = comm.remote_group
        self.assertEqual(type(group), MPI.Group)
        group.Free()
        #
        info = comm.info
        self.assertEqual(type(info), MPI.Info)
        info.Free()
        #
        self.assertTrue(comm.is_inter)
        self.assertFalse(comm.is_intra)


class TestIntercomm(BaseTestIntercomm, unittest.TestCase):
    BASECOMM = MPI.COMM_WORLD

class TestIntercommDup(TestIntercomm):
    def setUp(self):
        self.BASECOMM = self.BASECOMM.Dup()
        super().setUp()
    def tearDown(self):
        self.BASECOMM.Free()
        super().tearDown()

class TestIntercommDupDup(TestIntercomm):
    def setUp(self):
        super().setUp()
        INTERCOMM = self.INTERCOMM
        self.INTERCOMM = self.INTERCOMM.Dup()
        INTERCOMM.Free()


@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
class TestIntercommCreateFromGroups(unittest.TestCase):

    @unittest.skipMPI('openmpi', MPI.COMM_WORLD.Get_size() > 2)
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
            self.assertLess(MPI.Get_version(), (4, 0))
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
            self.assertLess(MPI.Get_version(), (4, 0))
            self.skipTest('mpi-intercomm-create_from_groups')


if __name__ == '__main__':
    unittest.main()
