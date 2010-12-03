from mpi4py import MPI
import mpiunittest as unittest
from sys import getrefcount as getrc

class TestCommWorldAttr(unittest.TestCase):

    keyval = MPI.KEYVAL_INVALID

    def setUp(self):
        self.comm = MPI.COMM_WORLD.Dup()

    def tearDown(self):
        self.comm.Free()
        if self.keyval != MPI.KEYVAL_INVALID:
            self.keyval = MPI.Comm.Free_keyval(self.keyval)
            self.assertEqual(self.keyval, MPI.KEYVAL_INVALID)

    def testAttr(self, copy_fn=None, delete_fn=None):
        self.keyval = MPI.Comm.Create_keyval(copy_fn, delete_fn)
        self.assertNotEqual(self.keyval, MPI.KEYVAL_INVALID)

        attrval = [1,2,3]
        rc = getrc(attrval)
        self.comm.Set_attr(self.keyval, attrval)
        self.assertEqual(getrc(attrval), rc+1)

        o = self.comm.Get_attr(self.keyval)
        self.assertTrue(o is attrval)
        self.assertEqual(getrc(attrval), rc+2)
        o = None

        dupcomm = self.comm.Dup()
        if copy_fn is True:
            self.assertEqual(getrc(attrval), rc+2)
        o = dupcomm.Get_attr(self.keyval)
        if copy_fn is True:
            self.assertTrue(o is attrval)
            self.assertEqual(getrc(attrval), rc+3)
        elif not copy_fn:
            self.assertTrue(o is None)
            self.assertEqual(getrc(attrval), rc+1)
        dupcomm.Free()
        o = None

        self.assertEqual(getrc(attrval), rc+1)
        self.comm.Del_attr(self.keyval)
        self.assertEqual(getrc(attrval), rc)

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
        dupcomm1 = comm1.Dup()
        rc = getrc(dupcomm1)

        comm1.Set_attr(self.keyval, dupcomm1)
        self.assertTrue(dupcomm1 != MPI.COMM_NULL)
        self.assertTrue(getrc(dupcomm1), rc+1)

        comm2 = comm1.Clone()
        dupcomm2 = comm2.Get_attr(self.keyval)
        self.assertTrue(dupcomm1 != dupcomm2)
        self.assertTrue(getrc(dupcomm1), rc+1)
        self.assertTrue(getrc(dupcomm2), 3)
        comm2.Free()
        self.assertTrue(dupcomm2 == MPI.COMM_NULL)
        self.assertTrue(getrc(dupcomm1), rc+1)
        self.assertTrue(getrc(dupcomm2), 2)

        self.comm.Del_attr(self.keyval)
        self.assertTrue(dupcomm1 == MPI.COMM_NULL)
        self.assertTrue(getrc(dupcomm1), rc)

class TestCommSelfAttr(TestCommWorldAttr):

    def setUp(self):
        self.comm = MPI.COMM_SELF.Dup()

if __name__ == '__main__':
    unittest.main()
