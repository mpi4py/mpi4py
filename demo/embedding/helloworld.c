#include <Python.h>
#include <mpi.h>

const char helloworld[] = \
  "from mpi4py import MPI                                \n"
  "hwmess = 'Hello, World! I am process %d of %d on %s.' \n"
  "myrank = MPI.COMM_WORLD.Get_rank()                    \n"
  "nprocs = MPI.COMM_WORLD.Get_size()                    \n"
  "procnm = MPI.Get_processor_name()                     \n"
  "print (hwmess % (myrank, nprocs, procnm))             \n"
  "";

int main(int argc, char *argv[])
{
  int i, n=1;

  MPI_Init(&argc, &argv);

  for (i=0; i<n; i++) {
    Py_Initialize();
    PyRun_SimpleString(helloworld);
    Py_Finalize();
  }

  MPI_Finalize();

  Py_Initialize();
  PyRun_SimpleString("from mpi4py import MPI\n");
  Py_Finalize();

  return 0;
}
