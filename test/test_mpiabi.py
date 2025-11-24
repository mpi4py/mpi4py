import mpitestutil as testutil
import mpiunittest as unittest

from mpi4py import MPI


class TestMPIABI(unittest.TestCase):
    #
    def testGetVersion(self):
        version = MPI.Get_abi_version()
        self.assertTrue(version >= (1, 0) or version == (-1, -1))

    def testGetInfo(self):
        info = MPI.Get_abi_info()
        for typename in (
            "aint",
            "count",
            "offset",
        ):
            with self.subTest(typename=typename):
                key = f"mpi_{typename}_size"
                sizestr = info.Get(key)
                self.assertIsNotNone(sizestr)
                datatype = getattr(MPI, typename.upper())
                if testutil.has_datatype(datatype):
                    self.assertEqual(datatype.Get_size(), int(sizestr))
        info.Free()

    def testGetFortranInfo(self):
        info = MPI.Get_abi_fortran_info()
        if info == MPI.INFO_NULL:
            return
        for typename in (
            "logical",
            "integer",
            "real",
            "double_precision",
        ):
            with self.subTest(typename=typename):
                key = f"mpi_{typename}_size"
                sizestr = info.Get(key)
                self.assertIsNotNone(sizestr)
                datatype = getattr(MPI, typename.upper())
                if testutil.has_datatype(datatype):
                    self.assertEqual(datatype.Get_size(), int(sizestr))
        str2bool = {"true": True, "false": False}
        for typeclass, typesizes in (
            ("logical", (1, 2, 4, 8, 16)),
            ("integer", (1, 2, 4, 8, 16)),
            ("real", (2, 4, 8, 16)),
            ("complex", (4, 8, 16, 32)),
            ("double_complex", ("",)),
        ):
            for typesize in typesizes:
                typename = f"{typeclass}{typesize}"
                datatype = getattr(MPI, typename.upper())
                if unittest.is_mpi("impi"):
                    if typename in {"real2", "complex4"}:
                        if datatype == MPI.DATATYPE_NULL:
                            continue
                with self.subTest(typename=typename):
                    key = f"mpi_{typename}_supported"
                    supported = info.Get(key)
                    self.assertIn(supported, ("true", "false"))
                    self.assertEqual(
                        testutil.has_datatype(datatype),
                        str2bool[supported],
                    )
        info.Free()

    @unittest.skipIf(MPI.Get_abi_version() < (1, 0), "mpi-abi")
    def testIntConstant(self):
        for attr, value in (
            ("ERR_LASTCODE", 0x3FFF),
            ("ANY_SOURCE", -1),
            ("ANY_TAG", -2),
            ("PROC_NULL", -3),
            ("ROOT", -4),
            ("UNDEFINED", -32766),
            ("THREAD_SINGLE", 0),
            ("THREAD_FUNNELED", 1024),
            ("THREAD_SERIALIZED", 2048),
            ("THREAD_MULTIPLE", 4096),
            ("ORDER_C", 0xC),
            ("ORDER_FORTRAN", 0xF),
        ):
            const = getattr(MPI, attr)
            self.assertEqual(const, value)

    @unittest.skipIf(MPI.Get_abi_version() < (1, 0), "mpi-abi")
    def testBufferConstant(self):
        for attr, value in (
            ("BOTTOM", 0),
            ("IN_PLACE", 1),
            ("BUFFER_AUTOMATIC", 2),
        ):
            obj = getattr(MPI, attr)
            self.assertEqual(obj, value)
            addr = MPI.Get_address(obj)
            self.assertEqual(addr, value)

    @unittest.skipIf(MPI.Get_abi_version() < (1, 0), "mpi-abi")
    def testIntHandle(self):
        for attr in dir(MPI):
            obj = getattr(MPI, attr)
            if isinstance(obj, type):
                continue
            if not hasattr(obj, "toint"):
                continue
            intval = obj.toint()
            self.assertGreater(intval, 0)
            self.assertLess(intval, 4096)
            handle = obj.tohandle()
            self.assertEqual(handle, intval)


if __name__ == "__main__":
    unittest.main()
