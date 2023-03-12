import sys, os.path as p
wdir = p.abspath(p.dirname(__file__))
topdir = p.normpath(p.join(wdir, p.pardir, p.pardir))
srcdir = p.join(topdir, 'src')
sys.path.insert(0, p.join(topdir, 'conf'))

from mpiapigen import Generator
generator = Generator()
libmpi_pxd = p.join(srcdir, 'mpi4py', 'libmpi.pxd')
generator.parse_file(libmpi_pxd)
libmpi_h = p.join(wdir, 'libmpi.h')
generator.dump_header_h(libmpi_h)

#from io import StringIO
#libmpi_h = StringIO()
#generator.dump_header_h(libmpi_h)
#print libmpi_h.read()

libmpi_c = p.join(wdir, 'libmpi.c.in')
with open(libmpi_c, 'w') as f:
    f.write(f"""\
#include <mpi.h>
#include "{srcdir}/lib-mpi/config.h"
#include "{srcdir}/lib-mpi/missing.h"
#include "{srcdir}/lib-mpi/fallback.h"
#include "{srcdir}/lib-mpi/compat.h"
""")
