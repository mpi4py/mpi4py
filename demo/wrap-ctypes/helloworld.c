#define MPICH_SKIP_MPICXX 1
#define OMPI_SKIP_MPICXX  1
#include <mpi.h>
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif
void sayhello(void *);
#ifdef __cplusplus
}
#endif

void sayhello(void *ptr) {
  MPI_Comm comm = *((MPI_Comm*)ptr);
  int size, rank;
  char pname[MPI_MAX_PROCESSOR_NAME]; int len;
  if (comm == MPI_COMM_NULL) {
    printf("You passed MPI_COMM_NULL !!!\n");
    return;
  }
  MPI_Comm_size(comm, &size);
  MPI_Comm_rank(comm, &rank);
  MPI_Get_processor_name(pname, &len);
  pname[len] = 0;
  printf("Hello, World! I am process %d of %d on %s.\n",
         rank, size, pname);
}
