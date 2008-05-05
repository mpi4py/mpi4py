/* this is just for testing */

#include <mpi.h>

#ifndef OPEN_MPI
#define OPEN_MPI
#define OMPI_MAJOR_VERSION 1
#define OMPI_MINOR_VERSION 1
#else
#undef  OMPI_MAJOR_VERSION
#undef  OMPI_MINOR_VERSION
#define OMPI_MAJOR_VERSION 1
#define OMPI_MINOR_VERSION 1
#endif

#include "openmpi.h"

#if !defined(MPI_Init)
#error "'MPI_Init' not defined"
#endif

#if !defined(MPI_Init_thread)
#error "'MPI_Init_thread' not defined"
#endif

#if !defined(MPI_Finalize)
#error "'MPI_Finalize' not defined"
#endif

#if !defined(MPI_File_get_errhandler)
#error "'MPI_File_get_errhandler' not defined"
#endif

#if !defined(MPI_File_set_errhandler)
#error "'MPI_File_set_errhandler' not defined"
#endif

int main(int argc, char *argv[])
{ 
  return 0; 
}
