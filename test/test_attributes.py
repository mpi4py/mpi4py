from mpi4py import MPI
import mpiunittest as unittest
try:
    from sys import getrefcount
except ImportError:
    class getrefcount(object):
        def __init__(self, arg):
            pass
        def __eq__(self, other):
            return True
        def __add__(self, other):
            return self

class BaseTestCommAttr(object):

    keyval = MPI.KEYVAL_INVALID

    def tearDown(self):
        self.comm.Free()
        if self.keyval != MPI.KEYVAL_INVALID:
            self.keyval = MPI.Comm.Free_keyval(self.keyval)
            self.assertEqual(self.keyval, MPI.KEYVAL_INVALID)

    def testAttr(self, copy_fn=None, delete_fn=None):
        self.keyval = MPI.Comm.Create_keyval(copy_fn, delete_fn)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        attrval = [1,2,3]
        rc = getrefcount(attrval)
        self.comm.Set_attr(self.keyval, attrval)
        self.assertEqual(getrefcount(attrval), rc+1)

        o = self.comm.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        self.assertEqual(getrefcount(attrval), rc+2)
        o = None

        dupcomm = self.comm.Clone()
        if copy_fn is True:
            self.assertEqual(getrefcount(attrval), rc+2)
        o = dupcomm.Get_attr(self.keyval)
        if copy_fn is True:
            self.assertTrue(o is attrval)
            self.assertEqual(getrefcount(attrval), rc+3)
        elif not copy_fn:
            self.assertTrue(o is None)
            self.assertEqual(getrefcount(attrval), rc+1)
        dupcomm.Free()
        o = None

        self.assertEqual(getrefcount(attrval), rc+1)
        self.comm.Delete_attr(self.keyval)
        self.assertEqual(getrefcount(attrval), rc)

        o = self.comm.Get_attr(self.keyval)
        self.assertTrue(o is None)

    def testAttrCopyFalse(self):
        self.testAttr(False)

    def testAttrCopyTrue(self):
        self.testAttr(True)

    def testAttrCopyDelete(self):
        self.keyval = MPI.Comm.Create_keyval(
            copy_fn=MPI.Comm.Clone,
            delete_fn=MPI.Comm.Free)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        comm1 = self.comm
        dupcomm1 = comm1.Clone()
        rc = getrefcount(dupcomm1)

        comm1.Set_attr(self.keyval, dupcomm1)
        self.assertTrue(dupcomm1 != MPI.COMM_NULL)
        self.assertTrue(getrefcount(dupcomm1), rc+1)

        comm2 = comm1.Clone()
        dupcomm2 = comm2.Get_attr(self.keyval)
        self.assertTrue(dupcomm1 != dupcomm2)
        self.assertTrue(getrefcount(dupcomm1), rc+1)
        self.assertTrue(getrefcount(dupcomm2), 3)
        comm2.Free()
        self.assertTrue(dupcomm2 == MPI.COMM_NULL)
        self.assertTrue(getrefcount(dupcomm1), rc+1)
        self.assertTrue(getrefcount(dupcomm2), 2)

        self.comm.Delete_attr(self.keyval)
        self.assertTrue(dupcomm1 == MPI.COMM_NULL)
        self.assertTrue(getrefcount(dupcomm1), rc)

class TestCommAttrWorld(BaseTestCommAttr, unittest.TestCase):
    def setUp(self):
        self.comm = MPI.COMM_WORLD.Dup()
class TestCommAttrSelf(BaseTestCommAttr, unittest.TestCase):
    def setUp(self):
        self.comm = MPI.COMM_SELF.Dup()


