import os
import pathlib
import platform
import sys
import tempfile
import textwrap

import mpitestutil as testutil
import mpiunittest as unittest

import mpi4py
from mpi4py import MPI

MPI4PYPATH = pathlib.Path(mpi4py.__path__[0]).resolve().parent
CHILDSCRIPT = pathlib.Path(__file__).resolve().parent / "spawn_child.py"


def childscript():
    fd, script = tempfile.mkstemp(suffix=".py", prefix="mpi4py-")
    os.close(fd)
    script = pathlib.Path(script)
    python = os.fspath(sys.executable)
    pypath = os.fspath(MPI4PYPATH)
    script.write_text(
        textwrap.dedent(f"""\
        #!{python}
        import sys
        sys.path.insert(0, "{pypath}")
        from mpi4py import MPI
        parent = MPI.Comm.Get_parent()
        parent.Barrier()
        parent.Disconnect()
        assert parent == MPI.COMM_NULL
        parent = MPI.Comm.Get_parent()
        assert parent == MPI.COMM_NULL
        """)
    )
    script.chmod(0o770)
    return script


@unittest.skipIf(testutil.disable_mpi_spawn(), "mpi-spawn")
class BaseTestSpawn:
    #
    COMM = MPI.COMM_NULL
    COMMAND = sys.executable
    ARGS = [os.fspath(CHILDSCRIPT), os.fspath(MPI4PYPATH)]
    MAXPROCS = 1
    INFO = MPI.INFO_NULL
    ROOT = 0


