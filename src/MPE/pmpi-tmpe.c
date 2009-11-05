#include <stdio.h>
#ifdef HAVE_STDARG_H    
#include <stdarg.h>
#endif

#define MPICH_SKIP_MPICXX 1
#define OMPI_SKIP_MPICXX  1
#include <mpi.h>

#if defined(c_plusplus) || defined(__cplusplus)
extern "C" {
#endif

extern int MPE_Trace_hasBeenInit;
extern int MPE_Trace_hasBeenFinished;
static int MPE_Trace_isActive = 1;

#define TRACE_PRINTF(msg) \
if ( (MPE_Trace_hasBeenInit) && (!MPE_Trace_hasBeenFinished) ) {\
  PMPI_Comm_rank( MPI_COMM_WORLD, &llrank ); \
  printf( "[%d] %s\n", llrank, msg ); \
  fflush( stdout ); \
}

int MPI_Pcontrol( const int level, ... )
{
#ifdef HAVE_STDARG_H    
    /* Some compilers are unhappy if routines with stdargs (...) don't 
       include va_start/end */
    va_list list;
    va_start( list, level );
    MPE_Trace_isActive = (level!=0);
    va_end( list );
#else
    MPE_Trace_isActive = (level!=0);
#endif
    /* XXX This is a hack ... */
    MPE_Trace_hasBeenInit = MPE_Trace_isActive;
    return MPI_SUCCESS;
}

#if defined(MPI_VERSION) && MPI_VERSION > 1

int  MPI_Init_thread( argc, argv , required, provided)
int * argc;
char *** argv;
int required;
int * provided;
{
  int returnVal;
  int llrank;

/*
    MPI_Init_thread - prototyping replacement for MPI_Init_thread
    Trace the beginning and ending of MPI_Init_thread.
*/

  printf( "Starting MPI_Init_thread...\n" ); fflush( stdout );
  
  returnVal = PMPI_Init_thread( argc, argv , required, provided );

  MPE_Trace_hasBeenInit = 1;
  MPE_Trace_isActive = 1;

  TRACE_PRINTF( "Ending MPI_Init_thread" );

  return returnVal;
}

#endif /* MPI_VERSION > 1 */


#if defined(c_plusplus) || defined(__cplusplus)
}  /* extern "C" */
#endif
