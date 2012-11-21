#ifndef PyMPI_CONFIG_MPICH2_H
#define PyMPI_CONFIG_MPICH2_H

/* These types are Open MPI extensions */
#define PyMPI_MISSING_MPI_LOGICAL1 1
#define PyMPI_MISSING_MPI_LOGICAL2 1
#define PyMPI_MISSING_MPI_LOGICAL4 1
#define PyMPI_MISSING_MPI_LOGICAL8 1

/* These types are difficult to implement portably */
#define PyMPI_MISSING_MPI_REAL2 1
#define PyMPI_MISSING_MPI_COMPLEX4 1

#ifndef ROMIO_VERSION
#include "mpich3-io.h"
#endif

#endif /* !PyMPI_CONFIG_MPICH2_H */
