from mpi4py import MPI
import mpiunittest as unittest
import sys


class TestInfoNull(unittest.TestCase):

    def testTruth(self):
        self.assertFalse(bool(MPI.INFO_NULL))

    def testPyMethods(self):
        inull = MPI.INFO_NULL
        def getitem(): return inull['k']
        def setitem(): inull['k'] = 'v'
        def delitem(): del inull['k']
        def update():  inull.update([])
        def pop():     inull.pop('k')
        def popitem(): inull.popitem()
        self.assertEqual(len(inull), 0)
        self.assertFalse('key' in inull)
        self.assertRaises(KeyError, getitem)
        self.assertRaises(KeyError, setitem)
        self.assertRaises(KeyError, delitem)
        self.assertRaises(KeyError, update)
        self.assertRaises(KeyError, pop)
        self.assertRaises(KeyError, popitem)
        self.assertEqual(inull.get('key', None), None)
        self.assertEqual(inull.pop('key', None), None)
        self.assertEqual(inull.keys(), [])
        self.assertEqual(inull.values(), [])
        self.assertEqual(inull.items(), [])
        self.assertEqual(inull.copy(), inull)
        inull.clear()

class TestInfoEnv(unittest.TestCase):

    def testTruth(self):
        self.assertTrue(bool(MPI.INFO_ENV))

    def testPyMethods(self):
        env = MPI.INFO_ENV
        if env == MPI.INFO_NULL: return
        for key in ("command", "argv",
                    "maxprocs", "soft",
                    "host", "arch",
                    "wdir", "file",
                    "thread_level"):
            v = env.Get(key)

    def testCreateEnv(self):
        env = MPI.Info.Create_env()
        if env == MPI.INFO_NULL: return
        for key in ("command", "argv",
                    "maxprocs", "soft",
                    "host", "arch",
                    "wdir", "file",
                    "thread_level"):
            v = env.Get(key)
        env.Free()
        for args in (
            None, [], (),
            sys.executable,
            [sys.executable],
            (sys.executable,),
        ):
            MPI.Info.Create_env(args).Free()
            MPI.Info.Create_env(args=args).Free()

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
        value = self.INFO.Get('key')
        self.assertEqual(value, None)

    def testGetString(self):
        value = self.INFO.Get_string('key')
        self.assertEqual(value, None)

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
        value = INFO.Get('key')
        self.assertEqual(value, 'value')
        INFO.Delete('key')
        nkeys = INFO.Get_nkeys()
        self.assertEqual(nkeys, 0)
        value = INFO.Get('key')
        self.assertEqual(value, None)

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

        INFO['key'] = 'value'
        self.assertEqual(INFO.pop('key'), 'value')
        self.assertEqual(len(INFO), 0)
        self.assertEqual(INFO.pop('key', 'value'), 'value')
        self.assertRaises(KeyError, INFO.pop, 'key')
        INFO['key1'] = 'value1'
        INFO['key2'] = 'value2'
        self.assertEqual(INFO.pop('key1'), 'value1')
        self.assertEqual(len(INFO), 1)
        self.assertEqual(INFO.pop('key2'), 'value2')
        self.assertEqual(len(INFO), 0)

        INFO['key'] = 'value'
        self.assertEqual(INFO.popitem(), ('key', 'value'))
        self.assertEqual(len(INFO), 0)
        self.assertRaises(KeyError, INFO.popitem)
        INFO['key1'] = 'value1'
        INFO['key2'] = 'value2'
        self.assertEqual(INFO.popitem(), ('key2', 'value2'))
        self.assertEqual(len(INFO), 1)
        self.assertEqual(INFO.popitem(), ('key1', 'value1'))
        self.assertEqual(len(INFO), 0)

        self.assertEqual(len(INFO), 0)
        self.assertTrue('key' not in INFO)
        self.assertEqual(INFO.keys(), [])
        self.assertEqual(INFO.values(), [])
        self.assertEqual(INFO.items(), [])
        def getitem(): INFO['key']
        self.assertRaises(KeyError, getitem)
        def delitem(): del INFO['key']
        self.assertRaises(KeyError, delitem)

        INFO.clear()
        INFO.update([('key1','value1')])
        self.assertEqual(len(INFO), 1)
        self.assertEqual(INFO['key1'], 'value1')
        self.assertEqual(INFO.get('key1'), 'value1')
        self.assertEqual(INFO.get('key2'),  None)
        self.assertEqual(INFO.get('key2', 'value2'),  'value2')
        INFO.update(key2='value2')
        self.assertEqual(len(INFO), 2)
        self.assertEqual(INFO['key1'], 'value1')
        self.assertEqual(INFO['key2'], 'value2')
        self.assertEqual(INFO.get('key1'), 'value1')
        self.assertEqual(INFO.get('key2'), 'value2')
        self.assertEqual(INFO.get('key3'),  None)
        self.assertEqual(INFO.get('key3', 'value3'),  'value3')
        INFO.update([('key1', 'newval1')], key2='newval2')
        self.assertEqual(len(INFO), 2)
        self.assertEqual(INFO['key1'], 'newval1')
        self.assertEqual(INFO['key2'], 'newval2')
        self.assertEqual(INFO.get('key1'), 'newval1')
        self.assertEqual(INFO.get('key2'), 'newval2')
        self.assertEqual(INFO.get('key3'),  None)
        self.assertEqual(INFO.get('key3', 'newval3'),  'newval3')
        INFO.update(dict(key1='val1', key2='val2', key3='val3'))
        self.assertEqual(len(INFO), 3)
        self.assertEqual(INFO['key1'], 'val1')
        self.assertEqual(INFO['key2'], 'val2')
        self.assertEqual(INFO['key3'], 'val3')
        dupe = INFO.copy()
        self.assertEqual(INFO.items(), dupe.items())
        dupe.Free()
        INFO.clear()
        self.assertEqual(len(INFO), 0)
        self.assertEqual(INFO.get('key1'), None)
        self.assertEqual(INFO.get('key2'), None)
        self.assertEqual(INFO.get('key3'), None)
        self.assertEqual(INFO.get('key1', 'value1'), 'value1')
        self.assertEqual(INFO.get('key2', 'value2'), 'value2')
        self.assertEqual(INFO.get('key3', 'value3'), 'value3')


try:
    MPI.Info.Create().Free()
except NotImplementedError:
    unittest.disable(TestInfo, 'mpi-info')
    unittest.disable(TestInfoNull, 'mpi-info')
if (MPI.VERSION < 3 and MPI.INFO_ENV == MPI.INFO_NULL):
    unittest.disable(TestInfoEnv, 'mpi-info-env')


if __name__ == '__main__':
    unittest.main()
