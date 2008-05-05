/* this is just for testing */

#include <mpi.h>

#ifndef MPICH_NAME
#define MPICH_NAME 1
#define ROMIO 1
#elif MPICH_NAME != 1
#undef MPICH_NAME
#undef ROMIO
#define MPICH_NAME 1
#define ROMIO 1
#endif

#ifndef Py_PYTHON_H
#define Py_PYTHON_H
#define Py_GetProgramName() 0
#endif

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
