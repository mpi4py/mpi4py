from mpi4py import MPI
import mpiunittest as unittest
try:
    import array
except ImportError:
    array = None


class BaseTestAttr(object):

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
        self.assertEqual(attr, None)
        attrval = [1,2,3]
        obj.Set_attr(self.keyval, attrval)
        attr = obj.Get_attr(self.keyval)
        self.assertTrue(attr is attrval)
        if hasattr(obj, 'Dup'):
            dup = obj.Dup()
            attr = dup.Get_attr(self.keyval)
            if copy_fn is True:
                self.assertTrue(attr is attrval)
            elif not copy_fn:
                self.assertTrue(attr is None)
            dup.Free()
        obj.Delete_attr(self.keyval)
        attr = obj.Get_attr(self.keyval)
        self.assertTrue(attr is None)

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
        self.assertEqual(attr, None)
        attrval = [1,2,3]
        obj.Set_attr(self.keyval, attrval)
        attr = obj.Get_attr(self.keyval)
        self.assertTrue(attr is attrval)
        if hasattr(obj, 'Dup'):
            dup = obj.Dup()
            attr = dup.Get_attr(self.keyval)
            self.assertTrue(attr is None)
            dup.Free()
        obj.Delete_attr(self.keyval)
        attr = obj.Get_attr(self.keyval)
        self.assertTrue(attr is None)

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
        self.assertEqual(attr, None)
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
        self.assertTrue(attr is None)

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
        self.assertTrue(dup1 != null)
        obj2 = obj1.Dup()
        dup2 = obj2.Get_attr(self.keyval)
        self.assertTrue(dup1 != dup2)
        obj2.Free()
        self.assertTrue(dup2 == null)
        self.obj.Delete_attr(self.keyval)
        self.assertTrue(dup1 == null)

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
        self.assertTrue(dup1 != null)
        obj2 = obj1.Dup()
        dup2 = obj2.Get_attr(self.keyval)
        self.assertTrue(dup1 != dup2)
        obj2.Free()
        self.assertTrue(dup2 == null)
        self.obj.Delete_attr(self.keyval)
        self.assertTrue(dup1 == null)

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
    @unittest.skipMPI('PlatformMPI')
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
        win = MPI.Win.Create(MPI.BOTTOM, 1,
                             MPI.INFO_NULL, MPI.COMM_SELF)
        self.obj.Set_attr(self.keyval, win)
        self.assertTrue(win != null)
        self.obj.Delete_attr(self.keyval)
        self.assertTrue(win == null)


try:
    k = MPI.Datatype.Create_keyval()
    k = MPI.Datatype.Free_keyval(k)
except NotImplementedError:
    unittest.disable(BaseTestDatatypeAttr, 'mpi-type-attr')
SpectrumMPI = MPI.get_vendor()[0] == 'Spectrum MPI'
try:
    if SpectrumMPI: raise NotImplementedError
    k = MPI.Win.Create_keyval()
    k = MPI.Win.Free_keyval(k)
except NotImplementedError:
    unittest.disable(TestWinAttr, 'mpi-win-attr')


if __name__ == '__main__':
    unittest.main()
