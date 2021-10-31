import mpi4py
import unittest
import warnings
import os


class TestRC(unittest.TestCase):

    def testCall(self):
        rc = type(mpi4py.rc)()
        rc(initialize   = rc.initialize)
        rc(threads      = rc.threads)
        rc(thread_level = rc.thread_level)
        rc(finalize     = rc.finalize)
        rc(fast_reduce  = rc.fast_reduce)
        rc(recv_mprobe  = rc.recv_mprobe)
        return rc

    def testCallKwArgs(self):
        rc = self.testCall()
        kwargs = rc.__dict__.copy()
        rc(**kwargs)

    def testInitKwArgs(self):
        rc = self.testCall()
        kwargs = rc.__dict__.copy()
        rc = type(mpi4py.rc)(**kwargs)

    def testBadAttribute(self):
        error = lambda: mpi4py.rc(ABCXYZ=123456)
        self.assertRaises(TypeError, error)
        error = lambda: setattr(mpi4py.rc, 'ABCXYZ', 123456)
        self.assertRaises(TypeError, error)
        error = lambda: getattr(mpi4py.rc, 'ABCXYZ')
        self.assertRaises(AttributeError, error)

    def testRepr(self):
        repr(mpi4py.rc)


class TestConfig(unittest.TestCase):

    def testGetInclude(self):
        path = mpi4py.get_include()
        self.assertTrue(isinstance(path, str))
        self.assertTrue(os.path.isdir(path))
        header = os.path.join(path, 'mpi4py', 'mpi4py.h')
        self.assertTrue(os.path.isfile(header))

    def testGetConfig(self):
        conf = mpi4py.get_config()
        self.assertTrue(isinstance(conf, dict))
        mpicc = conf.get('mpicc')
        if mpicc is not None:
            self.assertTrue(os.path.exists(mpicc))


@unittest.skipIf(os.name != 'posix', 'not-posix')
class TestProfile(unittest.TestCase):

    def testProfile(self):
        import platform, sysconfig
        bits = platform.architecture()[0][:-3]
        multiarch = sysconfig.get_config_var('MULTIARCH') or ''
        libpath = [
            "/usr/lib" + bits,
            os.path.join("/usr/lib", multiarch),
            "/usr/lib",
        ]
        def mpi4py_profile(*args, **kargs):
            try:
                mpi4py.profile(*args, **kargs)
            except ValueError:
                pass
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            with self.assertRaises(UserWarning):
                mpi4py.profile('hosts', path=["/etc"])
            warnings.simplefilter('ignore')
            for libname in ('c', 'm', 'dl'):
                mpi4py_profile(libname, path=libpath)
                for path in libpath:
                    mpi4py_profile(libname, path=path)
            with self.assertRaises(ValueError):
                mpi4py.profile('@querty')
            with self.assertRaises(ValueError):
                mpi4py.profile('@querty', path="/usr/lib")
            with self.assertRaises(ValueError):
                mpi4py.profile('@querty', path=["/usr/lib"])
            with self.assertRaises(ValueError):
                mpi4py.profile('@querty')


class TestPackage(unittest.TestCase):

    def testImports(self):
        import mpi4py
        import mpi4py.MPI
        import mpi4py.typing
        import mpi4py.__main__
        import mpi4py.bench
        import mpi4py.futures
        import mpi4py.futures.__main__
        import mpi4py.futures.server
        import mpi4py.util
        import mpi4py.util.pkl5
        import mpi4py.util.dtlib
        import mpi4py.run


if __name__ == '__main__':
    unittest.main()
