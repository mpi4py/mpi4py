/* Author:  Lisandro Dalcin
 * Contact: dalcinl@gmail.com
 */

#include <Python.h>

#ifdef __FreeBSD__
#include <floatingpoint.h>
#endif

#define MPICH_IGNORE_CXX_SEEK
#define OMPI_IGNORE_CXX_SEEK
#include <mpi.h>

#define CHKIERR(ierr) if (ierr) return -1

static int PyMPI_Main(int argc, char **argv)
{
  int sts=0, flag=0, ierr=0;

  /* MPI Initalization */
  ierr = MPI_Initialized(&flag); CHKIERR(ierr);
  if (!flag) {
#if 0 
    int required = MPI_THREAD_MULTIPLE;
    int provided = MPI_THREAD_SINGLE;
    ierr = MPI_Init_thread(&argc, &argv, required, &provided); CHKIERR(ierr);
#else
    ierr = MPI_Init(&argc, &argv); CHKIERR(ierr);
#endif
  }

  /* Python main */
#if PY_MAJOR_VERSION < 3
  sts = Py_Main(argc, argv);
#else
  #warning "this may not work Python 3 ..."
  sts = Py_Main(argc, argv);
#endif

  /* MPI finalization */
  ierr = MPI_Finalized(&flag); CHKIERR(ierr);
  if (!flag) { 
    ierr = MPI_Finalize(); CHKIERR(ierr);
  }

  /* return */
  return sts;
}


int main(int argc, char **argv)
{
#ifdef __FreeBSD__
  fp_except_t m;
  m = fpgetmask();
  fpsetmask(m & ~FP_X_OFL);
#endif
  return PyMPI_Main(argc, argv);
}


/*
   Local variables:
   c-basic-offset: 2
   indent-tabs-mode: nil
   End:
*/
