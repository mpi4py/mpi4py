from mpi4py import MPI
import mpiunittest as unittest

_basic = [None,
          True, False,
          -7, 0, 7,
          -2**63+1, 2**63-1,
          -2.17, 0.0, 3.14,
          1+2j, 2-3j,
          'mpi4py',
          ]
messages = list(_basic)
messages += [ list(_basic),
              tuple(_basic),
              dict([('k%d' % key, val)
                    for key, val in enumerate(_basic)])
              ]

@unittest.skipIf(MPI.MESSAGE_NULL == MPI.MESSAGE_NO_PROC, 'mpi-message')
class TestMessage(unittest.TestCase):

    def testMessageNull(self):
        null = MPI.MESSAGE_NULL
        self.assertFalse(null)
        null2 = MPI.Message()
        self.assertEqual(null, null2)
        null3 = MPI.Message(null)
        self.assertEqual(null, null3)

    def testMessageNoProc(self):
        #
        noproc = MPI.MESSAGE_NO_PROC
        self.assertTrue(noproc)
        noproc.recv()
        self.assertTrue(noproc)
        noproc.irecv().wait()
        self.assertTrue(noproc)
        #
        noproc2 = MPI.Message(MPI.MESSAGE_NO_PROC)
        self.assertTrue(noproc2)
        self.assertEqual(noproc2, noproc)
        self.assertNotEqual(noproc, MPI.MESSAGE_NULL)
        #
        message = MPI.Message(MPI.MESSAGE_NO_PROC)
        message.recv()
        self.assertEqual(message, MPI.MESSAGE_NULL)
        #
        message = MPI.Message(MPI.MESSAGE_NO_PROC)
        request = message.irecv()
        self.assertEqual(message, MPI.MESSAGE_NULL)
        self.assertNotEqual(request, MPI.REQUEST_NULL)
        request.wait()
        self.assertEqual(request, MPI.REQUEST_NULL)
        #
        comm = MPI.COMM_SELF
        message = comm.mprobe(MPI.PROC_NULL)
        self.assertNotEqual(message, MPI.MESSAGE_NULL)
        self.assertEqual(message, MPI.MESSAGE_NO_PROC)
        noproc = comm.improbe(MPI.PROC_NULL)
        self.assertNotEqual(message, MPI.MESSAGE_NULL)
        self.assertEqual(message, MPI.MESSAGE_NO_PROC)

@unittest.skipIf(MPI.MESSAGE_NULL == MPI.MESSAGE_NO_PROC, 'mpi-message')
class BaseTestP2PMatched(object):

    COMM = MPI.COMM_NULL

    def testIMProbe(self):
        comm = self.COMM.Dup()
        try:
            m = comm.improbe()
            self.assertEqual(m, None)
            m = comm.improbe(MPI.ANY_SOURCE)
            self.assertEqual(m, None)
            m = comm.improbe(MPI.ANY_SOURCE, MPI.ANY_TAG)
            self.assertEqual(m, None)
            status = MPI.Status()
            m = comm.improbe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertEqual(m, None)
            self.assertEqual(status.source, MPI.ANY_SOURCE)
            self.assertEqual(status.tag,    MPI.ANY_TAG)
            self.assertEqual(status.error,  MPI.SUCCESS)
            m = MPI.Message.iprobe(comm)
            self.assertEqual(m, None)
            # Open MPI <= 1.8.4
            s = comm.isend(None, comm.rank, 0)
            r = comm.mprobe(comm.rank, 0).irecv()
            MPI.Request.waitall([s,r])
        finally:
            comm.Free()

    def testProbeRecv(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for smsg in messages:
            if size == 1:
                sr = comm.isend(smsg, 0, 0)
                m = comm.mprobe(0, 0)
                self.assertTrue(isinstance(m, MPI.Message))
                self.assertTrue(m)
                rr = m.irecv()
                self.assertFalse(m)
                self.assertTrue(sr)
                self.assertTrue(rr)
                MPI.Request.Waitall([sr,rr])
                self.assertFalse(sr)
                self.assertFalse(rr)
                #
                r = comm.isend(smsg, 0, 0)
                m = MPI.Message.probe(comm, 0, 0)
                self.assertTrue(isinstance(m, MPI.Message))
                self.assertTrue(m)
                rmsg = m.recv()
                self.assertFalse(m)
                r.wait()
            elif rank == 0:
                comm.send(smsg, 1, 0)
                m = comm.mprobe(1, 0)
                self.assertTrue(m)
                rmsg = m.recv()
                self.assertFalse(m)
                #
                comm.send(smsg, 1, 1)
                m = None
                while not m:
                    m = MPI.Message.iprobe(comm, 1, 1)
                rmsg = m.irecv().wait()
            elif rank == 1:
                m = comm.mprobe(0, 0)
                self.assertTrue(m)
                rmsg = m.recv()
                self.assertFalse(m)
                comm.send(rmsg, 0, 0)
                #
                m = None
                while not m:
                    m = MPI.Message.iprobe(comm, 0, 1)
                rmsg = m.irecv().wait()
                comm.send(smsg, 0, 1)
            else:
                rmsg = smsg

            self.assertEqual(smsg, rmsg)


class TestP2PMatchedSelf(BaseTestP2PMatched, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PMatchedWorld(BaseTestP2PMatched, unittest.TestCase):
    COMM = MPI.COMM_WORLD

@unittest.skipMPI('openmpi(<1.8.5)', MPI.COMM_WORLD.Get_size() > 1)
class TestP2PMatchedSelfDup(TestP2PMatchedSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

@unittest.skipMPI('openmpi(<1.8.5)', MPI.COMM_WORLD.Get_size() > 1)
class TestP2PMatchedWorldDup(TestP2PMatchedWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    unittest.main()
