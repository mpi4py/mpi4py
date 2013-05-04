#ifndef PyMPI_CONFIG_UNKNOWN_H
#define PyMPI_CONFIG_UNKNOWN_H

/* ------------------------------------------------------------------------- */

#include "mpi-11.h"
#include "mpi-12.h"
#include "mpi-20.h"
#include "mpi-22.h"
#include "mpi-30.h"

/* ------------------------------------------------------------------------- */

/* These types are difficult to implement portably */
#undef PyMPI_HAVE_MPI_INTEGER16
#undef PyMPI_HAVE_MPI_REAL2
#undef PyMPI_HAVE_MPI_COMPLEX4

/* These types are not available in MPICH(1) */
#if defined(MPICH_NAME) && (MPICH_NAME==1)
#undef PyMPI_HAVE_MPI_INTEGER1
#undef PyMPI_HAVE_MPI_INTEGER2
#undef PyMPI_HAVE_MPI_INTEGER4
#undef PyMPI_HAVE_MPI_REAL4
#undef PyMPI_HAVE_MPI_REAL8
#endif

/* ------------------------------------------------------------------------- */

#endif /* !PyMPI_CONFIG_UNKNOWN_H */
