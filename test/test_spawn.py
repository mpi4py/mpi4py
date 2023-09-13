from mpi4py import MPI
import mpiunittest as unittest
import sys, os, mpi4py

MPI4PYPATH = os.path.abspath(
    os.path.dirname(mpi4py.__path__[0])
)

CHILDSCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'spawn_child.py')
)

def childscript():
    from tempfile import mkstemp
    from textwrap import dedent
    fd, script = mkstemp(suffix='.py', prefix="mpi4py-")
    os.close(fd)
    python = sys.executable
    pypath = MPI4PYPATH
    with open(script, "w") as f:
        f.write(dedent(f"""\
        #!{python}
        import sys; sys.path.insert(0, "{pypath}")
        from mpi4py import MPI
        parent = MPI.Comm.Get_parent()
        parent.Barrier()
        parent.Disconnect()
        assert parent == MPI.COMM_NULL
        parent = MPI.Comm.Get_parent()
        assert parent == MPI.COMM_NULL
        """))
    os.chmod(script, int("770", 8))
    return script

def ch4_ucx():
    return 'ch4:ucx' in MPI.Get_library_version()

def ch4_ofi():
    return 'ch4:ofi' in MPI.Get_library_version()

def appnum():
    if MPI.APPNUM == MPI.KEYVAL_INVALID: return None
    return MPI.COMM_WORLD.Get_attr(MPI.APPNUM)

def badport():
    if MPI.get_vendor()[0] != 'MPICH':
        return False
    try:
        port = MPI.Open_port()
        MPI.Close_port(port)
    except:
        port = ""
    return port == ""

def using_GPU():
    # Once a CUDA context is created, the process cannot be forked.
    # Note: This seems to be a partial fix. Even if we are running cpu-only
    # tests, if MPI is built with CUDA support we can still fail. Unfortunately
    # there is no runtime check for us to detect if it's the case...
    using_cupy = (sys.modules.get('cupy') is not None)
    using_numba = (sys.modules.get('numba') is not None)
    return using_cupy or using_numba

def sequential():
    return MPI.COMM_WORLD.Get_size() == 1

def windows():
    return sys.platform == 'win32'

def github_actions():
    return os.environ.get('GITHUB_ACTIONS') == 'true'


@unittest.skipMPI('MPI(<2.0)')
@unittest.skipMPI('openmpi(<3.0.0)')
@unittest.skipMPI('openmpi(==4.0.0)')
@unittest.skipMPI('openmpi(==4.0.1)', sys.platform=='darwin')
@unittest.skipMPI('openmpi(==4.0.2)', sys.platform=='darwin')
@unittest.skipMPI('openmpi(>=4.1.0,<4.2.0)', github_actions())
@unittest.skipMPI('mpich(<4.1.0)', appnum() is None)
@unittest.skipMPI('mpich', badport())
@unittest.skipMPI('msmpi(<8.1.0)')
@unittest.skipMPI('msmpi', appnum() is None)
@unittest.skipMPI('mvapich', appnum() is None)
@unittest.skipMPI('mvapich', badport())
@unittest.skipMPI('MPICH2')
@unittest.skipMPI('MVAPICH2')
@unittest.skipMPI('MPICH1')
@unittest.skipIf(using_GPU(), 'using CUDA')
class BaseTestSpawn:

    COMM = MPI.COMM_NULL
    COMMAND = sys.executable
    ARGS = [CHILDSCRIPT, MPI4PYPATH]
    MAXPROCS = 1
    INFO = MPI.INFO_NULL
    ROOT = 0


