#if defined(MPI_ABI_VERSION)
#  if MPI_ABI_VERSION < 1
#    undef MPI_ABI_VERSION
#  endif
#endif

#if !defined(MPIAPI)
#  define MPIAPI
#endif

#if defined(HAVE_PYMPICONF_H)
#include "pympiconf.h"
#elif defined(MPI_ABI_VERSION)
#include "config/mpiabi.h"
#elif defined(I_MPI_NUMVERSION)
#include "config/impi.h"
#elif defined(MSMPI_VER)
#include "config/msmpi.h"
#elif defined(MPICH_NAME) && (MPICH_NAME >= 4)
#include "config/mpich.h"
#elif defined(MPICH_NAME) && (MPICH_NAME == 3)
#include "config/mpich3.h"
#elif defined(MPICH_NAME) && (MPICH_NAME == 2)
#include "config/mpich2.h"
#elif defined(OPEN_MPI)
#include "config/openmpi.h"
#else /* Unknown MPI*/
#include "config/unknown.h"
#endif
