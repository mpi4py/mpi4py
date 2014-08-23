from mpi4py import dl
import mpiunittest as unittest
import sys
import os

class TestDL(unittest.TestCase):

    def testDL1(self):
        if sys.platform == 'darwin':
            libm = 'libm.dylib'
        else:
            libm = 'libm.so'

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
        handle = dl.dlopen('xxxxx', dl.RTLD_LOCAL|dl.RTLD_LAZY)
        self.assertTrue(handle == 0)
        self.assertTrue(dl.dlerror() is not None)


if os.name != 'posix':
    del TestDL


if __name__ == '__main__':
    unittest.main()
