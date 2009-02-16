from mpi4py import MPI
import mpiunittest as unittest

MPI_ERR_INFO = MPI.ERR_INFO

class TestInfoNull(unittest.TestCase):

    def testTruth(self):
        self.assertFalse(bool(MPI.INFO_NULL))

    def testDup(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Dup)

    def testFree(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Free)

    def testGet(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Get, 'key')

    def testSet(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Set, 'key', 'value')

    def testDelete(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Delete, 'key')

    def testGetNKeys(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Get_nkeys)

    def testGetNthKey(self):
        self.assertRaisesMPI(MPI_ERR_INFO, MPI.INFO_NULL.Get_nthkey, 0)

    def testPyMethods(self):
        inull = MPI.INFO_NULL
        def getitem(): return inull['k']
        def setitem(): inull['k'] = 'v'
        def delitem(): del inull['k']
        self.assertEqual(len(inull), 0)
        self.assertFalse('key' in inull)
        self.assertRaises(KeyError, getitem)
        self.assertRaises(KeyError, setitem)
        self.assertRaises(KeyError, delitem)
        self.assertEqual(inull.keys(), [])
        self.assertEqual(inull.values(), [])
        self.assertEqual(inull.items(), [])

class TestInfo(unittest.TestCase):

    def setUp(self):
        self.INFO  = MPI.Info.Create()

    def tearDown(self):
        self.INFO.Free()
        self.assertEqual(self.INFO, MPI.INFO_NULL)
        self.INFO = None

    def testTruth(self):
        self.assertTrue(bool(self.INFO))

    def testDup(self):
        info = self.INFO.Dup()
        self.assertNotEqual(self.INFO, info)
        self.assertEqual(info.Get_nkeys(), 0)
        info.Free()
        self.assertFalse(info)

    def testGet(self):
        value, flag = self.INFO.Get('key')
        self.assertEqual(value, None)
        self.assertEqual(flag,  False)

    def testGetNKeys(self):
        self.assertEqual(self.INFO.Get_nkeys(), 0)

    def testGetSetDelete(self):
        INFO = self.INFO
        self.assertEqual(INFO.Get_nkeys(), 0)
        INFO.Set('key', 'value')
        nkeys = INFO.Get_nkeys()
        self.assertEqual(nkeys, 1)
        key = INFO.Get_nthkey(0)
        self.assertEqual(key, 'key')
        value, flag = INFO.Get('key')
        self.assertEqual(value, 'value')
        self.assertEqual(flag,  True)
        INFO.Delete('key')
        nkeys = INFO.Get_nkeys()
        self.assertEqual(nkeys, 0)
        value, flag = INFO.Get('key')
        self.assertEqual(value, None)
        self.assertEqual(flag,  False)
        self.assertRaisesMPI(MPI.ERR_INFO_NOKEY, INFO.Delete, 'key')
        self.assertRaisesMPI([MPI.ERR_ARG,MPI.ERR_INFO_KEY], INFO.Get_nthkey, 0)

    def testPyMethods(self):
        INFO = self.INFO

        self.assertEqual(len(INFO), 0)
        self.assertTrue('key' not in INFO)
        self.assertEqual(INFO.keys(), [])
        self.assertEqual(INFO.values(), [])
        self.assertEqual(INFO.items(), [])

        INFO['key'] = 'value'
        self.assertEqual(len(INFO), 1)
        self.assertTrue('key' in INFO)
        self.assertEqual(INFO['key'], 'value')
        for key in INFO:
            self.assertEqual(key, 'key')
        self.assertEqual(INFO.keys(), ['key'])
        self.assertEqual(INFO.values(), ['value'])
        self.assertEqual(INFO.items(), [('key', 'value')])
        self.assertEqual(key, 'key')

        del INFO['key']
        self.assertEqual(len(INFO), 0)
        self.assertTrue('key' not in INFO)
        self.assertEqual(INFO.keys(), [])
        self.assertEqual(INFO.values(), [])
        self.assertEqual(INFO.items(), [])
        def getitem(): INFO['key']
        self.assertRaises(KeyError, getitem)
        def delitem(): del INFO['key']
        self.assertRaises(KeyError, delitem)

try:
    MPI.Info.Create().Free()
except NotImplementedError:
    del TestInfoNull, TestInfo

if MPI.Get_version() <= (2, 0):
    MPI_ERR_INFO = (MPI.ERR_INFO, MPI.ERR_ARG)

_name, _version = MPI.get_vendor()
if _name == 'MPICH2':
    # XXX under discussion
    MPI_ERR_INFO = MPI.ERR_ARG

if __name__ == '__main__':
    unittest.main()
