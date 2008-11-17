/* this is just for testing */

#include <mpi.h>

#define ROMIO 1

#include "mpich1.h"

#if !defined(MPI_Init)
#error "'MPI_Init' not defined"
#endif

#if !defined(MPI_Init_thread)
#error "'MPI_Init_thread' not defined"
#endif

#if !defined(MPI_Status_set_elements)
#error "'MPI_Status_set_elements' not defined"
#endif

#if !defined(MPI_File_get_errhandler)
#error "'MPI_File_get_errhandler' not defined"
#endif

#if !defined(MPI_File_set_errhandler)
#error "'MPI_File_set_errhandler' not defined"
#endif

#if !defined(MPI_MAX_OBJECT_NAME)
#error "'MPI_MAX_OBJECT_NAME' not defined"
#endif



int main(int argc, char *argv[])
{ 
  return 0; 
}
