from mpi4py import MPI
import mpiunittest as unittest
import mpitestutil as testutil

try:
    import array
except ImportError:
    array = None


class BaseTestAttr:

    keyval = MPI.KEYVAL_INVALID

    def tearDown(self):
        if self.obj:
            self.obj.Free()
        if self.keyval != MPI.KEYVAL_INVALID:
            self.keyval = type(self.obj).Free_keyval(self.keyval)
            self.assertEqual(self.keyval, MPI.KEYVAL_INVALID)

    def testAttr(self, copy_fn=None, delete_fn=None):
        cls, obj = type(self.obj), self.obj
        self.keyval = cls.Create_keyval(copy_fn, delete_fn)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        attr = obj.Get_attr(self.keyval)
        self.assertIsNone(attr)
        attrval = [1,2,3]
        obj.Set_attr(self.keyval, attrval)
        attr = obj.Get_attr(self.keyval)
        self.assertIs(attr, attrval)
        if hasattr(obj, 'Dup'):
            dup = obj.Dup()
            attr = dup.Get_attr(self.keyval)
            if copy_fn is True:
                self.assertIs(attr, attrval)
            elif not copy_fn:
                self.assertIsNone(attr)
            dup.Free()
        obj.Delete_attr(self.keyval)
        attr = obj.Get_attr(self.keyval)
        self.assertIsNone(attr)

    def testAttrCopyFalse(self):
        self.testAttr(False)

    def testAttrCopyTrue(self):
        self.testAttr(True)

    def testAttrNoCopy(self):
        cls, obj = type(self.obj), self.obj
        def copy_fn(o, k, v):
            assert k == self.keyval
            assert v is attrval
            return NotImplemented
        self.keyval = cls.Create_keyval(copy_fn, None)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        attr = obj.Get_attr(self.keyval)
        self.assertIsNone(attr)
        attrval = [1,2,3]
        obj.Set_attr(self.keyval, attrval)
        attr = obj.Get_attr(self.keyval)
        self.assertIs(attr, attrval)
        if hasattr(obj, 'Dup'):
            dup = obj.Dup()
            attr = dup.Get_attr(self.keyval)
            self.assertIsNone(attr)
            dup.Free()
        obj.Delete_attr(self.keyval)
        attr = obj.Get_attr(self.keyval)
        self.assertIsNone(attr)

    def testAttrNoPython(self, intval=123456789):
        cls, obj = type(self.obj), self.obj
        def copy_fn(o, k, v):
            assert k == self.keyval
            assert v == intval
            return v
        def del_fn(o, k, v):
            assert k == self.keyval
            assert v == intval
        self.keyval = cls.Create_keyval(copy_fn, del_fn, nopython=True)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        attr = obj.Get_attr(self.keyval)
        self.assertIsNone(attr)
        obj.Set_attr(self.keyval, intval)
        attr = obj.Get_attr(self.keyval)
        self.assertEqual(attr, intval)
        if hasattr(obj, 'Dup'):
            dup = obj.Dup()
            attr = dup.Get_attr(self.keyval)
            self.assertEqual(attr, intval)
            dup.Free()
        obj.Delete_attr(self.keyval)
        attr = obj.Get_attr(self.keyval)
        self.assertIsNone(attr)

    @unittest.skipMPI('openmpi(<=1.10.2)')
    def testAttrNoPythonZero(self):
        self.testAttrNoPython(0)

    @unittest.skipIf(array is None, 'array')
    def testAttrNoPythonArray(self):
        cls, obj = type(self.obj), self.obj
        self.keyval = cls.Create_keyval(nopython=True)
        #
        ary = array.array('i', [42])
        addr, _ = ary.buffer_info()
        obj.Set_attr(self.keyval, addr)
        #
        attr = obj.Get_attr(self.keyval)
        self.assertEqual(attr, addr)

    @unittest.skipMPI('impi(<2021.14.0)')
    @unittest.skipMPI('mvapich')
    @unittest.skipMPI('mpich(<4.2.1)')
    @unittest.skipMPI('openmpi(<5.0.0)')
    def testAttrCopyException(self):
        cls, obj = type(self.obj), self.obj
        if not isinstance(obj, MPI.Datatype): return
        if not hasattr(cls, 'Dup'): return
        def copy_fn(o, k, v):
            raise ValueError
        self.keyval = cls.Create_keyval(copy_fn, None)
        try:
            obj.Set_attr(self.keyval, "value")
            with self.assertRaises(MPI.Exception) as exc_cm:
                with testutil.capture_stderr() as stderr:
                    obj.Dup().Free()
            ierr = exc_cm.exception.Get_error_class()
            self.assertEqual(ierr, MPI.ERR_OTHER)
            self.assertIn('ValueError', stderr.getvalue())
        finally:
            obj.Delete_attr(self.keyval)
            self.keyval = cls.Free_keyval(self.keyval)

    @unittest.skipMPI('impi(<2021.14.0)')
    @unittest.skipMPI('mvapich')
    @unittest.skipMPI('mpich(<4.2.1)')
    def testAttrDeleteException(self):
        cls, obj = type(self.obj), self.obj
        raise_flag = True
        def delete_fn(o, k, v):
            raise ValueError
        self.keyval = cls.Create_keyval(None, delete_fn)
        obj.Set_attr(self.keyval, "value")
        try:
            with self.assertRaises(MPI.Exception) as exc_cm:
                with testutil.capture_stderr() as stderr:
                    obj.Delete_attr(self.keyval)
            ierr = exc_cm.exception.Get_error_class()
            self.assertEqual(ierr, MPI.ERR_OTHER)
            self.assertIn('ValueError', stderr.getvalue())
        finally:
            self.keyval = cls.Free_keyval(self.keyval)


