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


if __name__ == '__main__':
    unittest.main()
