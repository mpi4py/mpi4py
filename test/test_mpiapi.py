from mpi4py import MPI
import mpiunittest as unittest
import os, re
import subprocess as sp
import shutil

mod_file = MPI.__file__
pxd_file = os.path.join(os.path.dirname(mod_file), 'libmpi.pxd')

mpi_small_count_allowed = [
    'MPI_Op_create',
]

@unittest.skipMPI('MPI(<4.0)')
class TestMPIAPI(unittest.TestCase):

    @unittest.skipIf(shutil.which('nm') is None, 'nm')
    @unittest.skipUnless(hasattr(os, 'posix_spawn'), 'os.posix_spawn')
    def testLargeCountSymbols(self):
        mpiname = r"MPI_[A-Z][a-z0-9_]+"

        regex = re.compile(rf"^\s*int\s+({mpiname})\s*\(")
        large_count = set()
        with open(pxd_file) as fh:
            for line in fh:
                match = regex.search(line)
                if match:
                    fcn = match.groups()[0]
                    if fcn.endswith("_c"):
                        large_count.add(fcn)
        self.assertTrue(large_count)

        nm = shutil.which('nm')
        cmd = [nm, '-Pu', mod_file]
        out = sp.check_output(cmd, close_fds=False)
        nm_output = out.decode()

        regex = re.compile(rf"^_?({mpiname}) U.*$")
        mpi_symbols = set()
        for line in nm_output.split("\n"):
            match = regex.search(line)
            if match:
                fcn = match.groups()[0]
                mpi_symbols.add(fcn)
        self.assertTrue(mpi_symbols)

        for symbol in mpi_small_count_allowed:
            self.assertIn(symbol, mpi_symbols)
            mpi_symbols.remove(symbol)

        small_count = {fcn[:-2] for fcn in large_count}
        bad_symbols = set.intersection(small_count, mpi_symbols)
        self.assertFalse(bad_symbols)
