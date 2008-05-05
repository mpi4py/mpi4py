from mpi4py import MPI
import mpiunittest as unittest

class TestEnviron(unittest.TestCase):

    def testIsInitialized(self):
        flag = MPI.Is_initialized()
        self.assertTrue(type(flag) is bool)
        self.assertTrue(flag)

    def testIsFinalized(self):
        flag = MPI.Is_finalized()
        self.assertTrue(type(flag) is bool)
        self.assertFalse(flag)

    def testGetVersion(self):
        version = MPI.Get_version()
        self.assertEqual(len(version), 2)
        major, minor = version
        self.assertTrue(type(major) is int)
        self.assertTrue(major >= 1)
        self.assertTrue(type(minor) is int)
        self.assertTrue(minor >= 0)

    def testGetProcessorName(self):
        procname = MPI.Get_processor_name()
        self.assertTrue(isinstance(procname, type('')))

    def testWTime(self):
        time1 = MPI.Wtime()
        self.assertTrue(type(time1) is float)
        time2 = MPI.Wtime()
        self.assertTrue(type(time2) is float)
        self.assertTrue(time2 >= time1)

    def testWTick(self):
        tick = MPI.Wtick()
        self.assertTrue(type(tick) is float)
        self.assertTrue(tick > 0.0)


class TestWorldAttrs(unittest.TestCase):

    def testHostPorcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size)) + [MPI.PROC_NULL]
        self.assertTrue(MPI.HOST in vals)

    def testIOProcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size)) + [MPI.UNDEFINED,
                                    MPI.ANY_SOURCE,
                                    MPI.PROC_NULL]
        self.assertTrue(MPI.IO in vals)

    def testAppNum(self):
        appnum = MPI.APPNUM
        self.assertTrue(appnum == MPI.UNDEFINED or appnum >= 0)

    def testUniverseSize(self):
        univsz = MPI.UNIVERSE_SIZE
        self.assertTrue(univsz == MPI.UNDEFINED or univsz >= 0)


del TestWorldAttrs # XXX not implemented


if __name__ == '__main__':
    unittest.main()
