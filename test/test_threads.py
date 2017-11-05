import sys
try:
    import threading
    HAVE_THREADING = True
except ImportError:
    import dummy_threading as threading
    HAVE_THREADING = False

VERBOSE = False
#VERBOSE = True

import mpi4py.rc
mpi4py.rc.thread_level = 'multiple'
from mpi4py import MPI
import mpiunittest as unittest

pypy3_lt_50 = (hasattr(sys, 'pypy_version_info') and
               sys.version_info[0] == 3 and
               sys.pypy_version_info < (5, 0))

class TestMPIThreads(unittest.TestCase):

    def testThreadLevels(self):
        levels = [MPI.THREAD_SINGLE,
                  MPI.THREAD_FUNNELED,
                  MPI.THREAD_SERIALIZED,
                  MPI.THREAD_MULTIPLE]
        for i in range(len(levels)-1):
            self.assertTrue(levels[i] < levels[i+1])
        try:
            provided = MPI.Query_thread()
            self.assertTrue(provided in levels)
        except NotImplementedError:
            self.skipTest('mpi-query_thread')

    def testIsThreadMain(self):
        try:
            flag = MPI.Is_thread_main()
        except NotImplementedError:
            self.skipTest('mpi-is_thread_main')
        name = threading.current_thread().name
        main = (name == 'MainThread') or not HAVE_THREADING
        self.assertEqual(flag, main)
        if VERBOSE:
            log = lambda m: sys.stderr.write(m+'\n')
            log("%s: MPI.Is_thread_main() -> %s" % (name, flag))

    @unittest.skipIf(pypy3_lt_50, 'pypy3(<5.0)')
    def testIsThreadMainInThread(self):
        try:
            provided = MPI.Query_thread()
        except NotImplementedError:
            self.skipTest('mpi-query_thread')
        self.testIsThreadMain()
        T = [threading.Thread(target=self.testIsThreadMain) for _ in range(5)]
        if provided == MPI.THREAD_MULTIPLE:
            for t in T:
                t.start()
            for t in T:
                t.join()
        elif provided == MPI.THREAD_SERIALIZED:
            for t in T:
                t.start()
                t.join()
        else:
            self.skipTest('mpi-thread_level')


if __name__ == '__main__':
    unittest.main()
