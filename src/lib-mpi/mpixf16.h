#ifndef PyMPI_HAVE_MPI_FLOAT16_T

#if defined(OPEN_MPI)
#include <mpi-ext.h>
#endif

#if defined(MPIX_C_FLOAT16)
#undef  MPI_FLOAT16_T
#define MPI_FLOAT16_T MPIX_C_FLOAT16
#elif defined(MPIX_SHORT_FLOAT)
#undef  MPI_FLOAT16_T
#define MPI_FLOAT16_T MPIX_SHORT_FLOAT
#endif

#endif

#ifndef PyMPI_HAVE_MPI_BFLOAT16_T

#if defined(MPIX_BFLOAT16)
#undef  MPI_BFLOAT16_T
#define MPI_BFLOAT16_T MPIX_BFLOAT16
#endif

#endif
