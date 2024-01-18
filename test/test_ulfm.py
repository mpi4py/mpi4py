from mpi4py import MPI
import mpiunittest as unittest
import warnings
import struct


def mpi_threads():
    return MPI.Query_thread() > MPI.THREAD_SINGLE


@unittest.skipMPI('msmpi')
@unittest.skipMPI('mvapich')
@unittest.skipMPI('intelmpi')
class BaseTestULFM:

    COMM = MPI.COMM_NULL

    def setUp(self):
        self.COMM = self.COMM.Dup()
        self.COMM.Set_errhandler(MPI.ERRORS_RETURN)

    def tearDown(self):
        self.COMM.Free()
        del self.COMM

    def testIsRevoked(self):
        comm = self.COMM
        try:
            self.assertFalse(comm.Is_revoked())
        except NotImplementedError:
            pass

    def testRevoke(self):
        comm = self.COMM
        is_intra = comm.Is_intra()
        try:
            comm.Revoke()
        except NotImplementedError:
            self.skipTest('mpi-comm_revoke')
        try:
            self.assertTrue(comm.Is_revoked())
        except NotImplementedError:
            pass
        #
        try:
            comm.Barrier()
        except MPI.Exception as exc:
            code = exc.Get_error_class()
        else:
            code = MPI.SUCCESS
        self.assertEqual(code, MPI.ERR_REVOKED)
        #
        try:
            comm.Send([None, 0, MPI.BYTE], MPI.PROC_NULL)
        except MPI.Exception as exc:
            code = exc.Get_error_class()
        else:
            code = MPI.SUCCESS
        self.assertEqual(code, MPI.ERR_REVOKED)
        #
        try:
            comm.Recv([None, 0, MPI.BYTE], MPI.PROC_NULL)
        except MPI.Exception as exc:
            code = exc.Get_error_class()
        else:
            code = MPI.SUCCESS
        self.assertEqual(code, MPI.ERR_REVOKED)

    def testGetFailed(self):
        comm = self.COMM
        group = comm.Get_failed()
        gcmp = MPI.Group.Compare(group, MPI.GROUP_EMPTY)
        group.Free()
        self.assertIn(gcmp, [MPI.IDENT, MPI.CONGRUENT])

    def testAckFailed(self):
        comm = self.COMM
        size = comm.Get_size()
        num_acked = comm.Ack_failed(0)
        self.assertEqual(num_acked, 0)
        num_acked = comm.Ack_failed(size)
        self.assertEqual(num_acked, 0)
        num_acked = comm.Ack_failed()
        self.assertEqual(num_acked, 0)

    def testAgree(self):
        comm = self.COMM
        for i in range(5):
            flag = i
            flag = comm.Agree(flag)
            self.assertEqual(flag, i)

    @unittest.skipMPI('MVAPICH2', MPI.COMM_WORLD.Get_size() > 3)
    def testIAgree(self):
        comm = self.COMM
        with self.assertRaises(TypeError):
            comm.Iagree(0)
        with self.assertRaises(ValueError):
            comm.Iagree(bytearray(8))
        ibuf = MPI.buffer.allocate(struct.calcsize('i'))
        flag = memoryview(ibuf).cast('i')
        for i in range(5):
            flag[0] = i
            request = comm.Iagree(flag)
            request.Wait()
            self.assertEqual(flag[0], i)
        size = comm.Get_size()
        if comm.Is_intra() and size > 1:
            for root in range(size):
                rank = comm.Get_rank()
                comm.Barrier()
                if rank == root:
                    ival = int('1011', base=2)
                    flag[0] = ival
                    request = comm.Iagree(flag)
                    self.assertFalse(request.Test())
                    self.assertEqual(flag[0], ival)
                    comm.Barrier()
                else:
                    ival = int('1101', base=2)
                    flag[0] = ival
                    comm.Barrier()
                    self.assertEqual(flag[0], ival)
                    request = comm.Iagree(flag)
                request.Wait()
                ival = int('1001', base=2)
                self.assertEqual(flag[0], ival)

    def testShrink(self):
        comm = self.COMM
        shrink = comm.Shrink()
        self.assertEqual(comm.Get_size(), shrink.Get_size())
        self.assertEqual(comm.Get_rank(), shrink.Get_rank())
        if shrink.Is_inter():
            self.assertEqual(comm.Get_remote_size(),
                             shrink.Get_remote_size())
        shrink.Free()

    def testIShrink(self):
        comm = self.COMM
        shrink, request = comm.Ishrink()
        self.assertTrue(request)
        request.Wait()
        self.assertFalse(request)
        self.assertEqual(comm.Get_size(), shrink.Get_size())
        self.assertEqual(comm.Get_rank(), shrink.Get_rank())
        if shrink.Is_inter():
            self.assertEqual(comm.Get_remote_size(),
                             shrink.Get_remote_size())
        shrink.Free()

    def testLegacyAck(self):
        comm = self.COMM
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            comm._Failure_ack()

    def testLegacyGetAcked(self):
        comm = self.COMM
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            group = comm._Failure_get_acked()
        gcmp = MPI.Group.Compare(group, MPI.GROUP_EMPTY)
        group.Free()
        self.assertIn(gcmp, [MPI.IDENT, MPI.CONGRUENT])


class TestULFMSelf(BaseTestULFM, unittest.TestCase):
    COMM = MPI.COMM_SELF


class TestULFMWorld(BaseTestULFM, unittest.TestCase):
    COMM = MPI.COMM_WORLD

    @unittest.skipMPI('openmpi(>=5.0.0)', mpi_threads())  # TODO
    def testIShrink(self):
        super().testIShrink()


@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
class TestULFMInter(BaseTestULFM, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        BASECOMM = MPI.COMM_WORLD
        size = BASECOMM.Get_size()
        rank = BASECOMM.Get_rank()
        if rank < size // 2 :
            COLOR = 0
            LOCAL_LEADER = 0
            REMOTE_LEADER = size // 2
        else:
            COLOR = 1
            LOCAL_LEADER = 0
            REMOTE_LEADER = 0
        INTRACOMM = BASECOMM.Split(COLOR, key=0)
        INTERCOMM = MPI.Intracomm.Create_intercomm(
            INTRACOMM, LOCAL_LEADER,
            BASECOMM, REMOTE_LEADER,
        )
        INTRACOMM.Free()
        cls.COMM = INTERCOMM
        cls.COMM.Set_errhandler(MPI.ERRORS_RETURN)

    @classmethod
    def tearDownClass(cls):
        cls.COMM.Free()

    @unittest.skipMPI('openmpi(>=5.0.0)')  # TODO
    def testAgree(self):
        super().testAgree()

    @unittest.skipMPI('openmpi(>=5.0.0)')  # TODO
    def testIAgree(self):
        super().testIAgree()

    @unittest.skipMPI('openmpi(>=5.0.0)')  # TODO
    def testShrink(self):
        super().testShrink()

    @unittest.skipMPI('openmpi(>=5.0.0)')  # TODO
    def testIShrink(self):
        super().testIShrink()


if __name__ == '__main__':
    unittest.main()
