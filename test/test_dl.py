import mpiunittest as unittest
import sys, os

try:
    from mpi4py import dl
except ImportError:
    dl = None

try:
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
