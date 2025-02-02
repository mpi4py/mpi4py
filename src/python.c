/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

/* -------------------------------------------------------------------------- */

#include <Python.h>

#if defined(PYPY_VERSION)
PyAPI_FUNC(int) pypy_main_startup(int, char **);
#define Py_BytesMain pypy_main_startup
#endif

#define MPICH_IGNORE_CXX_SEEK 1
#define OMPI_IGNORE_CXX_SEEK 1
#include <mpi.h>

int main(int argc, char **argv)
{
  int status = 0, flag = 1, finalize = 0;

  /* MPI initialization */
  (void)MPI_Initialized(&flag);
  if (!flag) {
#if defined(MPI_VERSION) && (MPI_VERSION > 1)
    int required = MPI_THREAD_MULTIPLE;
    int provided = MPI_THREAD_SINGLE;
    (void)MPI_Init_thread(&argc, &argv, required, &provided);
#else
    (void)MPI_Init(&argc, &argv);
#endif
    finalize = 1;
  }

  /* Python main */
  status = Py_BytesMain(argc, argv);

  /* MPI finalization */
  (void)MPI_Finalized(&flag);
  if (!flag) {
    if (status)
      (void)MPI_Abort(MPI_COMM_WORLD, status);
    if (finalize)
      (void)MPI_Finalize();
  }

  return status;
}

/* -------------------------------------------------------------------------- */

/*
   Local variables:
   c-basic-offset: 2
   indent-tabs-mode: nil
   End:
*/
