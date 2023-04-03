from mpi4py import MPI
import mpiunittest as unittest
import weakref


class TestObjModel(unittest.TestCase):

    objects = [
        MPI.Status(),
        MPI.DATATYPE_NULL,
        MPI.REQUEST_NULL,
        MPI.INFO_NULL,
        MPI.ERRHANDLER_NULL,
        MPI.SESSION_NULL,
        MPI.GROUP_NULL,
        MPI.WIN_NULL,
        MPI.OP_NULL,
        MPI.FILE_NULL,
        MPI.MESSAGE_NULL,
        MPI.COMM_NULL,
    ]

    def testEq(self):
        for i, obj1 in enumerate(self.objects):
            objects = self.objects[:]
            obj2 = objects[i]
            self.assertTrue (bool(obj1 == obj2))
            self.assertFalse(bool(obj1 != obj2))
            del objects[i]
            for obj2 in objects:
                self.assertTrue (bool(obj1 != obj2))
                self.assertTrue (bool(obj2 != obj1))
                self.assertFalse(bool(obj1 == obj2))
                self.assertFalse(bool(obj2 == obj1))
            self.assertFalse(bool(None == obj1 ))
            self.assertFalse(bool(obj1 == None ))
            self.assertFalse(bool(obj1 == True ))
            self.assertFalse(bool(obj1 == False))
            self.assertFalse(bool(obj1 == 12345))
            self.assertFalse(bool(obj1 == "abc"))
            self.assertFalse(bool(obj1 == [123]))
            self.assertFalse(bool(obj1 == (1,2)))
            self.assertFalse(bool(obj1 == {0:0}))
            self.assertFalse(bool(obj1 == set()))

    def testNe(self):
        for i, obj1 in enumerate(self.objects):
            objects = self.objects[:]
            obj2 = objects[i]
            self.assertFalse(bool(obj1 != obj2))
            del objects[i]
            for obj2 in objects:
                self.assertTrue(bool(obj1 != obj2))
            self.assertTrue(bool(None != obj1 ))
            self.assertTrue(bool(obj1 != None ))
            self.assertTrue(bool(obj1 != True ))
            self.assertTrue(bool(obj1 != False))
            self.assertTrue(bool(obj1 != 12345))
            self.assertTrue(bool(obj1 != "abc"))
            self.assertTrue(bool(obj1 != [123]))
            self.assertTrue(bool(obj1 != (1,2)))
            self.assertTrue(bool(obj1 != {0:0}))
            self.assertTrue(bool(obj1 != set()))

    def testBool(self):
        for obj in self.objects[1:]:
            self.assertFalse(not not obj)
            self.assertTrue(not obj)
            self.assertFalse(obj)

    def testReduce(self):
        import pickle
        import copy

        def functions(obj):
            for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
                yield lambda ob: pickle.loads(pickle.dumps(ob, protocol))
            yield copy.copy
            yield copy.deepcopy

        for obj in self.objects:
            for copier in functions(obj):
                dup = copier(obj)
                self.assertIs(type(dup), type(obj))
                if isinstance(obj, MPI.Status):
                    self.assertIsNot(dup, obj)
                else:
                    self.assertIs(dup, obj)
                cls = type(obj)
                dup = copier(cls(obj))
                self.assertIs(type(dup), cls)
                self.assertIsNot(dup, obj)
                cls = type(f'My{type(obj).__name__}', (type(obj),), {})
                main = __import__('__main__')
                cls.__module__ = main.__name__
                setattr(main, cls.__name__, cls)
                dup = copier(cls(obj))
                delattr(main, cls.__name__)
                self.assertIs(type(dup), cls)
                self.assertIsNot(dup, obj)

    def testHash(self):
        for obj in self.objects:
            ob_hash = lambda: hash(obj)
            self.assertRaises(TypeError, ob_hash)

    def testInit(self):
        for i, obj in enumerate(self.objects):
            klass = type(obj)
            new = klass()
            self.assertEqual(new, obj)
            new = klass(obj)
            self.assertEqual(new, obj)
            objects = self.objects[:]
            del objects[i]
            for other in objects:
                ob_init = lambda: klass(other)
                self.assertRaises(TypeError, ob_init)
            ob_init = lambda: klass(1234)
            self.assertRaises(TypeError, ob_init)
            ob_init = lambda: klass("abc")
            self.assertRaises(TypeError, ob_init)

    def testWeakRef(self):
        for obj in self.objects:
            wr = weakref.ref(obj)
            self.assertIs(wr(), obj)
            self.assertIn(wr, weakref.getweakrefs(obj))
            wr = weakref.proxy(obj)
            self.assertIn(wr, weakref.getweakrefs(obj))

    def testSizeOf(self):
        for obj in self.objects:
            n1 = MPI._sizeof(obj)
            n2 = MPI._sizeof(type(obj))
            self.assertEqual(n1, n2)

    def testAddressOf(self):
        for obj in self.objects:
            addr = MPI._addressof(obj)
            self.assertNotEqual(addr, 0)

    def testAHandleOf(self):
        for obj in self.objects:
            if isinstance(obj, MPI.Status):
                hdl = lambda: MPI._handleof(obj)
                self.assertRaises(NotImplementedError, hdl)
                continue
            hdl = MPI._handleof(obj)
            self.assertGreaterEqual(hdl, 0)


if __name__ == '__main__':
    unittest.main()
