from mpi4py import MPI
import mpiunittest as unittest


class TestStatus(unittest.TestCase):

    def setUp(self):
        self.STATUS = MPI.Status()

    def tearDown(self):
        self.STATUS = None

    def testDefaultFieldValues(self):
        self.assertEqual(self.STATUS.Get_source(), MPI.ANY_SOURCE)
        self.assertEqual(self.STATUS.Get_tag(),    MPI.ANY_TAG)
        self.assertEqual(self.STATUS.Get_error(),  MPI.SUCCESS)

    def testGetCount(self):
        count = self.STATUS.Get_count(MPI.BYTE)
        self.assertEqual(count, 0)

    def testGetElements(self):
        elements = self.STATUS.Get_elements(MPI.BYTE)
        self.assertEqual(elements, 0)

    def testSetElements(self):
        try:
            self.STATUS.Set_elements(MPI.BYTE, 7)
            count = self.STATUS.Get_count(MPI.BYTE)
            self.assertEqual(count, 7)
            elements = self.STATUS.Get_elements(MPI.BYTE)
            self.assertEqual(elements, 7)
        except NotImplementedError:
            if MPI.Get_version() >= (2,0): raise
            self.skipTest('mpi-status-set_elements')

    def testIsCancelled(self):
        flag = self.STATUS.Is_cancelled()
        self.assertTrue(type(flag) is bool)
        self.assertFalse(flag)

    def testSetCancelled(self):
        try:
            self.STATUS.Set_cancelled(True)
            flag = self.STATUS.Is_cancelled()
            self.assertTrue(flag)
        except NotImplementedError:
            if MPI.Get_version() >= (2,0): raise
            self.skipTest('mpi-status-set_cancelled')

    def testPyProps(self):
        self.assertEqual(self.STATUS.Get_source(), self.STATUS.source)
        self.assertEqual(self.STATUS.Get_tag(),    self.STATUS.tag)
        self.assertEqual(self.STATUS.Get_error(),  self.STATUS.error)
        self.STATUS.source = 1
        self.STATUS.tag    = 2
        self.STATUS.error  = MPI.ERR_ARG
        self.assertEqual(self.STATUS.source, 1)
        self.assertEqual(self.STATUS.tag,    2)
        self.assertEqual(self.STATUS.error,  MPI.ERR_ARG)

    def testConstructor(self):
        self.assertRaises(TypeError, MPI.Status, 123)
        self.assertRaises(TypeError, MPI.Status, "abc")
        
    def testCopyConstructor(self):
        self.STATUS.source = 1
        self.STATUS.tag    = 2
        self.STATUS.error  = MPI.ERR_ARG
        status = MPI.Status(self.STATUS)
        self.assertEqual(status.source, 1)
        self.assertEqual(status.tag,    2)
        self.assertEqual(status.error,  MPI.ERR_ARG)
        try:
            self.STATUS.Set_elements(MPI.BYTE, 7)
        except NotImplementedError:
            pass
        try:
            self.STATUS.Set_cancelled(True)
        except NotImplementedError:
            pass
        status = MPI.Status(self.STATUS)
        try:
            count = status.Get_count(MPI.BYTE)
            elems = status.Get_elements(MPI.BYTE)
            self.assertEqual(count, 7)
            self.assertEqual(elems, 7)
        except NotImplementedError:
            pass
        try:
            flag = status.Is_cancelled()
            self.assertTrue(flag)
        except NotImplementedError:
            pass


if __name__ == '__main__':
    unittest.main()
