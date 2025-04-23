import os
import pathlib
import sys

wrkdir = pathlib.Path(__file__).parent
topdir = wrkdir.parent.parent
srcdir = topdir / "src"
cfgdir = topdir / "conf"

sys.path.insert(0, os.fspath(cfgdir))
from mpiapigen import Generator  # noqa: E402

generator = Generator()
libmpi_pxd = srcdir / "mpi4py" / "libmpi.pxd"
generator.parse_file(libmpi_pxd)
libmpi_h = wrkdir / "libmpi.h"
generator.dump_header_h(libmpi_h)

# from io import StringIO
# libmpi_h = StringIO()
# generator.dump_header_h(libmpi_h)
# print libmpi_h.read()

libmpi_c = wrkdir / "libmpi.c.in"
with libmpi_c.open("w", encoding="utf-8") as f:
    f.write(f"""\
#include <mpi.h>
#include "{srcdir}/lib-mpi.h"
""")
