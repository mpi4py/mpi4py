/* this is just for testing */

#include <mpi.h>

#ifndef MPICH_NAME
#define MPICH_NAME 2
#elif MPICH_NAME != 2
#undef MPICH_NAME
#define MPICH_NAME 2
#endif

#include "mpich2.h"

int main(int argc, char *argv[])
{ 
  return 0; 
}
