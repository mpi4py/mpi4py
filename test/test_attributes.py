from mpi4py import MPI
import mpiunittest as unittest

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
        self.comm.Set_attr(self.keyval, attrval)
        o = self.comm.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        dupcomm = self.comm.Clone()
        o = dupcomm.Get_attr(self.keyval)
        if copy_fn is True:
            self.assertTrue(o is attrval)
        elif not copy_fn:
            self.assertTrue(o is None)
        dupcomm.Free()
        self.comm.Delete_attr(self.keyval)
        o = self.comm.Get_attr(self.keyval)
        self.assertTrue(o is None)

    def testAttrCopyFalse(self):
        self.testAttr(False)

    def testAttrCopyTrue(self):
        self.testAttr(True)

    def testAttrCopyDelete(self):
        self.keyval = MPI.Comm.Create_keyval(
            copy_fn=lambda o, k, a: MPI.Comm.Clone(a),
            delete_fn=lambda o, k, a: MPI.Comm.Free(a))
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)
        comm1 = self.comm
        dupcomm1 = comm1.Clone()
        comm1.Set_attr(self.keyval, dupcomm1)
        self.assertTrue(dupcomm1 != MPI.COMM_NULL)
        comm2 = comm1.Clone()
        dupcomm2 = comm2.Get_attr(self.keyval)
        self.assertTrue(dupcomm1 != dupcomm2)
        comm2.Free()
        self.assertTrue(dupcomm2 == MPI.COMM_NULL)
        self.comm.Delete_attr(self.keyval)
        self.assertTrue(dupcomm1 == MPI.COMM_NULL)

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
        self.datatype.Set_attr(self.keyval, attrval)

        o = self.datatype.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        dupdatatype = self.datatype.Dup()
        o = dupdatatype.Get_attr(self.keyval)
        if copy_fn is True:
            self.assertTrue(o is attrval)
        elif not copy_fn:
            self.assertTrue(o is None)
        dupdatatype.Free()
        self.datatype.Delete_attr(self.keyval)
        o = self.datatype.Get_attr(self.keyval)
        self.assertTrue(o is None)

    def testAttrCopyFalse(self):
        self.testAttr(False)

    def testAttrCopyTrue(self):
        self.testAttr(True)

    def testAttrCopyDelete(self):
        self.keyval = MPI.Datatype.Create_keyval(
            copy_fn=lambda o, k, a: MPI.Datatype.Dup(a),
            delete_fn=lambda o, k, a: MPI.Datatype.Free(a))
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        datatype1 = self.datatype
        dupdatatype1 = datatype1.Dup()
        datatype1.Set_attr(self.keyval, dupdatatype1)
        self.assertTrue(dupdatatype1 != MPI.DATATYPE_NULL)
        datatype2 = datatype1.Dup()
        dupdatatype2 = datatype2.Get_attr(self.keyval)
        self.assertTrue(dupdatatype1 != dupdatatype2)
        datatype2.Free()
        self.assertTrue(dupdatatype2 == MPI.DATATYPE_NULL)
        self.datatype.Delete_attr(self.keyval)
        self.assertTrue(dupdatatype1 == MPI.DATATYPE_NULL)

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
        self.win.Set_attr(self.keyval, attrval)
        o = self.win.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        self.win.Delete_attr(self.keyval)
        o = self.win.Get_attr(self.keyval)
        self.assertTrue(o is None)

    def testAttrCopyDelete(self):
        self.keyval = MPI.Win.Create_keyval(
            delete_fn=lambda o, k, a: MPI.Win.Free(a))
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        newwin = MPI.Win.Create(MPI.BOTTOM, 1,
                                MPI.INFO_NULL, MPI.COMM_SELF)
        #
        self.win.Set_attr(self.keyval, newwin)
        self.assertTrue(newwin != MPI.WIN_NULL)
        #
        self.win.Delete_attr(self.keyval)
        self.assertTrue(newwin == MPI.WIN_NULL)


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


name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version < (1,5,2):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del BaseTestCommAttr.testAttrCopyDelete
            del TestWinAttr.testAttrCopyDelete
if name == 'Platform MPI':
    del TestWinAttr.testAttrCopyDelete


if __name__ == '__main__':
    unittest.main()
