from libmpi import ffi, lib

NULL   = ffi.NULL
size_p = ffi.new('int*')
rank_p = ffi.new('int*')
nlen_p = ffi.new('int*')
name_p = ffi.new('char[]', lib.MPI_MAX_PROCESSOR_NAME);

lib.MPI_Init(NULL, NULL);

lib.MPI_Comm_size(lib.MPI_COMM_WORLD, size_p)
lib.MPI_Comm_rank(lib.MPI_COMM_WORLD, rank_p)
lib.MPI_Get_processor_name(name_p, nlen_p)

size = size_p[0]
rank = rank_p[0]
nlen = nlen_p[0]
name = ffi.string(name_p[0:nlen])

print("Hello, World! I am process %d of %d on %s."
      % (rank, size, name))

lib.MPI_Finalize()
