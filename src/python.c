/* $Id: python.c,v 1.1 2006/10/20 22:47:43 dalcinl Exp $ */

#include <Python.h>

#ifdef __FreeBSD__
#include <floatingpoint.h>
#endif

#define MPICH_IGNORE_CXX_SEEK
#define OMPI_IGNORE_CXX_SEEK
#include <mpi.h>


/* macro for MPI error checking */
#define CHKIERR(MPI_CALL)          \
  do {                             \
    ierr = (MPI_CALL);             \
    if (ierr != MPI_SUCCESS)       \
      goto fail;                   \
  } while(0)


int main(int argc, char **argv)
{
  int ierr   = 0; /* MPI error code       */
  int status = 0; /* Python return status */

#ifdef __FreeBSD__
  /* 754 requires that FP exceptions run in "no stop" mode by default,
   * and until C vendors implement C99's ways to control FP exceptions,
   * Python requires non-stop mode.  Alas, some platforms enable FP
   * exceptions by default.  Here we disable them.
   */
  fp_except_t m;
  m = fpgetmask();
  fpsetmask(m & ~FP_X_OFL);
#endif

  /* -------------------------------------------------------------- */
  /* Initialize MPI                                                 */
  /* -------------------------------------------------------------- */
  { /* Perhaps MPI is already initialized of finalized.
     * I know, this does not make any sense ...                     */
    int initialized=1, finalized=1;
    MPI_Initialized(&initialized);
    MPI_Finalized(&finalized);
    if (!initialized && !finalized) {
#if 1
      CHKIERR( MPI_Init(&argc, &argv) );
#else /* room for the future */
      int required = MPI_THREAD_MULTIPLE;
      int provided = MPI_THREAD_SINGLE;
      CHKIERR( MPI_Init_thread(&argc, &argv, required, &provided) );
#endif
    }
  }
  /* -------------------------------------------------------------- */

  /* -------------------------------------------------------------- */
  /* Command Line Arguments                                         */
  /* -------------------------------------------------------------- */
  /* XXX I should broadcast command line arguments here !!!         */
  /* -------------------------------------------------------------- */

  /* -------------------------------------------------------------- */
  /* Python main                                                    */
  /* -------------------------------------------------------------- */
  status = Py_Main(argc, argv);
  /* -------------------------------------------------------------- */

  /* -------------------------------------------------------------- */
  /* Finalize MPI                                                   */
  /* -------------------------------------------------------------- */
  { /* Perhaps some previous call (from Python) finalized MPI.
     * Should we inform about that? It is not good practice ...     */
    int initialized=1, finalized=1;
    MPI_Initialized(&initialized);
    MPI_Finalized(&finalized);
    if (initialized && !finalized) CHKIERR( MPI_Finalize() );
  }
  /* -------------------------------------------------------------- */

  return status;

  /* -------------------------------------------------------------- */
  /* Handle MPI error                                               */
  /* -------------------------------------------------------------- */
 fail:
  {
    char msgstr[MPI_MAX_ERROR_STRING+1] = { '\0' };
    int msglen = 0;
    int initialized = 0, finalized = 1;
    MPI_Initialized(&initialized);
    MPI_Finalized(&finalized);
    if (initialized && !finalized) {
      MPI_Error_string(ierr, msgstr, &msglen);
    } else {
      strncpy(msgstr, "unknown", MPI_MAX_ERROR_STRING);
    }
    msgstr[MPI_MAX_ERROR_STRING] = '\0';
    fflush(stderr);
    fprintf(stderr, "\n"
	    "MPI_Init()/MPI_Finalize() failed\n. "
	    "error code: %d, error string: %s"
	    "\n", ierr, msgstr);
    fflush(stderr);
    exit(ierr);
    return ierr;
  }
  /* -------------------------------------------------------------- */

}

/*
   Local variables:
   c-basic-offset: 2
   indent-tabs-mode: nil
   End:
*/
