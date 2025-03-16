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
        with self.catchNotImplementedError(2, 0):
            self.STATUS.Set_elements(MPI.BYTE, 7)
            count = self.STATUS.Get_count(MPI.BYTE)
            self.assertEqual(count, 7)
            elements = self.STATUS.Get_elements(MPI.BYTE)
            self.assertEqual(elements, 7)

    def testIsCancelled(self):
        flag = self.STATUS.Is_cancelled()
        self.assertIs(type(flag), bool)
        self.assertFalse(flag)

    def testSetCancelled(self):
        with self.catchNotImplementedError(2, 0):
            self.STATUS.Set_cancelled(True)
            flag = self.STATUS.Is_cancelled()
            self.assertTrue(flag)

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
        with self.catchNotImplementedError(2, 0):
            self.assertIs(type(self.STATUS.count), int)
            self.assertEqual(self.STATUS.count, 0)
            self.STATUS.count = 7
            self.assertEqual(self.STATUS.count, 7)
            self.STATUS.count = 0
        with self.catchNotImplementedError(2, 0):
            self.assertIs(type(self.STATUS.cancelled), bool)
            self.assertFalse(self.STATUS.cancelled)
            self.STATUS.cancelled = True
            self.assertTrue(self.STATUS.cancelled)
            self.STATUS.cancelled = False

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
        with self.catchNotImplementedError(2, 0):
            self.STATUS.Set_elements(MPI.BYTE, 7)
        with self.catchNotImplementedError(2, 0):
            self.STATUS.Set_cancelled(True)
        status = MPI.Status(self.STATUS)
        with self.catchNotImplementedError(2, 0):
            count = status.Get_count(MPI.BYTE)
            elems = status.Get_elements(MPI.BYTE)
            self.assertEqual(count, 7)
            self.assertEqual(elems, 7)
        with self.catchNotImplementedError(2, 0):
            flag = status.Is_cancelled()
            self.assertTrue(flag)

    def testPickle(self):
        from pickle import dumps, loads
        self.STATUS.source = 1
        self.STATUS.tag    = 2
        self.STATUS.error  = MPI.ERR_ARG
        status = loads(dumps(self.STATUS))
        self.assertEqual(status.source, 1)
        self.assertEqual(status.tag,    2)
        self.assertEqual(status.error,  MPI.ERR_ARG)

    def testToMemory(self):
        status = self.STATUS
        status.source = 11
        status.tag    = 22
        status.error  = 33
        mem = status.tomemory()
        seq = list(mem)
        mem[seq.index(11)] = 111
        mem[seq.index(22)] = 222
        mem[seq.index(33)] = 333
        self.assertEqual(status.source, 111)
        self.assertEqual(status.tag,    222)
        self.assertEqual(status.error,  333)


if __name__ == '__main__':
    unittest.main()
