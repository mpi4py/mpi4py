/* this is just for testing */

#include <mpi.h>

#ifndef DEINO_MPI
#define DEINO_MPI
#endif

#ifndef Py_PYTHON_H
#define Py_PYTHON_H
#define Py_GetProgramName() 0
#endif

#include "deinompi.h"

#if !defined(MPI_Init)
#error "'MPI_Init' not defined"
#endif

#if !defined(MPI_Init_thread)
#error "'MPI_Init_thread' not defined"
#endif

int main(int argc, char *argv[])
{ 
  return 0; 
}