class BaseTestSpawnSingle(BaseTestSpawn):

    def testCommSpawn(self):
        self.COMM.Barrier()
        child = self.COMM.Spawn(
            self.COMMAND, self.ARGS, self.MAXPROCS,
            info=self.INFO, root=self.ROOT,
        )
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, self.MAXPROCS)

    @unittest.skipMPI('msmpi')
    def testErrcodes(self):
        self.COMM.Barrier()
        errcodes = []
        child = self.COMM.Spawn(
            self.COMMAND, self.ARGS, self.MAXPROCS,
            info=self.INFO, root=self.ROOT,
            errcodes=errcodes,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(len(errcodes), self.MAXPROCS)
        for errcode in errcodes:
            self.assertEqual(errcode, MPI.SUCCESS)

    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('mpich(==3.4.1)', ch4_ofi())
    def testArgsOnlyAtRoot(self):
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            child = self.COMM.Spawn(
                self.COMMAND, self.ARGS, self.MAXPROCS,
                info=self.INFO, root=self.ROOT,
            )
        else:
            child = self.COMM.Spawn(
                None, None, -1,
                info=MPI.INFO_NULL, root=self.ROOT,
            )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()

    @unittest.skipIf(os.name != 'posix', 'posix')
    def testNoArgs(self):
        self.COMM.Barrier()
        script = None
        if self.COMM.Get_rank() == self.ROOT:
            script = childscript()
        self.COMM.Barrier()
        script = self.COMM.bcast(script, root=self.ROOT)
        child = self.COMM.Spawn(
            script, None, self.MAXPROCS,
            info=self.INFO, root=self.ROOT,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            os.remove(script)
        self.COMM.Barrier()


class BaseTestSpawnMultiple(BaseTestSpawn):

    def testCommSpawn(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS] * len(COMMAND)
        MAXPROCS = [self.MAXPROCS] * len(COMMAND)
        INFO = [self.INFO] * len(COMMAND)
        child = self.COMM.Spawn_multiple(
            COMMAND, ARGS, MAXPROCS,
            info=INFO, root=self.ROOT,
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

    @unittest.skipMPI('msmpi')
    def testErrcodes(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS]*len(COMMAND)
        MAXPROCS = list(range(1, len(COMMAND)+1))
        INFO = MPI.INFO_NULL
        errcodelist = []
        child = self.COMM.Spawn_multiple(
            COMMAND, ARGS, MAXPROCS,
            info=INFO, root=self.ROOT,
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

    @unittest.skipMPI('msmpi')
    def testArgsOnlyAtRoot(self):
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            count = 2 + (self.COMM.Get_size() == 0)
            COMMAND = [self.COMMAND] * count
            ARGS = [self.ARGS] * len(COMMAND)
            MAXPROCS = list(range(1, len(COMMAND)+1))
            INFO = [MPI.INFO_NULL] * len(COMMAND)
            child = self.COMM.Spawn_multiple(
                COMMAND, ARGS, MAXPROCS,
                info=INFO, root=self.ROOT,
            )
        else:
            child = self.COMM.Spawn_multiple(
                None, None, -1,
                info=MPI.INFO_NULL, root=self.ROOT,
            )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()

    @unittest.skipIf(os.name != 'posix', 'posix')
    def testNoArgs(self):
        self.COMM.Barrier()
        script = None
        if self.COMM.Get_rank() == self.ROOT:
            script = childscript()
        self.COMM.Barrier()
        script = self.COMM.bcast(script, root=self.ROOT)
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [script] * count
        MAXPROCS = list(range(1, len(COMMAND)+1))
        INFO = [self.INFO] * len(COMMAND)
        child = self.COMM.Spawn_multiple(
            COMMAND, None, MAXPROCS,
            info=INFO, root=self.ROOT,
        )
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            os.remove(script)
        self.COMM.Barrier()

    def testArgsBad(self):
        if self.COMM.Get_size() > 1: return
        CMDS = [self.COMMAND]
        ARGS = [self.ARGS]
        MAXP = [self.MAXPROCS]
        INFO = [self.INFO]
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS[0], ARGS, MAXP, INFO, root=0)
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS, ARGS*2, MAXP, INFO, root=0)
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS, ARGS[0][0], MAXP*2, INFO, root=0)
        with self.assertRaises(ValueError):
            self.COMM.Spawn_multiple(CMDS, ARGS, MAXP[0], INFO*2, root=0)


class TestSpawnSingleSelf(BaseTestSpawnSingle, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnSingleWorld(BaseTestSpawnSingle, unittest.TestCase):
    COMM = MPI.COMM_WORLD

@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnSingleSelfMany(TestSpawnSingleSelf):
    MAXPROCS = MPI.COMM_WORLD.Get_size()

@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnSingleWorldMany(TestSpawnSingleWorld):
    MAXPROCS = MPI.COMM_WORLD.Get_size()


@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnMultipleSelf(BaseTestSpawnMultiple, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnMultipleWorld(BaseTestSpawnMultiple, unittest.TestCase):
    COMM = MPI.COMM_WORLD

@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnMultipleSelfMany(TestSpawnMultipleSelf):
    MAXPROCS = MPI.COMM_WORLD.Get_size()

@unittest.skipMPI('intelmpi', windows() and not sequential())
class TestSpawnMultipleWorldMany(TestSpawnMultipleWorld):
    MAXPROCS = MPI.COMM_WORLD.Get_size()


if __name__ == '__main__':
    unittest.main()