class BaseTestDatatypeAttr(object):

    keyval = MPI.KEYVAL_INVALID

    def tearDown(self):
        self.datatype.Free()
        if self.keyval != MPI.KEYVAL_INVALID:
            self.keyval = MPI.Datatype.Free_keyval(self.keyval)
            self.assertEqual(self.keyval, MPI.KEYVAL_INVALID)

    def testAttr(self, copy_fn=None, delete_fn=None):
        self.keyval = MPI.Datatype.Create_keyval(copy_fn, delete_fn)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        attrval = [1,2,3]
        rc = getrefcount(attrval)
        self.datatype.Set_attr(self.keyval, attrval)
        self.assertEqual(getrefcount(attrval), rc+1)

        o = self.datatype.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        self.assertEqual(getrefcount(attrval), rc+2)
        o = None

        dupdatatype = self.datatype.Dup()
        if copy_fn is True:
            self.assertEqual(getrefcount(attrval), rc+2)
        o = dupdatatype.Get_attr(self.keyval)
        if copy_fn is True:
            self.assertTrue(o is attrval)
            self.assertEqual(getrefcount(attrval), rc+3)
        elif not copy_fn:
            self.assertTrue(o is None)
            self.assertEqual(getrefcount(attrval), rc+1)
        dupdatatype.Free()
        o = None

        self.assertEqual(getrefcount(attrval), rc+1)
        self.datatype.Delete_attr(self.keyval)
        self.assertEqual(getrefcount(attrval), rc)

        o = self.datatype.Get_attr(self.keyval)
        self.assertTrue(o is None)

    def testAttrCopyFalse(self):
        self.testAttr(False)

    def testAttrCopyTrue(self):
        self.testAttr(True)

    def testAttrCopyDelete(self):
        self.keyval = MPI.Datatype.Create_keyval(
            copy_fn=MPI.Datatype.Dup,
            delete_fn=MPI.Datatype.Free)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        datatype1 = self.datatype
        dupdatatype1 = datatype1.Dup()
        rc = getrefcount(dupdatatype1)

        datatype1.Set_attr(self.keyval, dupdatatype1)
        self.assertTrue(dupdatatype1 != MPI.DATATYPE_NULL)
        self.assertTrue(getrefcount(dupdatatype1), rc+1)

        datatype2 = datatype1.Dup()
        dupdatatype2 = datatype2.Get_attr(self.keyval)
        self.assertTrue(dupdatatype1 != dupdatatype2)
        self.assertTrue(getrefcount(dupdatatype1), rc+1)
        self.assertTrue(getrefcount(dupdatatype2), 3)
        datatype2.Free()
        self.assertTrue(dupdatatype2 == MPI.DATATYPE_NULL)
        self.assertTrue(getrefcount(dupdatatype1), rc+1)
        self.assertTrue(getrefcount(dupdatatype2), 2)

        self.datatype.Delete_attr(self.keyval)
        self.assertTrue(dupdatatype1 == MPI.DATATYPE_NULL)
        self.assertTrue(getrefcount(dupdatatype1), rc)

class TestDatatypeAttrBYTE(BaseTestDatatypeAttr, unittest.TestCase):
    def setUp(self):
        self.datatype = MPI.BYTE.Dup()
class TestDatatypeAttrINT(BaseTestDatatypeAttr, unittest.TestCase):
    def setUp(self):
        self.datatype = MPI.INT.Dup()
class TestDatatypeAttrFLOAT(BaseTestDatatypeAttr, unittest.TestCase):
    def setUp(self):
        self.datatype = MPI.FLOAT.Dup()

class TestWinAttr(unittest.TestCase):

    keyval = MPI.KEYVAL_INVALID

    def setUp(self):
        self.win = MPI.Win.Create(MPI.BOTTOM, 1,
                                  MPI.INFO_NULL, MPI.COMM_SELF)

    def tearDown(self):
        self.win.Free()
        if self.keyval != MPI.KEYVAL_INVALID:
            self.keyval = MPI.Win.Free_keyval(self.keyval)
            self.assertEqual(self.keyval, MPI.KEYVAL_INVALID)

    def testAttr(self, copy_fn=None, delete_fn=None):
        self.keyval = MPI.Win.Create_keyval(copy_fn, delete_fn)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        attrval = [1,2,3]
        rc = getrefcount(attrval)
        self.win.Set_attr(self.keyval, attrval)
        self.assertEqual(getrefcount(attrval), rc+1)

        o = self.win.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        self.assertEqual(getrefcount(attrval), rc+2)
        o = None

        self.assertEqual(getrefcount(attrval), rc+1)
        self.win.Delete_attr(self.keyval)
        self.assertEqual(getrefcount(attrval), rc)


        o = self.win.Get_attr(self.keyval)
        self.assertTrue(o is None)

    def testAttrCopyDelete(self):
        self.keyval = MPI.Win.Create_keyval(delete_fn=MPI.Win.Free)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        newwin = MPI.Win.Create(MPI.BOTTOM, 1,
                                MPI.INFO_NULL, MPI.COMM_SELF)
        rc = getrefcount(newwin)
        #
        self.win.Set_attr(self.keyval, newwin)
        self.assertTrue(newwin != MPI.WIN_NULL)
        self.assertTrue(getrefcount(newwin), rc+1)
        #
        self.win.Delete_attr(self.keyval)
        self.assertTrue(newwin == MPI.WIN_NULL)
        self.assertTrue(getrefcount(newwin), rc)


try:
    k = MPI.Datatype.Create_keyval()
    k = MPI.Datatype.Free_keyval(k)
except NotImplementedError:
    del TestDatatypeAttrBYTE
    del TestDatatypeAttrINT
    del TestDatatypeAttrFLOAT

try:
    k = MPI.Win.Create_keyval()
    k = MPI.Win.Free_keyval(k)
except NotImplementedError:
    del TestWinAttr


_name, _version = MPI.get_vendor()
if (_name == 'Open MPI' and
    _version <= (1, 5, 1)):
    if MPI.Query_thread() > MPI.THREAD_SINGLE:
        del BaseTestCommAttr.testAttrCopyDelete
        del TestWinAttr.testAttrCopyDelete

if __name__ == '__main__':
    unittest.main()
