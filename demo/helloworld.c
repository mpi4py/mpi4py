#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
  int size, rank, len;
  char name[MPI_MAX_PROCESSOR_NAME];

#if defined(MPI_VERSION) && (MPI_VERSION >= 2)
  int provided;
  MPI_Init_thread(&argc, &argv, MPI_THREAD_MULTIPLE, &provided);
#else
  MPI_Init(&argc, &argv);
#endif

  MPI_Comm_size(MPI_COMM_WORLD, &size);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Get_processor_name(name, &len);

  printf("Hello, World! I am process %d of %d on %s.\n", rank, size, name);

  MPI_Finalize();
  return 0;
}

/*
 * Local Variables:
 * mode: C
 * c-basic-offset: 2
 * indent-tabs-mode: nil
 * End:
*/
