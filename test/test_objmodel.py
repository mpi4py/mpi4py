from mpi4py import MPI
import mpiunittest as unittest
import ctypes
import operator
import weakref
import sys


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

    def testCmp(self):
        for obj in self.objects:
            for binop in ('lt', 'le', 'gt', 'ge'):
                binop = getattr(operator, binop)
                with self.assertRaises(TypeError):
                    binop(obj, obj)

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

    def testConstants(self):
        import pickle
        self.assertEqual(repr(MPI.BOTTOM), 'BOTTOM')
        self.assertEqual(repr(MPI.IN_PLACE), 'IN_PLACE')
        for name in ('BOTTOM', 'IN_PLACE'):
            constant = getattr(MPI, name)
            with self.assertRaises(ValueError):
                type(constant)(constant + 1)
            self.assertEqual(repr(constant), name)
            self.assertEqual(constant.__reduce__(), name)
            for protocol in range(pickle.HIGHEST_PROTOCOL):
                value = pickle.loads(pickle.dumps(constant, protocol))
                self.assertIs(type(value), type(constant))
                self.assertEqual(value, constant)

    def testSizeOf(self):
        for obj in self.objects:
            n1 = MPI._sizeof(obj)
            n2 = MPI._sizeof(type(obj))
            self.assertEqual(n1, n2)
        with self.assertRaises(TypeError):
            MPI._sizeof(None)

    def testAddressOf(self):
        for obj in self.objects:
            addr = MPI._addressof(obj)
            self.assertNotEqual(addr, 0)
        with self.assertRaises(TypeError):
            MPI._addressof(None)

    def testAHandleOf(self):
        for obj in self.objects:
            hdl = MPI._handleof(obj)
            self.assertGreaterEqual(hdl, 0)
        with self.assertRaises(TypeError):
            MPI._handleof(None)

    @unittest.skipUnless(sys.implementation.name == 'cpython', "cpython")
    @unittest.skipUnless(hasattr(MPI, '__pyx_capi__'), "cython")
    def testCAPI(self):
        status = MPI.Status()
        status.source = 0
        status.tag = 1
        status.error = MPI.ERR_OTHER
        extra_objects = [
            status,
            MPI.INT,
            MPI.SUM,
            MPI.INFO_ENV,
            MPI.MESSAGE_NO_PROC,
            MPI.ERRORS_RETURN,
            MPI.GROUP_EMPTY,
            MPI.COMM_SELF,
        ]

        pyapi = ctypes.pythonapi
        PyCapsule_GetPointer = pyapi.PyCapsule_GetPointer
        PyCapsule_GetPointer.restype = ctypes.c_void_p
        PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]

        pyx_capi = MPI.__pyx_capi__

        for obj in self.objects + extra_objects:
            cls = type(obj)
            if issubclass(cls, MPI.Comm):
                cls = MPI.Comm
            typename = cls.__name__
            modifier = ''
            if isinstance(obj, MPI.Status):
                mpi_type = ctypes.c_void_p
                modifier = ' *'
            elif MPI._sizeof(cls) == ctypes.sizeof(ctypes.c_uint32):
                mpi_type = ctypes.c_uint32
            elif MPI._sizeof(cls) == ctypes.sizeof(ctypes.c_uint64):
                mpi_type = ctypes.c_uint64

            new_functype = ctypes.PYFUNCTYPE(ctypes.py_object, mpi_type)
            get_functype = ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.py_object)
            new_capsule = pyx_capi[f'PyMPI{typename}_New']
            get_capsule = pyx_capi[f'PyMPI{typename}_Get']
            new_signature = f'PyObject *(MPI_{typename}{modifier})'.encode()
            get_signature = f'MPI_{typename} *(PyObject *)'.encode()
            PyCapsule_GetPointer.restype = new_functype
            pympi_new = PyCapsule_GetPointer(new_capsule, new_signature)
            PyCapsule_GetPointer.restype = get_functype
            pympi_get = PyCapsule_GetPointer(get_capsule, get_signature)
            PyCapsule_GetPointer.restype = ctypes.c_void_p

            objptr = pympi_get(obj)
            if isinstance(obj, MPI.Status):
                newarg = objptr
            else:
                newarg = mpi_type.from_address(objptr).value
            self.assertEqual(objptr, MPI._addressof(obj))
            self.assertEqual(newarg, MPI._handleof(obj))
            newobj = pympi_new(newarg)
            self.assertIs(type(newobj), type(obj))
            self.assertEqual(newobj, obj)


if __name__ == '__main__':
    unittest.main()
