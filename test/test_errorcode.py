from mpi4py import MPI
import mpiunittest as unittest

class TestErrorCode(unittest.TestCase):

    errorclasses = [item[1] for item in vars(MPI).items()
                    if item[0].startswith('ERR_')]
    errorclasses.insert(0, MPI.SUCCESS)
    errorclasses.remove(MPI.ERR_LASTCODE)

    def testGetErrorClass(self):
        self.assertEqual(self.errorclasses[0], 0)
        for ierr in self.errorclasses:
            errcls = MPI.Get_error_class(ierr)
            self.assertTrue(errcls >= MPI.SUCCESS)
            self.assertTrue(errcls < MPI.ERR_LASTCODE)
            self.assertEqual(errcls, ierr)

    def testGetErrorStrings(self):
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)

    def testException(self):
        from sys import version_info as py_version
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)
            errcls = MPI.Get_error_class(ierr)
            errexc = MPI.Exception(ierr)
            if py_version >= (2,5):
                self.assertEqual(errexc.error_code,   ierr)
                self.assertEqual(errexc.error_class,  ierr)
                self.assertEqual(errexc.error_string, errstr)
            self.assertEqual(str(errexc), errstr)
            self.assertEqual(int(errexc), ierr)
            self.assertTrue(errexc == ierr)
            self.assertTrue(errexc == errexc)
            self.assertFalse(errexc != ierr)
            self.assertFalse(errexc != errexc)

if __name__ == '__main__':
    unittest.main()