class BaseTestSpawnSingle(BaseTestSpawn):
    #
    def testCommSpawn(self):
        self.COMM.Barrier()
        child = self.COMM.Spawn(
            self.COMMAND,
            self.ARGS,
            self.MAXPROCS,
            info=self.INFO,
            root=self.ROOT,
        )
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, self.MAXPROCS)

    @unittest.skipMPI("msmpi")
    def testErrcodes(self):
        self.COMM.Barrier()
        errcodes = []
        child = self.COMM.Spawn(
            self.COMMAND,
            self.ARGS,
            self.MAXPROCS,
            info=self.INFO,
            root=self.ROOT,
            errcodes=errcodes,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(len(errcodes), self.MAXPROCS)
        for errcode in errcodes:
            self.assertEqual(errcode, MPI.SUCCESS)

    @unittest.skipMPI("mpich(<5.0.0)", platform.machine() == "ppc")
    @unittest.skipMPI("mpich(==3.4.1)")
    @unittest.skipMPI("msmpi")
    def testArgsOnlyAtRoot(self):
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            child = self.COMM.Spawn(
                self.COMMAND,
                self.ARGS,
                self.MAXPROCS,
                info=self.INFO,
                root=self.ROOT,
            )
        else:
            child = self.COMM.Spawn(
                None,
                None,
                -1,
                info=MPI.INFO_NULL,
                root=self.ROOT,
            )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()

    @unittest.skipIf(os.name != "posix", "posix")
    def testNoArgs(self):
        self.COMM.Barrier()
        script = None
        if self.COMM.Get_rank() == self.ROOT:
            script = childscript()
        self.COMM.Barrier()
        script = self.COMM.bcast(script, root=self.ROOT)
        child = self.COMM.Spawn(
            script,
            None,
            self.MAXPROCS,
            info=self.INFO,
            root=self.ROOT,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            script.unlink()
        self.COMM.Barrier()


class BaseTestSpawnMultiple(BaseTestSpawn):
    #
    def testCommSpawn(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS] * len(COMMAND)
        MAXPROCS = [self.MAXPROCS] * len(COMMAND)
        INFO = [self.INFO] * len(COMMAND)
        child = self.COMM.Spawn_multiple(
            COMMAND,
            ARGS,
            MAXPROCS,
            info=INFO,
            root=self.ROOT,
        )
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, sum(MAXPROCS))

    def testCommSpawnDefaults1(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS] * len(COMMAND)
        child = self.COMM.Spawn_multiple(COMMAND, ARGS)
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, len(COMMAND))

    def testCommSpawnDefaults2(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS] * len(COMMAND)
        child = self.COMM.Spawn_multiple(COMMAND, ARGS, 1, MPI.INFO_NULL)
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, len(COMMAND))

    @unittest.skipMPI("msmpi")
    def testErrcodes(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS] * len(COMMAND)
        MAXPROCS = list(range(1, len(COMMAND) + 1))
        INFO = MPI.INFO_NULL
        errcodelist = []
        child = self.COMM.Spawn_multiple(
            COMMAND,
            ARGS,
            MAXPROCS,
            info=INFO,
            root=self.ROOT,
            errcodes=errcodelist,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(len(errcodelist), len(COMMAND))
        for i, errcodes in enumerate(errcodelist):
            self.assertEqual(len(errcodes), MAXPROCS[i])
            for errcode in errcodes:
                self.assertEqual(errcode, MPI.SUCCESS)

    @unittest.skipMPI("msmpi")
    def testArgsOnlyAtRoot(self):
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            count = 2 + (self.COMM.Get_size() == 0)
            COMMAND = [self.COMMAND] * count
            ARGS = [self.ARGS] * len(COMMAND)
            MAXPROCS = list(range(1, len(COMMAND) + 1))
            INFO = [MPI.INFO_NULL] * len(COMMAND)
            child = self.COMM.Spawn_multiple(
                COMMAND,
                ARGS,
                MAXPROCS,
                info=INFO,
                root=self.ROOT,
            )
        else:
            child = self.COMM.Spawn_multiple(
                None,
                None,
                -1,
                info=MPI.INFO_NULL,
                root=self.ROOT,
            )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()

    @unittest.skipIf(os.name != "posix", "posix")
    def testNoArgs(self):
        self.COMM.Barrier()
        script = None
        if self.COMM.Get_rank() == self.ROOT:
            script = childscript()
        self.COMM.Barrier()
        script = self.COMM.bcast(script, root=self.ROOT)
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [script] * count
        MAXPROCS = list(range(1, len(COMMAND) + 1))
        INFO = [self.INFO] * len(COMMAND)
        child = self.COMM.Spawn_multiple(
            COMMAND,
            None,
            MAXPROCS,
            info=INFO,
            root=self.ROOT,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            script.unlink()
        self.COMM.Barrier()

    def testArgsBad(self):
        if self.COMM.Get_size() > 1:
            return
        CMDS = [self.COMMAND]
        ARGS = [self.ARGS]
        MAXP = [self.MAXPROCS]
        INFO = [self.INFO]
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS[0], ARGS, MAXP, INFO, root=0)
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS, ARGS * 2, MAXP, INFO, root=0)
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS, ARGS[0][0], MAXP * 2, INFO, root=0)
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS, ARGS, MAXP[0], INFO * 2, root=0)


class TestSpawnSingleSelf(BaseTestSpawnSingle, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestSpawnSingleWorld(BaseTestSpawnSingle, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestSpawnSingleSelfMany(TestSpawnSingleSelf):
    #
    MAXPROCS = MPI.COMM_WORLD.Get_size()


class TestSpawnSingleWorldMany(TestSpawnSingleWorld):
    #
    MAXPROCS = MPI.COMM_WORLD.Get_size()


class TestSpawnMultipleSelf(BaseTestSpawnMultiple, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestSpawnMultipleWorld(BaseTestSpawnMultiple, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestSpawnMultipleSelfMany(TestSpawnMultipleSelf):
    #
    MAXPROCS = MPI.COMM_WORLD.Get_size()


class TestSpawnMultipleWorldMany(TestSpawnMultipleWorld):
    #
    MAXPROCS = MPI.COMM_WORLD.Get_size()


if __name__ == "__main__":
    unittest.main()
