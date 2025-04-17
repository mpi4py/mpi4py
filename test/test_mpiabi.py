from mpi4py import MPI
import mpiunittest as unittest
import mpitestutil as testutil


class TestMPIABI(unittest.TestCase):

    def testGetVersion(self):
        version = MPI.Get_abi_version()
        self.assertTrue(
            version >= (1, 0)
            or version == (-1, -1)
        )

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
            ("logical", (1, 2,  4,  8, 16)),
            ("integer", (1, 2,  4,  8, 16)),
            ("real",    (2, 4,  8, 16)),
            ("complex", (4, 8, 16, 32)),
            ("double_complex", ("",)),
        ):
            for typesize in typesizes:
                typename = f"{typeclass}{typesize}"
                datatype = getattr(MPI, typename.upper())
                with self.subTest(typename=typename):
                    key = f"mpi_{typename}_supported"
                    supported = info.Get(key)
                    self.assertIn(supported, ("true", "false"))
                    self.assertEqual(
                        testutil.has_datatype(datatype),
                        str2bool[supported],
                    )
        info.Free()


if __name__ == '__main__':
    unittest.main()
