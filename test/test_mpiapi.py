from mpi4py import MPI
import mpiunittest as unittest
import os, re, sys
import subprocess as sp
import shutil

mod_file = MPI.__file__
pxd_file = os.path.join(os.path.dirname(mod_file), 'libmpi.pxd')

mpi_small_count_allowed = [
    'MPI_Op_create',
]

mpi_fortran = [
    'MPI_Type_create_f90_integer',
    'MPI_Type_create_f90_real',
    'MPI_Type_create_f90_complex',
]

mpi_deprecated = [
    'MPI_Attr_delete',
    'MPI_Attr_get',
    'MPI_Attr_put',
    'MPI_Info_get',
    'MPI_Info_get_valuelen',
    'MPI_Keyval_create',
    'MPI_Keyval_free',
]

mpi_removed = [
    'MPI_Address',
    'MPI_Errhandler_create',
    'MPI_Errhandler_get',
    'MPI_Errhandler_set',
    'MPI_Type_extent',
    'MPI_Type_hindexed',
    'MPI_Type_hvector',
    'MPI_Type_lb',
    'MPI_Type_struct',
    'MPI_Type_ub',
]

mpi_missing = []

if MPI.Get_version() < (4, 1):
    mpi_missing += [
        f'MPI_Remove_error_{func}'
        for func in ('class', 'code', 'string')
    ]
    mpi_missing += [
        f'MPI_Status_{func}_{attr}'
        for func in ('get', 'set')
        for attr in ('source', 'tag', 'error')
    ]
    mpi_missing += [
        f'MPI_Request_get_status_{func}'
        for func in ('any', 'all', 'some')
    ]
    mpi_missing += [
        f'MPI_Buffer_{func}'
        for func in ('flush', 'iflush')
    ] + [
        f'MPI_{cls}_{func}_buffer{kind}'
        for cls in ('Comm', 'Session')
        for func in ('attach', 'detach', 'flush', 'iflush')
        for kind in (('',) if 'flush' in func else ('', '_c'))
    ]
    mpi_missing += [
        'MPI_Type_get_value_index',
        'MPI_Get_hw_resource_info',
    ]

if MPI.Get_version() < (6, 0):
    mpi_missing += [
        'MPI_Comm_ack_failed',
        'MPI_Comm_agree',
        'MPI_Comm_get_failed',
        'MPI_Comm_iagree',
        'MPI_Comm_is_revoked',
        'MPI_Comm_ishrink',
        'MPI_Comm_revoke',
        'MPI_Comm_shrink',
    ]
name, version = MPI.get_vendor()
if name == 'MPICH' and version < (4, 0, 3):
    mpi_missing += [
        'MPI_Status_set_elements_c',
    ]


@unittest.skipMPI('MPI(<4.0)')
class TestMPIAPI(unittest.TestCase):

    MPINAME = r"MPI_[A-Z][a-z0-9_]+"

    def get_api_symbols(self):
        regex = re.compile(rf"^\s*int\s+({self.MPINAME})\s*\(")
        api_symbols = set()
        with open(pxd_file) as fh:
            for line in fh:
                match = regex.search(line)
                if match:
                    sym = match.groups()[0]
                    api_symbols.add(sym)
        return api_symbols

    def get_mod_symbols(self):
        nm = shutil.which('nm')
        nm_flags = ['-Pu']
        if sys.platform == 'linux':
            nm_flags.append('-D')
        cmd = [nm, *nm_flags, mod_file]
        out = sp.check_output(cmd, close_fds=False)
        nm_output = out.decode()

        regex = re.compile(rf"^_?({self.MPINAME}) U.*$")
        mod_symbols = set()
        for line in nm_output.split("\n"):
            match = regex.search(line)
            if match:
                sym = match.groups()[0]
                mod_symbols.add(sym)
        return mod_symbols

    @unittest.skipIf(shutil.which('nm') is None, 'nm')
    @unittest.skipUnless(hasattr(os, 'posix_spawn'), 'os.posix_spawn')
    def testLargeCountSymbols(self):
        api_symbols = self.get_api_symbols()
        large_count = {sym for sym in api_symbols if sym.endswith("_c")}
        mpi_symbols = self.get_mod_symbols()

        for sym in mpi_small_count_allowed:
            self.assertIn(sym, mpi_symbols)
        mpi_symbols.difference_update(mpi_small_count_allowed)

        small_count = {sym[:-2] for sym in large_count}
        bad_symbols = set.intersection(small_count, mpi_symbols)
        self.assertFalse(bad_symbols)


    @unittest.skipIf(shutil.which('nm') is None, 'nm')
    @unittest.skipUnless(hasattr(os, 'posix_spawn'), 'os.posix_spawn')
    def testSymbolCoverage(self):
        api_symbols = self.get_api_symbols()
        mod_symbols = self.get_mod_symbols()
        self.assertTrue(api_symbols)
        self.assertTrue(mod_symbols)

        uncovered = set.difference(api_symbols, mod_symbols)
        uncovered.difference_update(mpi_deprecated)
        uncovered.difference_update(mpi_removed)
        uncovered.difference_update(mpi_missing)
        for sym in mod_symbols:
            if sym.endswith("_c"):
                uncovered.discard(sym[:-2])
                uncovered.discard(sym[:-2] + '_x')
            if sym.endswith("_x"):
                uncovered.discard(sym[:-2])
                uncovered.discard(sym[:-2] + '_c')
        if MPI.REAL == MPI.DATATYPE_NULL or MPI.REAL.Get_size() == 0:
            uncovered.difference_update(mpi_fortran)
        if name == 'MPICH' and MPI.DISPLACEMENT_CURRENT == 0:
            mpiio = re.compile('MPI_(File_.*|Register_datarep)')
            uncovered = set(filter( lambda s: not mpiio.match(s), uncovered))
        self.assertFalse(uncovered)


if __name__ == '__main__':
    unittest.main()
