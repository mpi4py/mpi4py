/* this is just for testing */

#include <mpi.h>

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
