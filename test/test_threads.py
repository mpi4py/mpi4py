try:
    import threading as _threading
    _HAS_THREADING = True
except ImportError:
    import dummy_threading as _threading
    _HAS_THREADING = False

Thread = _threading.Thread
try:
    current_thread = _threading.current_thread # Py 3.X
except AttributeError:
    current_thread = _threading.currentThread  # Py 2.X

import mpi4py.rc
mpi4py.rc.thread_level = 'multiple'
from mpi4py import MPI
import mpiunittest as unittest


class TestMPIThreads(unittest.TestCase):

    REQUIRED = MPI.THREAD_SERIALIZED

    def testThreadLevels(self):
        levels = [MPI.THREAD_SINGLE,
                  MPI.THREAD_FUNNELED,
                  MPI.THREAD_SERIALIZED,
                  MPI.THREAD_MULTIPLE]
        if None in levels: return
        for i in range(len(levels)-1):
            self.assertTrue(levels[i] < levels[i+1])
        try:
            provided = MPI.Query_thread()
            self.assertTrue(provided in levels)
        except NotImplementedError:
            pass

    def _test_is(self, main=False):
        try:
            flag = MPI.Is_thread_main()
        except NotImplementedError:
            return
        self.assertEqual(flag, main)
        if _VERBOSE:
            from sys import stderr
            thread = current_thread()
            name = thread.getName()
            log = lambda m: stderr.write(m+'\n')
            log("%s: MPI.Is_thread_main() -> %s" % (name, flag))

    def testIsThreadMain(self):
        self._test_is(main=True)
        try:
            provided = MPI.Query_thread()
        except NotImplementedError:
            return
        if provided < self.REQUIRED:
            return
        T = []
        for i in range(5):
            t = Thread(target=self._test_is,
                       args = (not _HAS_THREADING,))
            T.append(t)
        if provided == MPI.THREAD_MULTIPLE:
            for t in T:
                t.start()
                t.join()
        else:
            for t in T:
                t.start()
            for t in T:
                t.join()

_name, _version = MPI.get_vendor()
if _name == 'LAM/MPI':
    TestMPIThreads.REQUIRED = MPI.THREAD_MULTIPLE

_VERBOSE = False
#_VERBOSE = True

if __name__ == '__main__':
    import sys
    if '-v' in sys.argv:
        _VERBOSE = True
    unittest.main()
