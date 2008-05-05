/* this is just for testing */
#include <mpi.h>

#ifndef LAM_MPI
#define LAM_MPI
#endif

#include "lammpi.h"

#if !defined(MPI_Errhandler_get)
#error "'MPI_Errhandler_get' not defined"
#endif

#if !defined(MPI_Comm_get_errhandler)
#error "'MPI_Comm_get_errhandler' not defined"
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
