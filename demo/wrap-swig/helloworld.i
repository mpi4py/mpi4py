%module helloworld

%{

#define MPICH_SKIP_MPICXX 1
#define OMPI_SKIP_MPICXX  1

#include <mpi.h>
#include <stdio.h>

void sayhello(MPI_Comm comm) {
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

%}

%include mpi4py/mpi4py.i

%mpi4py_typemap(Comm, MPI_Comm);

void sayhello(MPI_Comm comm);

/*
 * Local Variables:
 * mode: C
 * End:
 */
