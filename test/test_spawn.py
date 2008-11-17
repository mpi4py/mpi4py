import sys, os, mpi4py
from mpi4py import MPI
import mpiunittest as unittest

PYTHONPATH = os.environ.get('PYTHONPATH','').split(os.path.pathsep)
MPI4PYPATH = os.path.split(mpi4py.__path__[0])[0]
PYTHONPATH.insert(0, MPI4PYPATH)

class TestSpawnBase(object):

    COMM = MPI.COMM_NULL
    COMMAND = sys.executable
    ARGS = ['-c', ';'.join([
        'import sys; sys.path[:] = %s + sys.path' % repr(PYTHONPATH),
        'from mpi4py import MPI',
        'parent = MPI.Comm.Get_parent()',
        'parent.Barrier()',
        'parent.Disconnect()',
        'assert parent == MPI.COMM_NULL',
        'parent = MPI.Comm.Get_parent()',
        'assert parent == MPI.COMM_NULL',
        ])]

    MAXPROCS = 1
    INFO = MPI.INFO_NULL
    ROOT = 0

    def testCommSpawn(self):
        child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT)
        local_size = child.Get_size()
        remote_size = child.Get_remote_size()
        child.Barrier()
        child.Disconnect()
        self.assertEqual(local_size, self.COMM.Get_size())
        self.assertEqual(remote_size, self.MAXPROCS)

    def testReturnedErrcodes(self):
        errcodes = []
        child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                info=self.INFO, root=self.ROOT,
                                errcodes=errcodes)
        child.Barrier()
        child.Disconnect()
        rank = self.COMM.Get_rank()
        if rank == self.ROOT:
            self.assertEqual(len(errcodes), self.MAXPROCS)
            for errcode in errcodes:
                self.assertEqual(errcode, MPI.SUCCESS)
        else:
            self.assertEqual(errcodes, [])

    def testArgsOnlyAtRoot(self):
        rank = self.COMM.Get_rank()
        if rank == self.ROOT:
            child = self.COMM.Spawn(self.COMMAND, self.ARGS, self.MAXPROCS,
                                        info=self.INFO, root=self.ROOT)
        else:
            child = self.COMM.Spawn('', None, -1,
                                    info=None, root=self.ROOT)
        child.Barrier()
        child.Disconnect()

class TestSpawnSelf(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestSpawnWorld(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestSpawnSelfMany(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_SELF
    MAXPROCS = MPI.COMM_WORLD.Get_size()

class TestSpawnWorldMany(TestSpawnBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD
    MAXPROCS = MPI.COMM_WORLD.Get_size()



_SKIP_TEST = False
_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if MPI.Query_thread() > MPI.THREAD_SINGLE:
        _SKIP_TEST = True
elif _name == 'MPICH2':
    if _version < (1,0,6):
        _appnum = getattr(MPI, 'APPNUM', MPI.UNDEFINED)
        if _appnum == MPI.UNDEFINED:
            _SKIP_TEST = True
elif MPI.Get_version() < (2,0):
    _SKIP_TEST = True

if _SKIP_TEST:
    del TestSpawnBase
    del TestSpawnSelf
    del TestSpawnWorld
    del TestSpawnSelfMany
    del TestSpawnWorldMany
elif _name == 'MPICH2':
    del TestSpawnBase.testReturnedErrcodes



if __name__ == '__main__':
    unittest.main()
