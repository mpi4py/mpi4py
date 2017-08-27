import sys
try:
    import threading
    HAVE_THREADING = True
except ImportError:
    import dummy_threading as threading
    HAVE_THREADING = False

Thread = threading.Thread
try:
    current_thread = threading.current_thread # Py 3.X
except AttributeError:
    current_thread = threading.currentThread  # Py 2.X

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

    REQUIRED = MPI.THREAD_SERIALIZED

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

    def testIsThreadMain(self, main=True):
        try:
            flag = MPI.Is_thread_main()
        except NotImplementedError:
            self.skipTest('mpi-is_thread_main')
        self.assertEqual(flag, main)
        if VERBOSE:
            thread = current_thread()
            name = thread.getName()
            log = lambda m: sys.stderr.write(m+'\n')
            log("%s: MPI.Is_thread_main() -> %s" % (name, flag))

    @unittest.skipIf(pypy3_lt_50, "pypy3(<5.0)")
    def testIsThreadMainInThread(self):
        try:
            provided = MPI.Query_thread()
        except NotImplementedError:
            self.skipTest('mpi-query_thread')
        if provided < self.REQUIRED:
            return
        T = []
        for i in range(5):
            t = Thread(target=self.testIsThreadMain,
                       args = (not HAVE_THREADING,))
            T.append(t)
        if provided == MPI.THREAD_SERIALIZED:
            for t in T:
                t.start()
                t.join()
        elif provided == MPI.THREAD_MULTIPLE:
            for t in T:
                t.start()
            for t in T:
                t.join()


name, version = MPI.get_vendor()
if name == 'Open MPI':
    TestMPIThreads.REQUIRED = MPI.THREAD_MULTIPLE
if name == 'LAM/MPI':
    TestMPIThreads.REQUIRED = MPI.THREAD_MULTIPLE


if __name__ == '__main__':
    unittest.main()
