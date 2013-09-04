from libmpi import ffi
from libmpi.mpi import *

NULL   = ffi.NULL
size_p = ffi.new('int*')
rank_p = ffi.new('int*')
nlen_p = ffi.new('int*')
name_p = ffi.new('char[]', MPI_MAX_PROCESSOR_NAME);

MPI_Init(NULL, NULL);

MPI_Comm_size(MPI_COMM_WORLD, size_p)
MPI_Comm_rank(MPI_COMM_WORLD, rank_p)
MPI_Get_processor_name(name_p, nlen_p)

size = size_p[0]
rank = rank_p[0]
nlen = nlen_p[0]
name = ffi.string(name_p[0:nlen])

print("Hello, World! I am process %d of %d on %s."
      % (rank, size, name))

MPI_Finalize()
