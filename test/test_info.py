from mpi4py import MPI
import mpiunittest as unittest
import sys


class TestInfoNull(unittest.TestCase):

    def testTruth(self):
        self.assertFalse(bool(MPI.INFO_NULL))

    def testPickle(self):
        from pickle import dumps, loads
        null = loads(dumps(MPI.INFO_NULL))
        self.assertIs(null, MPI.INFO_NULL)
        null = loads(dumps(MPI.Info()))
        self.assertIsNot(null, MPI.INFO_NULL)
        self.assertEqual(null, MPI.INFO_NULL)

    def testPyMethods(self):
        inull = MPI.INFO_NULL
        def getitem(): return inull['k']
        def setitem(): inull['k'] = 'v'
        def delitem(): del inull['k']
        def update():  inull.update([])
        def pop():     inull.pop('k')
        def popitem(): inull.popitem()
        self.assertEqual(len(inull), 0)
        self.assertNotIn('key', inull)
        self.assertRaises(KeyError, getitem)
        self.assertRaises(KeyError, setitem)
        self.assertRaises(KeyError, delitem)
        self.assertRaises(KeyError, update)
        self.assertRaises(KeyError, pop)
        self.assertRaises(KeyError, popitem)
        self.assertIsNone(inull.get('key', None))
        self.assertIsNone(inull.pop('key', None))
        self.assertEqual(inull.keys(), [])
        self.assertEqual(inull.values(), [])
        self.assertEqual(inull.items(), [])
        self.assertEqual(inull.copy(), inull)
        inull.clear()

class TestInfoEnv(unittest.TestCase):

    KEYS = (
        "command",
        "argv",
        "maxprocs",
        "soft",
        "host",
        "arch",
        "wdir",
        "file",
        "thread_level",
    )

    def testTruth(self):
        self.assertTrue(bool(MPI.INFO_ENV))

    def testPickle(self):
        from pickle import dumps, loads
        ienv = loads(dumps(MPI.INFO_ENV))
        self.assertIs(ienv, MPI.INFO_ENV)
        ienv = loads(dumps(MPI.Info(MPI.INFO_ENV)))
        self.assertIsNot(ienv, MPI.INFO_ENV)
        self.assertEqual(ienv, MPI.INFO_ENV)

    def testPyMethods(self):
        env = MPI.INFO_ENV
        for key in self.KEYS:
            v = env.Get(key)
            del v

    def testDup(self):
        env = MPI.INFO_ENV
        dup = env.Dup()
        try:
            for key in self.KEYS:
                self.assertEqual(env.Get(key), dup.Get(key))
        finally:
            dup.Free()

    def testCreateEnv(self):
        try:
            env = MPI.Info.Create_env()
        except NotImplementedError:
            if MPI.Get_version() >= (4, 0): raise
            raise unittest.SkipTest("mpi-info-create-env")
        for key in self.KEYS:
            v = env.Get(key)
            del v
        try:
            dup = env.Dup()
            try:
                for key in self.KEYS:
                    self.assertEqual(env.Get(key), dup.Get(key))
            finally:
                dup.Free()
        finally:
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
        self.assertIsNone(value)

    def testGetString(self):
        value = self.INFO.Get_string('key')
        self.assertIsNone(value)

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
        self.assertIsNone(value)

    def testPickle(self):
        from pickle import dumps, loads
        mold = self.INFO
        info = loads(dumps(mold))
        self.assertIsNot(info, mold)
        self.assertNotEqual(info, mold)
        self.assertEqual(info.items(), mold.items())
        info.Free()
        mold = self.INFO
        mold.update([("foo", "bar"), ("answer", "42")])
        info = loads(dumps(mold))
        self.assertIsNot(info, mold)
        self.assertNotEqual(info, mold)
        self.assertEqual(info.items(), mold.items())
        info.Free()

    def testPyMethods(self):
        INFO = self.INFO

        self.assertEqual(len(INFO), 0)
        self.assertNotIn('key', INFO)
        self.assertEqual(INFO.keys(), [])
        self.assertEqual(INFO.values(), [])
        self.assertEqual(INFO.items(), [])

        INFO['key'] = 'value'
        self.assertEqual(len(INFO), 1)
        self.assertIn('key', INFO)
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
        self.assertNotIn('key', INFO)
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
        self.assertIsNone(INFO.get('key2'))
        self.assertEqual(INFO.get('key2', 'value2'),  'value2')
        INFO.update(key2='value2')
        self.assertEqual(len(INFO), 2)
        self.assertEqual(INFO['key1'], 'value1')
        self.assertEqual(INFO['key2'], 'value2')
        self.assertEqual(INFO.get('key1'), 'value1')
        self.assertEqual(INFO.get('key2'), 'value2')
        self.assertIsNone(INFO.get('key3'))
        self.assertEqual(INFO.get('key3', 'value3'),  'value3')
        INFO.update([('key1', 'newval1')], key2='newval2')
        self.assertEqual(len(INFO), 2)
        self.assertEqual(INFO['key1'], 'newval1')
        self.assertEqual(INFO['key2'], 'newval2')
        self.assertEqual(INFO.get('key1'), 'newval1')
        self.assertEqual(INFO.get('key2'), 'newval2')
        self.assertIsNone(INFO.get('key3'))
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
        self.assertIsNone(INFO.get('key1'))
        self.assertIsNone(INFO.get('key2'))
        self.assertIsNone(INFO.get('key3'))
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
