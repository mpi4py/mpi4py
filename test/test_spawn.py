from mpi4py import MPI
import mpiunittest as unittest
import sys, os, mpi4py

MPI4PYPATH = os.path.abspath(os.path.dirname(mpi4py.__path__[0]))

CHILDSCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'spawn_child.py')
    )

HAVE_MPE = 'MPE_LOGFILE_PREFIX' in os.environ
HAVE_VT  = 'VT_FILE_PREFIX' in os.environ

def childscript():
    from tempfile import mkstemp
    from textwrap import dedent
    fd, script = mkstemp(suffix='.py', prefix="mpi4py-")
    os.close(fd)
    with open(script, "w") as f:
        f.write(dedent("""\
        #!%(python)s
        import sys; sys.path.insert(0, "%(path)s")
        import mpi4py
        if %(mpe)s: mpi4py.profile('mpe', logfile="%(logfile)s")
        if %(vt)s:  mpi4py.profile('vt',  logfile="%(logfile)s")
        from mpi4py import MPI
        parent = MPI.Comm.Get_parent()
        parent.Barrier()
        parent.Disconnect()
        assert parent == MPI.COMM_NULL
        parent = MPI.Comm.Get_parent()
        assert parent == MPI.COMM_NULL
        """ % dict(python=sys.executable, path=MPI4PYPATH,
                   mpe=HAVE_MPE, vt=HAVE_VT,
                   logfile="runtests-mpi4py-child")))
    os.chmod(script, int("770", 8))
    return script

def appnum():
    if MPI.APPNUM == MPI.KEYVAL_INVALID: return None
    return MPI.COMM_WORLD.Get_attr(MPI.APPNUM)

@unittest.skipMPI('MPI(<2.0)')
@unittest.skipMPI('openmpi(<3.0.0)')
@unittest.skipMPI('mpich', appnum() is None)
@unittest.skipMPI('msmpi(<8.1.0)')
@unittest.skipMPI('msmpi', appnum() is None)
@unittest.skipMPI('MVAPICH2')
@unittest.skipMPI('MPICH2')
@unittest.skipMPI('MPICH1')
@unittest.skipMPI('PlatformMPI')
class BaseTestSpawn(object):

    COMM = MPI.COMM_NULL
    COMMAND = sys.executable
    ARGS = [CHILDSCRIPT, MPI4PYPATH,
            "mpe" if HAVE_MPE else
            "vt"  if HAVE_VT  else ""]
    MAXPROCS = 1
    INFO = MPI.INFO_NULL
    ROOT = 0

    def testCommSpawn(self):
        self.COMM.Barrier()
        child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT)
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
        child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT,
                                errcodes=errcodes)
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(len(errcodes), self.MAXPROCS)
        for errcode in errcodes:
            self.assertEqual(errcode, MPI.SUCCESS)

    @unittest.skipMPI('msmpi')
    def testArgsOnlyAtRoot(self):
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                    info=self.INFO, root=self.ROOT)
        else:
            child = self.COMM.Spawn(None, None, -1,
                                    info=MPI.INFO_NULL, root=self.ROOT)
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
        child = self.COMM.Spawn(script, None, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT)
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            os.remove(script)
        self.COMM.Barrier()

    def testCommSpawnMultiple(self):
        self.COMM.Barrier()
        count = 2 + (self.COMM.Get_size() == 0)
        COMMAND = [self.COMMAND] * count
        ARGS = [self.ARGS] * len(COMMAND)
        MAXPROCS = [self.MAXPROCS] * len(COMMAND)
        INFO = [self.INFO] * len(COMMAND)
        child = self.COMM.Spawn_multiple(
            COMMAND, ARGS, MAXPROCS,
            info=INFO, root=self.ROOT)
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, sum(MAXPROCS))

    def testCommSpawnMultipleDefaults1(self):
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

    def testCommSpawnMultipleDefaults2(self):
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
    def testErrcodesMultiple(self):
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
            errcodes=errcodelist)
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        self.assertEqual(len(errcodelist), len(COMMAND))
        for i, errcodes in enumerate(errcodelist):
            self.assertEqual(len(errcodes), MAXPROCS[i])
            for errcode in errcodes:
                self.assertEqual(errcode, MPI.SUCCESS)

    @unittest.skipMPI('msmpi')
    def testArgsOnlyAtRootMultiple(self):
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            count = 2 + (self.COMM.Get_size() == 0)
            COMMAND = [self.COMMAND] * count
            ARGS = [self.ARGS] * len(COMMAND)
            MAXPROCS = list(range(1, len(COMMAND)+1))
            INFO = [MPI.INFO_NULL] * len(COMMAND)
            child = self.COMM.Spawn_multiple(
                COMMAND, ARGS, MAXPROCS,
                info=INFO, root=self.ROOT)
        else:
            child = self.COMM.Spawn_multiple(
                None, None, -1,
                info=MPI.INFO_NULL, root=self.ROOT)
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()

    @unittest.skipIf(os.name != 'posix', 'posix')
    def testNoArgsMultiple(self):
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
        child = self.COMM.Spawn_multiple(COMMAND, None, MAXPROCS,
                                         info=INFO, root=self.ROOT)
        child.Barrier()
        child.Disconnect()
        self.COMM.Barrier()
        if self.COMM.Get_rank() == self.ROOT:
            os.remove(script)
        self.COMM.Barrier()

class TestSpawnSelf(BaseTestSpawn, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestSpawnWorld(BaseTestSpawn, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestSpawnSelfMany(BaseTestSpawn, unittest.TestCase):
    COMM = MPI.COMM_SELF
    MAXPROCS = MPI.COMM_WORLD.Get_size()

class TestSpawnWorldMany(BaseTestSpawn, unittest.TestCase):
    COMM = MPI.COMM_WORLD
    MAXPROCS = MPI.COMM_WORLD.Get_size()


if __name__ == '__main__':
    unittest.main()
