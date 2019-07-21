import mpiunittest as unittest
import sys, os
try:
    from mpi4py import dl
except ImportError:
    dl = None

pypy_lt_510 = (hasattr(sys, 'pypy_version_info') and
               sys.pypy_version_info < (5, 10))

try:
    if pypy_lt_510:
        ctypes = None
    else:
        import ctypes
except ImportError:
    ctypes = None

@unittest.skipIf(dl is None, 'mpi4py-dl')
class TestDL(unittest.TestCase):

    @unittest.skipIf(ctypes is None, 'ctypes')
    def testDL1(self):
        from ctypes.util import find_library
        libm = find_library('m')

        handle = dl.dlopen(libm, dl.RTLD_LOCAL|dl.RTLD_LAZY)
        self.assertTrue(handle != 0)
        self.assertTrue(dl.dlerror() is None)

        symbol = dl.dlsym(handle, 'sqrt')
        self.assertTrue(symbol != 0)
        self.assertTrue(dl.dlerror() is None)

        symbol = dl.dlsym(handle, 'xxxxx')
        self.assertTrue(symbol == 0)
        self.assertTrue(dl.dlerror() is not None)

        ierr = dl.dlclose(handle)
        self.assertTrue(ierr == 0)
        self.assertTrue(dl.dlerror() is None)

    @unittest.skipIf(pypy_lt_510 and sys.platform == 'darwin',
                     'pypy(<5.10)|darwin')
    def testDL2(self):
        handle = dl.dlopen(None, dl.RTLD_GLOBAL|dl.RTLD_NOW)
        self.assertTrue(handle != 0)
        self.assertTrue(dl.dlerror() is None)

        symbol = dl.dlsym(handle, 'malloc')
        self.assertTrue(symbol != 0)
        self.assertTrue(dl.dlerror() is None)

        symbol = dl.dlsym(handle, '!@#$%^&*()')
        self.assertTrue(symbol == 0)
        self.assertTrue(dl.dlerror() is not None)

        ierr = dl.dlclose(handle)
        self.assertTrue(ierr == 0)
        self.assertTrue(dl.dlerror() is None)

    def testDL3(self):
        symbol = dl.dlsym(None, 'malloc')
        self.assertTrue(symbol != 0)
        self.assertTrue(dl.dlerror() is None)

        symbol = dl.dlsym(None, '!@#$%^&*()')
        self.assertTrue(symbol == 0)
        self.assertTrue(dl.dlerror() is not None)

        ierr = dl.dlclose(None)
        self.assertTrue(ierr == 0)
        self.assertTrue(dl.dlerror() is None)

    def testDL4(self):
        handle = dl.dlopen('xxxxx', dl.RTLD_LOCAL|dl.RTLD_LAZY)
        self.assertTrue(handle == 0)
        self.assertTrue(dl.dlerror() is not None)


if __name__ == '__main__':
    unittest.main()
