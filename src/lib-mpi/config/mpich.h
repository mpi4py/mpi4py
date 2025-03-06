#ifndef PyMPI_CONFIG_MPICH_H
#define PyMPI_CONFIG_MPICH_H

#include "mpiapi.h"

/* These types may not be available */
#ifndef MPI_REAL2
#undef PyMPI_HAVE_MPI_REAL2
#endif
#ifndef MPI_COMPLEX4
#undef PyMPI_HAVE_MPI_COMPLEX4
#endif

/* MPI I/O may not be available */
/* https://github.com/pmodels/mpich/issues/7278 */
#if MPICH_NUMVERSION < 40300000
#ifndef ROMIO_VERSION
#include "mpiio.h"
#endif
#endif

#endif /* !PyMPI_CONFIG_MPICH_H */
