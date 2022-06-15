import mpi4py
import unittest
import warnings
import pathlib
import os


class TestRC(unittest.TestCase):

    @staticmethod
    def newrc():
        rc = type(mpi4py.rc)()
        rc(initialize   = rc.initialize)
        rc(threads      = rc.threads)
        rc(thread_level = rc.thread_level)
        rc(finalize     = rc.finalize)
        rc(fast_reduce  = rc.fast_reduce)
        rc(recv_mprobe  = rc.recv_mprobe)
        rc(errors       = rc.errors)
        return rc

    def testCallKwArgs(self):
        rc = self.newrc()
        kwargs = rc.__dict__.copy()
        rc(**kwargs)

    def testInitKwArgs(self):
        rc = self.newrc()
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
        import struct
        import sysconfig
        bits = struct.calcsize('P') * 8
        triplet = sysconfig.get_config_var('MULTIARCH') or ''
        libpath = [
            f"{prefix}{suffix}"
            for prefix in ("/lib", "/usr/lib")
            for suffix in (bits, f"/{triplet}", "")
        ]
        fspath = (
            os.fsencode,
            os.fsdecode,
            pathlib.Path
        )
        libraries = (
            'c', 'libc.so.6',
            'm', 'libm.so.6',
            'dl', 'libdl.so.2',
        )
        def mpi4py_profile(*args, **kwargs):
            try:
                mpi4py.profile(*args, **kwargs)
            except ValueError:
                pass
        if os.name != 'posix':
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                with self.assertRaises(UserWarning):
                    mpi4py.profile(MPI.__file__)
            return
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for libname in libraries:
                mpi4py_profile(libname, path=libpath)
                for fs in fspath:
                    mpi4py_profile(libname, path=map(fs, libpath))
                for path in libpath:
                    mpi4py_profile(libname, path=path)
                    for fsp in fspath:
                        mpi4py_profile(libname, path=fsp(path))
            warnings.simplefilter('error')
            with self.assertRaises(UserWarning):
                mpi4py.profile('hosts', path=["/etc"])
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
