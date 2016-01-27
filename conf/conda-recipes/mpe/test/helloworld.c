#include <stdio.h>
#include <mpi.h>
#include <mpe.h>

int main(int argc, char *argv[])
{
  MPI_Comm comm;
  int size, rank, len;
  char name[MPI_MAX_PROCESSOR_NAME];

  MPI_Init(&argc, &argv);
  MPI_Comm_dup(MPI_COMM_WORLD, &comm);

  MPI_Comm_size(comm, &size);
  MPI_Comm_rank(comm, &rank);
  MPI_Get_processor_name(name, &len);

  MPE_Seq_begin(comm, 1);
  printf("Hello, World! I am process %d of %d on %s.\n", rank, size, name);
  MPE_Seq_end(comm, 1);

  MPI_Comm_free(&comm);
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
