try:
    import threading as _threading
    _HAS_THREADING = True
except ImportError:
    import dummy_threading as _threading
    _HAS_THREADING = False

Thread = _threading.Thread
try:
    currentThread = _threading.currentThread
except AttributeError:
    currentThread = _threading.current_thread

from mpi4py import MPI
import mpiunittest as unittest


class TestMPIThreads(unittest.TestCase):

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
        flag = MPI.Is_thread_main()
        self.assertEqual(flag, main)
        if _VERBOSE:
            from sys import stderr
            thread = currentThread()
            name = thread.getName()
            log = lambda m: stderr.write(m+'\n')
            log("%s: MPI.Is_thread_main() -> %s" % (name, flag))

    def testIsThreadMain(self):
        try:
            self._test_is(main=True)
            provided = MPI.Query_thread()
            required = MPI.THREAD_SERIALIZED
            if provided < required: return
        except NotImplementedError:
            return
        T = []
        for i in range(5):
            t = Thread(target=self._test_is,
                       args = (not _HAS_THREADING,),
                       verbose=_VERBOSE)
            T.append(t)
        self._test_is(main=True)
        for t in T:
            t.start()
        for t in T:
            t.join()


_VERBOSE = False
#_VERBOSE = True

if __name__ == '__main__':
    import sys
    if '-v' in sys.argv:
        _VERBOSE = True
    unittest.main()
