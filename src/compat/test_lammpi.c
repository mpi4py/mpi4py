/* this is just for testing */
#include <mpi.h>

#define LAM_WANT_ROMIO 1

#include "lammpi.h"

#if !defined(MPI_Cancel)
#error "'MPI_Cancel' not defined"
#endif

#if !defined(MPI_Comm_disconnect)
#error "'MPI_Comm_disconnect' not defined"
#endif

#if !defined(MPI_Errhandler_get)
#error "'MPI_Errhandler_get' not defined"
#endif

#if !defined(MPI_Errhandler_set)
#error "'MPI_Errhandler_set' not defined"
#endif

#if !defined(MPI_Comm_get_errhandler)
#error "'MPI_Comm_get_errhandler' not defined"
#endif

#if !defined(MPI_Comm_set_errhandler)
#error "'MPI_Comm_set_errhandler' not defined"
#endif

#if !defined(MPI_Win_get_errhandler)
#error "'MPI_Win_get_errhandler' not defined"
#endif

#if !defined(MPI_Win_set_errhandler)
#error "'MPI_Win_set_errhandler' not defined"
#endif

#if !defined(MPI_File_get_errhandler)
#error "'MPI_File_get_errhandler' not defined"
#endif

#if !defined(MPI_File_set_errhandler)
#error "'MPI_File_set_errhandler' not defined"
#endif

#if !defined(MPI_Win_create)
#error "'MPI_Win_create' not defined"
#endif

#if !defined(MPI_Win_free)
#error "'MPI_Win_free' not defined"
#endif

#if !defined(MPI_Errhandler_free)
#error "'MPI_Errhandler_free' not defined"
#endif

#if !defined(MPI_Info_free)
#error "'MPI_Info_free' not defined"
#endif

int main(int argc, char *argv[])
{ 
  return 0; 
}
