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
            self.assertTrue(errcls <= MPI.ERR_LASTCODE)
            self.assertEqual(errcls, ierr)

    def testGetErrorStrings(self):
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)

    def testException(self):
        from sys import version_info as py_version
        success = MPI.Exception(MPI.SUCCESS)
        lasterr = MPI.Exception(MPI.ERR_LASTCODE)
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)
            errcls = MPI.Get_error_class(ierr)
            errexc = MPI.Exception(ierr)
            if py_version >= (2,5):
                self.assertEqual(errexc.error_code,   ierr)
                self.assertEqual(errexc.error_class,  ierr)
                self.assertEqual(errexc.error_string, errstr)
            self.assertEqual(repr(errexc), "MPI.Exception(%d)" % ierr)
            self.assertEqual(str(errexc), errstr)
            self.assertEqual(int(errexc), ierr)
            self.assertEqual(hash(errexc), hash(errexc.error_code))
            self.assertTrue(errexc == ierr)
            self.assertTrue(errexc == errexc)
            self.assertFalse(errexc != ierr)
            self.assertFalse(errexc != errexc)
            self.assertTrue(success <= ierr   <= lasterr)
            self.assertTrue(success <= errexc <= lasterr)
            self.assertTrue(errexc >= ierr)
            self.assertTrue(errexc >= success)
            self.assertTrue(lasterr >= ierr)
            self.assertTrue(lasterr >= errexc)
            if errexc == success:
                self.assertFalse(errexc)
            else:
                self.assertTrue(errexc)
                self.assertTrue(errexc > success)
                self.assertTrue(success < errexc)
        exc = MPI.Exception(MPI.SUCCESS-1)
        self.assertTrue(exc, MPI.ERR_UNKNOWN)
        exc = MPI.Exception(MPI.ERR_LASTCODE+1)
        self.assertTrue(exc, MPI.ERR_UNKNOWN)

    @unittest.skipMPI('openmpi(<1.10.0)')
    def testAddErrorClass(self):
        try:
            errclass = MPI.Add_error_class()
        except NotImplementedError:
            self.skipTest('mpi-add_error_class')
        self.assertTrue(errclass >= MPI.ERR_LASTCODE)

    @unittest.skipMPI('openmpi(<1.10.0)')
    def testAddErrorClassCodeString(self):
        try:
            errclass = MPI.Add_error_class()
        except NotImplementedError:
            self.skipTest('mpi-add_error_class')
        lastused = MPI.COMM_WORLD.Get_attr(MPI.LASTUSEDCODE)
        self.assertTrue(errclass == lastused)
        errstr = MPI.Get_error_string(errclass)
        self.assertEqual(errstr, "")
        MPI.Add_error_string(errclass, "error class")
        self.assertEqual(MPI.Get_error_string(errclass), "error class")
        errcode1 = MPI.Add_error_code(errclass)
        errstr = MPI.Get_error_string(errcode1)
        self.assertEqual(errstr, "")
        MPI.Add_error_string(errcode1, "error code 1")
        self.assertEqual(MPI.Get_error_class(errcode1), errclass)
        self.assertEqual(MPI.Get_error_string(errcode1), "error code 1")
        errcode2 = MPI.Add_error_code(errclass)
        errstr = MPI.Get_error_string(errcode2)
        self.assertEqual(errstr, "")
        MPI.Add_error_string(errcode2, "error code 2")
        self.assertEqual(MPI.Get_error_class(errcode2), errclass)
        self.assertEqual(MPI.Get_error_string(errcode2), "error code 2")


if __name__ == '__main__':
    unittest.main()
