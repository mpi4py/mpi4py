from mpi4py import MPI
import mpiunittest as unittest
import sys


class TestObjModel(unittest.TestCase):

    objects = [
        MPI.DATATYPE_NULL,
        MPI.REQUEST_NULL,
        MPI.INFO_NULL,
        MPI.ERRHANDLER_NULL,
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
            self.assertTrue(obj1 == obj2)
            del objects[i]
            for obj2 in objects:
                self.assertFalse(obj1 == obj2)
                self.assertFalse(obj2 == obj1)
            self.assertFalse(None == obj1 )
            self.assertFalse(obj1 == None )
            self.assertFalse(obj1 == True )
            self.assertFalse(obj1 == False)
            self.assertFalse(obj1 == 12345)
            self.assertFalse(obj1 == "abc")
            self.assertFalse(obj1 == [123])
            self.assertFalse(obj1 == (1,2))
            self.assertFalse(obj1 == {0:0})
            self.assertFalse(obj1 == set())

    def testNe(self):
        for i, obj1 in enumerate(self.objects):
            objects = self.objects[:]
            obj2 = objects[i]
            self.assertFalse(obj1 != obj2)
            del objects[i]
            for obj2 in objects:
                self.assertTrue (obj1 != obj2)
            self.assertTrue(None != obj1 )
            self.assertTrue(obj1 != None )
            self.assertTrue(obj1 != True )
            self.assertTrue(obj1 != False)
            self.assertTrue(obj1 != 12345)
            self.assertTrue(obj1 != "abc")
            self.assertTrue(obj1 != [123])
            self.assertTrue(obj1 != (1,2))
            self.assertTrue(obj1 != {0:0})
            self.assertTrue(obj1 != set())

    def testBool(self):
        for obj in self.objects:
            self.assertFalse(not not obj)
            self.assertTrue(not obj)
            self.assertFalse(obj)

    def testHash(self):
        try:
            hash(MPI.COMM_NULL)
        except TypeError:
            pass
        else:
            if hasattr(sys, 'pypy_version_info'): return
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


if __name__ == '__main__':
    unittest.main()
