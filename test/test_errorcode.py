from mpi4py import MPI
import mpiunittest as unittest


class TestErrorCode(unittest.TestCase):

    errorclasses = [item[1] for item in vars(MPI).items()
                    if item[0].startswith('ERR_')]
    errorclasses.insert(0, MPI.SUCCESS)
    while MPI.ERR_LASTCODE in errorclasses:
        errorclasses.remove(MPI.ERR_LASTCODE)

    def testGetErrorClass(self):
        self.assertEqual(self.errorclasses[0], 0)
        for ierr in self.errorclasses:
            errcls = MPI.Get_error_class(ierr)
            self.assertGreaterEqual(errcls, MPI.SUCCESS)
            self.assertLessEqual(errcls, MPI.ERR_LASTCODE)
            self.assertEqual(errcls, ierr)

    def testGetErrorStrings(self):
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)
            self.assertGreater(len(errstr), 0)

    def testException(self):
        success = MPI.Exception(MPI.SUCCESS)
        lasterr = MPI.Exception(MPI.ERR_LASTCODE)
        for ierr in self.errorclasses:
            errstr = MPI.Get_error_string(ierr)
            errcls = MPI.Get_error_class(ierr)
            errexc = MPI.Exception(ierr)
            self.assertEqual(errexc.Get_error_code(),   ierr)
            self.assertEqual(errexc.Get_error_class(),  errcls)
            self.assertEqual(errexc.Get_error_string(), errstr)
            self.assertEqual(errexc.error_code,   ierr)
            self.assertEqual(errexc.error_class,  errcls)
            self.assertEqual(errexc.error_string, errstr)
            self.assertEqual(repr(errexc), f"MPI.Exception({ierr})")
            self.assertEqual(str(errexc), errstr)
            self.assertEqual(int(errexc), ierr)
            self.assertEqual(hash(errexc), hash(errexc.error_code))
            self.assertTrue(bool(errexc == ierr))
            self.assertTrue(bool(errexc == errexc))
            self.assertFalse(bool(errexc != ierr))
            self.assertFalse(bool(errexc != errexc))
            self.assertTrue(bool(success <= ierr   <= lasterr))
            self.assertTrue(bool(success <= errexc <= lasterr))
            self.assertTrue(bool(errexc >= ierr))
            self.assertTrue(bool(errexc >= success))
            self.assertTrue(bool(lasterr >= ierr))
            self.assertTrue(bool(lasterr >= errexc))
            if errexc == success:
                self.assertFalse(errexc)
            else:
                self.assertTrue(errexc)
                self.assertTrue(bool(errexc > success))
                self.assertTrue(bool(success < errexc))
        exc = MPI.Exception(MPI.SUCCESS-1)
        self.assertEqual(exc, MPI.ERR_UNKNOWN)
        exc = MPI.Exception(MPI.ERR_LASTCODE+1)
        self.assertEqual(exc, MPI.ERR_LASTCODE+1)

    @unittest.skipMPI('openmpi(<1.10.0)')
    def testAddErrorClass(self):
        try:
            errclass = MPI.Add_error_class()
        except NotImplementedError:
            self.skipTest('mpi-add_error_class')
        self.assertGreaterEqual(errclass, MPI.ERR_LASTCODE)
        try:
            MPI.Remove_error_class(errclass)
        except NotImplementedError:
            pass

    @unittest.skipMPI('openmpi(<1.10.0)')
    def testAddErrorCode(self):
        try:
            errcode = MPI.Add_error_code(MPI.ERR_OTHER)
        except NotImplementedError:
            self.skipTest('mpi-add_error_code')
        try:
            MPI.Remove_error_code(errcode)
        except NotImplementedError:
            pass

    @unittest.skipMPI('openmpi(<1.10.0)')
    def testAddErrorClassCodeString(self):
        LASTUSED = MPI.COMM_WORLD.Get_attr(MPI.LASTUSEDCODE)
        try:
            errclass = MPI.Add_error_class()
        except NotImplementedError:
            self.skipTest('mpi-add_error_class')
        lastused = MPI.COMM_WORLD.Get_attr(MPI.LASTUSEDCODE)
        self.assertEqual(errclass, lastused)
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
        #
        with self.catchNotImplementedError(4, 1):
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_class(errclass)
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_code(errcode2)
            MPI.Remove_error_string(errcode2)
            self.assertEqual(MPI.Get_error_string(errcode2), "")
            MPI.Remove_error_code(errcode2)
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_code(errcode2)
            #
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_class(errclass)
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_code(errcode1)
            MPI.Remove_error_string(errcode1)
            self.assertEqual(MPI.Get_error_string(errcode1), "")
            MPI.Remove_error_code(errcode1)
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_code(errcode1)
            #
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_class(errclass)
            MPI.Remove_error_string(errclass)
            self.assertEqual(MPI.Get_error_string(errclass), "")
            MPI.Remove_error_class(errclass)
            with self.assertRaises(MPI.Exception):
                MPI.Remove_error_class(errclass)
        #
        try:
            MPI.Remove_error_class(0)
            self.fail("expected Exception")
        except (MPI.Exception, NotImplementedError):
            pass
        try:
            MPI.Remove_error_code(0)
            self.fail("expected Exception")
        except (MPI.Exception, NotImplementedError):
            pass
        try:
            MPI.Remove_error_string(0)
            self.fail("expected Exception")
        except (MPI.Exception, NotImplementedError):
            pass


if __name__ == '__main__':
    unittest.main()
