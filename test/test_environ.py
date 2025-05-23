import os

import mpitestutil as testutil
import mpiunittest as unittest

from mpi4py import MPI


class TestEnviron(unittest.TestCase):
    #
    def testIsInitialized(self):
        flag = MPI.Is_initialized()
        self.assertIs(type(flag), bool)
        self.assertTrue(flag)

    def testIsFinalized(self):
        flag = MPI.Is_finalized()
        self.assertIs(type(flag), bool)
        self.assertFalse(flag)

    def testGetVersion(self):
        version = MPI.Get_version()
        self.assertEqual(len(version), 2)
        major, minor = version
        self.assertIs(type(major), int)
        self.assertIs(type(minor), int)
        self.assertGreaterEqual(major, 1)
        self.assertGreaterEqual(minor, 0)

    def testGetLibraryVersion(self):
        version = MPI.Get_library_version()
        self.assertIsInstance(version, str)
        self.assertGreater(len(version), 0)

    def testGetProcessorName(self):
        procname = MPI.Get_processor_name()
        self.assertIsInstance(procname, str)

    def testGetHWResourceInfo(self):
        with self.catchNotImplementedError(4, 1):
            info = MPI.Get_hw_resource_info()
            self.assertIsInstance(info, MPI.Info)

    def testWTime(self):
        time1 = MPI.Wtime()
        self.assertIs(type(time1), float)
        time2 = MPI.Wtime()
        self.assertIs(type(time2), float)
        self.assertGreaterEqual(time2, time1)

    @unittest.skipMPI("impi", os.name == "nt")
    def testWTick(self):
        tick = MPI.Wtick()
        self.assertIs(type(tick), float)
        self.assertGreater(tick, 0.0)

    def testPControl(self):
        for level in (2, 1, 0):
            MPI.Pcontrol(level)
        MPI.Pcontrol(1)


class TestWorldAttrs(unittest.TestCase):
    #
    def testWTimeIsGlobal(self):
        wtg = MPI.COMM_WORLD.Get_attr(MPI.WTIME_IS_GLOBAL)
        if wtg is not None:
            self.assertIn(wtg, (True, False))

    def testIOProcessor(self):
        size = MPI.COMM_WORLD.Get_size()
        vals = list(range(size))
        vals += [MPI.UNDEFINED, MPI.ANY_SOURCE, MPI.PROC_NULL]
        ioproc = MPI.COMM_WORLD.Get_attr(MPI.IO)
        if ioproc is not None:
            self.assertIn(ioproc, vals)

    @unittest.skipIf(MPI.APPNUM == MPI.KEYVAL_INVALID, "mpi-appnum")
    def testAppNum(self):
        appnum = MPI.COMM_WORLD.Get_attr(MPI.APPNUM)
        if appnum is not None:
            self.assertTrue(appnum == MPI.UNDEFINED or appnum >= 0)

    @unittest.skipMPI("mpich(<4.1.0)", not testutil.has_mpi_appnum())
    @unittest.skipMPI("mvapich", not testutil.has_mpi_appnum())
    @unittest.skipMPI("MPICH2", not testutil.has_mpi_appnum())
    @unittest.skipIf(
        MPI.UNIVERSE_SIZE == MPI.KEYVAL_INVALID, "mpi-universe-size"
    )
    def testUniverseSize(self):
        univsz = MPI.COMM_WORLD.Get_attr(MPI.UNIVERSE_SIZE)
        if univsz is not None:
            self.assertTrue(univsz == MPI.UNDEFINED or univsz >= 0)

    @unittest.skipIf(
        MPI.LASTUSEDCODE == MPI.KEYVAL_INVALID, "mpi-lastusedcode"
    )
    def testLastUsedCode(self):
        lastuc = MPI.COMM_WORLD.Get_attr(MPI.LASTUSEDCODE)
        self.assertGreaterEqual(lastuc, 0)


if __name__ == "__main__":
    unittest.main()
