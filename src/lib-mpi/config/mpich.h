#ifndef PyMPI_CONFIG_MPICH_H
#define PyMPI_CONFIG_MPICH_H

#include "mpiapi.h"

#if defined(MPIX_TYPECLASS_LOGICAL)
#define MPI_TYPECLASS_LOGICAL MPIX_TYPECLASS_LOGICAL
#define PyMPI_HAVE_MPI_TYPECLASS_LOGICAL 1
#endif

/* These types may not be available */
#if defined(MPIX_LOGICAL1)
#define MPI_LOGICAL1 MPIX_LOGICAL1
#define MPI_LOGICAL2 MPIX_LOGICAL2
#define MPI_LOGICAL4 MPIX_LOGICAL4
#define MPI_LOGICAL8 MPIX_LOGICAL8
#define MPI_LOGICAL16 MPIX_LOGICAL16
#define PyMPI_HAVE_MPI_LOGICAL1 1
#define PyMPI_HAVE_MPI_LOGICAL2 1
#define PyMPI_HAVE_MPI_LOGICAL4 1
#define PyMPI_HAVE_MPI_LOGICAL8 1
#define PyMPI_HAVE_MPI_LOGICAL16 1
#endif

/* These types may not be available */
#ifndef MPI_REAL2
#undef PyMPI_HAVE_MPI_REAL2
#endif
#ifndef MPI_MPI_COMPLEX4
#undef PyMPI_HAVE_MPI_COMPLEX4
#endif

/* MPI I/O may not be available */
#ifndef ROMIO_VERSION
#include "mpi-io.h"
#endif

#endif /* !PyMPI_CONFIG_MPICH_H */
