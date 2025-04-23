import ctypes
import operator
import os
import sys
import weakref

import mpiunittest as unittest

from mpi4py import MPI

# ruff: noqa: B023


class TestObjModel(unittest.TestCase):
    #
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
            self.assertTrue(bool(obj1 == obj2))
            self.assertFalse(bool(obj1 != obj2))
            del objects[i]
            for obj2 in objects:
                self.assertTrue(bool(obj1 != obj2))
                self.assertTrue(bool(obj2 != obj1))
                self.assertFalse(bool(obj1 == obj2))
                self.assertFalse(bool(obj2 == obj1))
            self.assertFalse(bool(None is obj1))
            self.assertFalse(bool(obj1 is None))
            self.assertFalse(bool(obj1 is True))
            self.assertFalse(bool(obj1 is False))
            self.assertFalse(bool(obj1 == 12345))
            self.assertFalse(bool(obj1 == "abc"))
            self.assertFalse(bool(obj1 == [123]))
            self.assertFalse(bool(obj1 == (1, 2)))
            self.assertFalse(bool(obj1 == {0: 0}))
            self.assertFalse(bool(obj1 == set()))

    def testNe(self):
        for i, obj1 in enumerate(self.objects):
            objects = self.objects[:]
            obj2 = objects[i]
            self.assertFalse(bool(obj1 != obj2))
            del objects[i]
            for obj2 in objects:
                self.assertTrue(bool(obj1 != obj2))
            self.assertTrue(bool(None is not obj1))
            self.assertTrue(bool(obj1 is not None))
            self.assertTrue(bool(obj1 is not True))
            self.assertTrue(bool(obj1 is not False))
            self.assertTrue(bool(obj1 != 12345))
            self.assertTrue(bool(obj1 != "abc"))
            self.assertTrue(bool(obj1 != [123]))
            self.assertTrue(bool(obj1 != (1, 2)))
            self.assertTrue(bool(obj1 != {0: 0}))
            self.assertTrue(bool(obj1 != set()))

    def testCmp(self):
        for obj in self.objects:
            for binop in ("lt", "le", "gt", "ge"):
                binop = getattr(operator, binop)
                with self.assertRaises(TypeError):
                    binop(obj, obj)

    def testBool(self):
        for obj in self.objects[1:]:
            self.assertFalse(not not obj)
            self.assertTrue(not obj)
            self.assertFalse(obj)

    def testReduce(self):
        import copy
        import pickle

        def functions(_obj):
            for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
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
                cls = type(f"My{type(obj).__name__}", (type(obj),), {})
                main = __import__("__main__")
                cls.__module__ = main.__name__
                setattr(main, cls.__name__, cls)
                dup = copier(cls(obj))
                delattr(main, cls.__name__)
                self.assertIs(type(dup), cls)
                self.assertIsNot(dup, obj)

    def testHash(self):
        for obj in self.objects:

            def ob_hash():
                return hash(obj)

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

                def ob_init():
                    return klass(other)

                self.assertRaises(TypeError, ob_init)

            def ob_init():
                return klass(1234)

            self.assertRaises(TypeError, ob_init)

            def ob_init():
                return klass("abc")

            self.assertRaises(TypeError, ob_init)

    def testWeakRef(self):
        for obj in self.objects:
            wr = weakref.ref(obj)
            self.assertIs(wr(), obj)
            self.assertIn(wr, weakref.getweakrefs(obj))
            wr = weakref.proxy(obj)
            self.assertIn(wr, weakref.getweakrefs(obj))

    def testHandle(self):
        objects = self.objects[:]
        objects += [
            MPI.INT,
            MPI.FLOAT,
            MPI.Request(MPI.REQUEST_NULL),
            MPI.Prequest(MPI.REQUEST_NULL),
            MPI.Grequest(MPI.REQUEST_NULL),
            MPI.INFO_ENV,
            MPI.GROUP_EMPTY,
            MPI.ERRORS_RETURN,
            MPI.ERRORS_ABORT,
            MPI.ERRORS_ARE_FATAL,
            MPI.COMM_SELF,
            MPI.COMM_WORLD,
        ]
        for obj in objects:
            if isinstance(obj, MPI.Status):
                continue
            self.assertGreaterEqual(obj.handle, 0)
            newobj = type(obj).fromhandle(obj.handle)
            self.assertEqual(newobj, obj)
            self.assertEqual(type(newobj), type(obj))
            self.assertEqual(newobj.handle, obj.handle)
            with self.assertRaises(AttributeError):
                newobj.handle = None
            with self.assertRaises(AttributeError):
                newobj.handle = obj.handle
            with self.assertRaises(AttributeError):
                del newobj.handle

    def testSafeFreeNull(self):
        objects = self.objects[:]
        for obj in objects:
            if isinstance(obj, MPI.Status):
                continue
            obj.free()
            self.assertFalse(obj)
            obj.free()
            self.assertFalse(obj)

    def testSafeFreeConstant(self):
        objects = [
            MPI.INT,
            MPI.LONG,
            MPI.FLOAT,
            MPI.DOUBLE,
            MPI.INFO_ENV,
            MPI.SUM,
            MPI.PROD,
            MPI.GROUP_EMPTY,
            MPI.ERRORS_ABORT,
            MPI.ERRORS_ARE_FATAL,
            MPI.ERRORS_RETURN,
            MPI.MESSAGE_NO_PROC,
            MPI.COMM_SELF,
            MPI.COMM_WORLD,
        ]
        for obj in filter(None, objects):
            self.assertTrue(obj)
            for _ in range(3):
                obj.free()
                self.assertTrue(obj)
            if not isinstance(obj, MPI.Errhandler):
                clon = type(obj)(obj)
                self.assertTrue(clon)
                for _ in range(3):
                    clon.free()
                    self.assertFalse(clon)
            if hasattr(obj, "Dup"):
                self.assertTrue(obj)
                dup = obj.Dup()
                self.assertTrue(dup)
                for _ in range(3):
                    dup.free()
                    self.assertFalse(dup)
            self.assertTrue(obj)
            for _ in range(3):
                obj.free()
                self.assertTrue(obj)

    def testSafeFreeCreated(self):
        objects = [
            MPI.COMM_SELF.Isend((None, 0, MPI.BYTE), MPI.PROC_NULL),
            MPI.Op.Create(lambda *_: None),
            MPI.COMM_SELF.Get_group(),
            MPI.COMM_SELF.Get_errhandler(),
        ]
        try:
            objects += [MPI.Info.Create()]
        except (NotImplementedError, MPI.Exception):
            pass
        if os.name == "posix":
            try:
                objects += [MPI.File.Open(MPI.COMM_SELF, "/dev/null")]
            except NotImplementedError:
                pass
        try:
            objects += [MPI.Win.Create(MPI.BOTTOM)]
        except (NotImplementedError, MPI.Exception):
            pass
        try:
            objects += [MPI.Session.Init()]
        except NotImplementedError:
            pass
        for obj in objects:
            self.assertTrue(obj)
            for _ in range(3):
                obj.free()
                self.assertFalse(obj)

    def testConstants(self):
        import pickle

        names = (
            "BOTTOM",
            "IN_PLACE",
            "BUFFER_AUTOMATIC",
        )
        for name in names:
            constant = getattr(MPI, name)
            self.assertTrue(operator.eq(constant, constant))
            self.assertTrue(operator.eq(constant, int(constant)))
            self.assertTrue(operator.ne(constant, None))
            self.assertFalse(operator.ne(constant, constant))
            self.assertFalse(operator.ne(constant, int(constant)))
            self.assertFalse(operator.eq(constant, None))
            self.assertEqual(constant, int(constant))
            self.assertEqual(hash(constant), hash(int(constant)))
            self.assertEqual(bool(constant), bool(int(constant)))
            self.assertEqual(type(constant)(), constant)
            self.assertEqual(memoryview(constant).nbytes, 0)
            self.assertEqual(MPI.Get_address(constant), constant)
            if sys.implementation.name != "pypy":
                self.assertIsNone(memoryview(constant).obj)
            with self.assertRaises(TypeError):
                constant + 1
            self.assertEqual(repr(constant), name)
            self.assertEqual(constant.__reduce__(), name)
            for protocol in range(pickle.HIGHEST_PROTOCOL):
                value = pickle.loads(pickle.dumps(constant, protocol))
                self.assertIs(type(value), type(constant))
                self.assertEqual(value, constant)
        constant = MPI.BOTTOM
        self.assertEqual(operator.index(constant), int(constant))

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

    @unittest.skipUnless(sys.implementation.name == "cpython", "cpython")
    @unittest.skipUnless(hasattr(MPI, "__pyx_capi__"), "cython")
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
            modifier = ""
            if isinstance(obj, MPI.Status):
                mpi_type = ctypes.c_void_p
                modifier = " *"
            elif MPI._sizeof(cls) == ctypes.sizeof(ctypes.c_uint32):
                mpi_type = ctypes.c_uint32
            elif MPI._sizeof(cls) == ctypes.sizeof(ctypes.c_uint64):
                mpi_type = ctypes.c_uint64

            new_functype = ctypes.PYFUNCTYPE(ctypes.py_object, mpi_type)
            get_functype = ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.py_object)
            new_capsule = pyx_capi[f"PyMPI{typename}_New"]
            get_capsule = pyx_capi[f"PyMPI{typename}_Get"]
            new_signature = f"PyObject *(MPI_{typename}{modifier})".encode()
            get_signature = f"MPI_{typename} *(PyObject *)".encode()
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


if __name__ == "__main__":
    unittest.main()
