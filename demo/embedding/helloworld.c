#include <mpi.h>
#include <Python.h>

static const char helloworld[] = \
  "from mpi4py import MPI                                \n"
  "hwmess = 'Hello, World! I am process %d of %d on %s.' \n"
  "myrank = MPI.COMM_WORLD.Get_rank()                    \n"
  "nprocs = MPI.COMM_WORLD.Get_size()                    \n"
  "procnm = MPI.Get_processor_name()                     \n"
  "print (hwmess % (myrank, nprocs, procnm))             \n"
  "";

int main(int argc, char *argv[])
{
  MPI_Init(&argc, &argv);
  Py_Initialize();
  PyRun_SimpleString(helloworld);
  Py_Finalize();
  MPI_Finalize();
  return 0;
}
