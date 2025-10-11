import os
import platform

import arrayimpl
import mpiunittest as unittest

from mpi4py import MPI


def allclose(a, b, rtol=1.0e-5, atol=1.0e-8):
    try:
        iter(a)
    except TypeError:
        a = [a]
    try:
        iter(b)
    except TypeError:
        b = [b]
    for x, y in zip(a, b):
        if x == y:
            continue
        if abs(x - y) > (atol + rtol * abs(y)):
            return False
    return True


class BaseTestPack:
    #
    COMM = MPI.COMM_NULL

    skipdtype = []

    def testPackSize(self):
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if typecode in self.skipdtype:
                    continue
                datatype = array.TypeMap[typecode]
                itemsize = datatype.Get_size()
                overhead = datatype.Pack_size(0, self.COMM)
                for count in range(10):
                    with self.subTest(count=count):
                        pack_size = datatype.Pack_size(count, self.COMM)
                        self.assertEqual(
                            pack_size - overhead, count * itemsize
                        )

    def testPackUnpack(self):
        for array, typecode1 in arrayimpl.loop():
            with arrayimpl.test(self):
                if typecode1 in self.skipdtype:
                    continue
                for typecode2 in array.TypeMap:
                    if typecode2 in self.skipdtype:
                        continue
                    datatype1 = array.TypeMap[typecode1]
                    datatype2 = array.TypeMap[typecode2]
                    for count in range(10):
                        with self.subTest(
                            typecode=(typecode1, typecode2), count=count
                        ):
                            # input and output arrays
                            iarray1 = array(range(count), typecode1).as_raw()
                            iarray2 = array(range(count), typecode2).as_raw()
                            oarray1 = array(count, typecode1, count).as_raw()
                            oarray2 = array(count, typecode2, count).as_raw()
                            # temp array for packing
                            size1 = datatype1.Pack_size(
                                len(iarray1), self.COMM
                            )
                            size2 = datatype2.Pack_size(
                                len(iarray2), self.COMM
                            )
                            tmpbuf = array(0, "b", size1 + size2 + 1).as_raw()
                            # pack input arrays
                            position = 0
                            position = datatype1.Pack(
                                iarray1, tmpbuf, position, self.COMM
                            )
                            position = datatype2.Pack(
                                iarray2, tmpbuf, position, self.COMM
                            )
                            # unpack output arrays
                            position = 0
                            position = datatype1.Unpack(
                                tmpbuf, position, oarray1, self.COMM
                            )
                            position = datatype2.Unpack(
                                tmpbuf, position, oarray2, self.COMM
                            )
                            # test
                            self.assertTrue(allclose(iarray1, oarray1))
                            self.assertTrue(allclose(iarray2, oarray2))


EXT32 = "external32"


class BaseTestPackExternal:
    #
    skipdtype = []

    def testPackSize(self):
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if typecode in self.skipdtype:
                    continue
                datatype = array.TypeMap[typecode]
                overhead = datatype.Pack_external_size(EXT32, 0)
                for count in range(10):
                    with self.subTest(count=count):
                        pack_size = datatype.Pack_external_size(EXT32, count)
                        real_size = pack_size - overhead
                        self.assertGreaterEqual(real_size, 0)

    @unittest.skipMPI("openmpi(<5.0.0)", platform.machine() == "sparc64")
    def testPackUnpackExternal(self):
        for array, typecode1 in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu("mpich", array):
                    continue
                if unittest.is_mpi_gpu("openmpi", array):
                    continue
                if unittest.is_mpi_gpu("mvapich", array):
                    continue
                if typecode1 in self.skipdtype:
                    continue
                for typecode2 in array.TypeMap:
                    if typecode2 in self.skipdtype:
                        continue
                    datatype1 = array.TypeMap[typecode1]
                    datatype2 = array.TypeMap[typecode2]
                    for count in range(1, 10):
                        with self.subTest(
                            count=count, typecode=(typecode1, typecode2)
                        ):
                            # input and output arrays
                            val = 127 if typecode1 == "b" else 255
                            iarray1 = array(val, typecode1, count).as_raw()
                            iarray2 = array(range(count), typecode2).as_raw()
                            oarray1 = array(-1, typecode1, count).as_raw()
                            oarray2 = array(-1, typecode2, count).as_raw()
                            # temp array for packing
                            size1 = datatype1.Pack_external_size(
                                EXT32, len(iarray1)
                            )
                            size2 = datatype2.Pack_external_size(
                                EXT32, len(iarray2)
                            )
                            tmpbuf = array(0, "b", size1 + size2 + 1).as_raw()
                            # pack input arrays
                            position = 0
                            position = datatype1.Pack_external(
                                EXT32, iarray1, tmpbuf, position
                            )
                            position = datatype2.Pack_external(
                                EXT32, iarray2, tmpbuf, position
                            )
                            # unpack output arrays
                            position = 0
                            position = datatype1.Unpack_external(
                                EXT32, tmpbuf, position, oarray1
                            )
                            position = datatype2.Unpack_external(
                                EXT32, tmpbuf, position, oarray2
                            )
                            # test result
                            self.assertTrue(allclose(iarray1, oarray1))
                            self.assertTrue(allclose(iarray2, oarray2))


class TestPackSelf(BaseTestPack, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestPackWorld(BaseTestPack, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("openmpi(<3.0.0)")
class TestPackExternal(BaseTestPackExternal, unittest.TestCase):
    #
    pass


name, version = MPI.get_vendor()
if name == "MPICH":
    if version < (4, 0, 0):
        BaseTestPackExternal.skipdtype += "ldgLFDG"
    if platform.architecture("")[0] == "32bit":
        BaseTestPackExternal.skipdtype += "gG"
elif name == "Open MPI":
    if version < (5, 0, 0):
        BaseTestPackExternal.skipdtype += "gG"
    if (platform.system(), platform.machine()) == ("Darwin", "arm64"):
        BaseTestPackExternal.skipdtype += "G"
elif name == "Intel MPI":
    BaseTestPackExternal.skipdtype += "lgLG"
    BaseTestPackExternal.skipdtype += "D"
    if os.name == "nt":
        BaseTestPackExternal.skipdtype += "q"
elif name == "Microsoft MPI":
    BaseTestPackExternal.skipdtype += "gFDG"
elif name == "MVAPICH":
    BaseTestPackExternal.skipdtype += "lfdgLFDG"
elif name == "MPICH2":
    BaseTestPackExternal.skipdtype += "ldgLFDG"
else:
    try:
        MPI.BYTE.Pack_external_size(EXT32, 0)
    except NotImplementedError:
        unittest.disable(BaseTestPackExternal, "mpi-ext32")


if __name__ == "__main__":
    unittest.main()
