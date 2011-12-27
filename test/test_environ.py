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
        self.assertTrue(isinstance(procname, str))

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

    def testWTimeIsGlobal(self):
        wtg = MPI.COMM_WORLD.Get_attr(MPI.WTIME_IS_GLOBAL)
        if wtg is not None:
            self.assertTrue(wtg in (True, False))

    def testWTimeIsGlobal(self):
        wtg = MPI.COMM_WORLD.Get_attr(MPI.WTIME_IS_GLOBAL)
        if wtg is not None:
            self.assertTrue(wtg in (True, False))

    def testHostPorcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size)) + [MPI.PROC_NULL]
        hostproc = MPI.COMM_WORLD.Get_attr(MPI.HOST)
        if hostproc is not None:
            self.assertTrue(hostproc in vals)

    def testIOProcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size)) + [MPI.UNDEFINED,
                                    MPI.ANY_SOURCE,
                                    MPI.PROC_NULL]
        ioproc = MPI.COMM_WORLD.Get_attr(MPI.IO)
        if ioproc is not None:
            self.assertTrue(ioproc in vals)

    def testAppNum(self):
        if MPI.APPNUM == MPI.KEYVAL_INVALID: return
        appnum = MPI.COMM_WORLD.Get_attr(MPI.APPNUM)
        if appnum is not None:
            self.assertTrue(appnum == MPI.UNDEFINED or appnum >= 0)

    def testUniverseSize(self):
        if MPI.UNIVERSE_SIZE == MPI.KEYVAL_INVALID: return
        univsz = MPI.COMM_WORLD.Get_attr(MPI.UNIVERSE_SIZE)
        if univsz is not None:
            self.assertTrue(univsz == MPI.UNDEFINED or univsz >= 0)

    def testLastUsedCode(self):
        if MPI.LASTUSEDCODE == MPI.KEYVAL_INVALID: return
        lastuc = MPI.COMM_WORLD.Get_attr(MPI.LASTUSEDCODE)
        self.assertTrue(lastuc >= 0)

_name, _version = MPI.get_vendor()
if (_name == 'MPICH2' and
    _version > (1, 2)):
    # Up to mpich2-1.3.1 when running under Hydra process manager,
    # getting the universe size fails for the singleton init case
    if MPI.COMM_WORLD.Get_attr(MPI.APPNUM) is None:
        del TestWorldAttrs.testUniverseSize

if __name__ == '__main__':
    unittest.main()