class BaseTestCommAttr(BaseTestAttr):

    NULL = MPI.COMM_NULL

    @unittest.skipMPI('openmpi(<=1.5.1)')
    def testAttrCopyDelete(self):
        cls, obj, null = type(self.obj), self.obj, self.NULL
        #
        self.keyval = cls.Create_keyval(
            copy_fn=lambda o, k, v: cls.Dup(v),
            delete_fn=lambda o, k, v: cls.Free(v))
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        #
        obj1 = obj
        dup1 = obj1.Dup()
        obj1.Set_attr(self.keyval, dup1)
        self.assertNotEqual(dup1, null)
        obj2 = obj1.Dup()
        dup2 = obj2.Get_attr(self.keyval)
        self.assertNotEqual(dup1, dup2)
        obj2.Free()
        self.assertEqual(dup2, null)
        self.obj.Delete_attr(self.keyval)
        self.assertEqual(dup1, null)

class TestCommAttrWorld(BaseTestCommAttr, unittest.TestCase):
    def setUp(self):
        self.obj = MPI.COMM_WORLD.Dup()
class TestCommAttrSelf(BaseTestCommAttr, unittest.TestCase):
    def setUp(self):
        self.obj = MPI.COMM_SELF.Dup()


class BaseTestDatatypeAttr(BaseTestAttr):

    NULL = MPI.DATATYPE_NULL

    def testAttrCopyDelete(self):
        cls, obj, null = type(self.obj), self.obj, self.NULL
        #
        self.keyval = cls.Create_keyval(
            copy_fn=lambda o, k, v: cls.Dup(v),
            delete_fn=lambda o, k, v: cls.Free(v))
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        #
        obj1 = obj
        dup1 = obj1.Dup()
        obj1.Set_attr(self.keyval, dup1)
        self.assertNotEqual(dup1, null)
        obj2 = obj1.Dup()
        dup2 = obj2.Get_attr(self.keyval)
        self.assertNotEqual(dup1, dup2)
        obj2.Free()
        self.assertEqual(dup2, null)
        self.obj.Delete_attr(self.keyval)
        self.assertEqual(dup1, null)

class TestDatatypeAttrBYTE(BaseTestDatatypeAttr, unittest.TestCase):
    def setUp(self):
        self.obj = MPI.BYTE.Dup()
class TestDatatypeAttrINT(BaseTestDatatypeAttr, unittest.TestCase):
    def setUp(self):
        self.obj = MPI.INT.Dup()
class TestDatatypeAttrFLOAT(BaseTestDatatypeAttr, unittest.TestCase):
    def setUp(self):
        self.obj = MPI.FLOAT.Dup()


class TestWinAttr(BaseTestAttr, unittest.TestCase):

    NULL = MPI.WIN_NULL

    def setUp(self):
        win = MPI.Win.Create(MPI.BOTTOM, 1,
                             MPI.INFO_NULL, MPI.COMM_SELF)
        self.obj = self.win = win

    @unittest.skipMPI('openmpi(<=1.5.1)')
    def testAttrCopyDelete(self):
        #
        null = self.NULL
        def delete_fn(o, k, v):
            assert isinstance(o, MPI.Win)
            assert k == self.keyval
            assert v is win
            MPI.Win.Free(v)
        self.keyval = MPI.Win.Create_keyval(delete_fn=delete_fn)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        #
        win = MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF)
        self.obj.Set_attr(self.keyval, win)
        self.assertNotEqual(win, null)
        self.obj.Delete_attr(self.keyval)
        self.assertEqual(win, null)


try:
    k = MPI.Datatype.Create_keyval()
    k = MPI.Datatype.Free_keyval(k)
except NotImplementedError:
    unittest.disable(BaseTestDatatypeAttr, 'mpi-type-attr')
try:
    MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
    k = MPI.Win.Create_keyval()
    k = MPI.Win.Free_keyval(k)
except (NotImplementedError, MPI.Exception):
    unittest.disable(TestWinAttr, 'mpi-win-attr')


if __name__ == '__main__':
    unittest.main()
