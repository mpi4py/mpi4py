#include <stdio.h>
#include <mpi.h>
#include <Python.h>

const char helloworld[] = \
  "from mpi4py import MPI				 \n"
  "hwmess = 'Hello, World! I am process %d of %d on %s.' \n"
  "myrank = MPI.COMM_WORLD.Get_rank()			 \n"
  "nprocs = MPI.COMM_WORLD.Get_size()			 \n"
  "procnm = MPI.Get_processor_name()			 \n"
  "print (hwmess % (myrank, nprocs, procnm))             \n"
  "";

int main(int argc, char *argv[])
{
  int ierr, rank, size;

  ierr = MPI_Init(&argc, &argv);
  ierr = MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  ierr = MPI_Comm_size(MPI_COMM_WORLD, &size);

  MPI_Barrier(MPI_COMM_WORLD);
  Py_Initialize();
  PyRun_SimpleString(helloworld);
  Py_Finalize();
  MPI_Barrier(MPI_COMM_WORLD);

  if (rank == 0) {
    printf("\n");
    fflush(stdout);
    fflush(stderr);
  }

  MPI_Barrier(MPI_COMM_WORLD);
  Py_Initialize();
  PyRun_SimpleString(helloworld);
  Py_Finalize();
  MPI_Barrier(MPI_COMM_WORLD);

  ierr = MPI_Finalize();
  return 0;
}
