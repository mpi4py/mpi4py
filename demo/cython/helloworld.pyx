# cython: language_level=3str

# ---------

# Python-level module import
# (file: mpi4py/MPI.*.so)

from mpi4py import MPI

# Python-level objects and code

size  = MPI.COMM_WORLD.Get_size()
rank  = MPI.COMM_WORLD.Get_rank()
pname = MPI.Get_processor_name()

hwmess = "Hello, World! I am process %d of %d on %s."
print (hwmess % (rank, size, pname))

# ---------

# Cython-level cimport
# this make available mpi4py's Python extension types
# (file:  mpi4py/MPI.pxd)

from mpi4py cimport MPI
from mpi4py.MPI cimport Intracomm as IntracommType

from mpi4py.libmpi cimport MPI_Comm_size
from mpi4py.libmpi cimport MPI_Comm_rank
from mpi4py.libmpi cimport MPI_MAX_PROCESSOR_NAME
from mpi4py.libmpi cimport MPI_Get_processor_name

# C-level cdef, typed, Python objects

cdef MPI.Comm WORLD = MPI.COMM_WORLD
cdef IntracommType SELF = MPI.COMM_SELF

cdef int ierr0 = 0

cdef int size0 = 0
ierr0 = MPI_Comm_size(WORLD.ob_mpi, &size0)

cdef int rank0 = 0
ierr0 = MPI_Comm_rank(WORLD.ob_mpi, &rank0)

cdef int rlen0 = 0
cdef char pname0[MPI_MAX_PROCESSOR_NAME]
ierr0 = MPI_Get_processor_name(pname0, &rlen0)
pname0[rlen0] = 0  # just in case ;-)

hwmess = "Hello, World! I am process %d of %d on %s."
print (hwmess % (rank0, size0, pname0.decode()))

# ---------

# Cython-level cimport with PXD file
# this make available the native MPI C API
# with namespace-protection (stuff accessed as mpi.XXX)
# (file: mpi4py/libmpi.pxd)

from mpi4py cimport libmpi as mpi

cdef mpi.MPI_Comm world1 = WORLD.ob_mpi

cdef int ierr1 = 0

cdef int size1 = 0
ierr1 = mpi.MPI_Comm_size(mpi.MPI_COMM_WORLD, &size1)

cdef int rank1 = 0
ierr1 = mpi.MPI_Comm_rank(mpi.MPI_COMM_WORLD, &rank1)

cdef int rlen1 = 0
cdef char pname1[mpi.MPI_MAX_PROCESSOR_NAME]
ierr1 = mpi.MPI_Get_processor_name(pname1, &rlen1)
pname1[rlen1] = 0  # just in case ;-)

hwmess = "Hello, World! I am process %d of %d on %s."
print (hwmess % (rank1, size1, pname1.decode()))

# ---------
