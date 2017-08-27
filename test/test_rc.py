from mpi4py import rc
import mpiunittest as unittest


class TestRC(unittest.TestCase):

    def testRC1(self):
        rc(initialize   = rc.initialize)
        rc(threads      = rc.threads)
        rc(thread_level = rc.thread_level)
        rc(finalize     = rc.finalize)
        rc(fast_reduce  = rc.fast_reduce)
        rc(recv_mprobe  = rc.recv_mprobe)

    def testRC2(self):
        kwargs = rc.__dict__.copy()
        rc(**kwargs)

    def testRC3(self):
        error = lambda: rc(ABCXYZ=123456)
        self.assertRaises(TypeError, error)


if __name__ == '__main__':
    unittest.main()
