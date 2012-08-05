#ifndef PyMPI_CONFIG_MPICH2_H
#define PyMPI_CONFIG_MPICH2_H

#include "mpi-22.h"

/* These types are Open MPI extensions */
#define PyMPI_MISSING_MPI_LOGICAL1 1
#define PyMPI_MISSING_MPI_LOGICAL2 1
#define PyMPI_MISSING_MPI_LOGICAL4 1
#define PyMPI_MISSING_MPI_LOGICAL8 1

/* These types are difficult to implement portably */
#define PyMPI_MISSING_MPI_REAL2 1
#define PyMPI_MISSING_MPI_COMPLEX4 1

#if defined(MPI_UNWEIGHTED) && (MPICH2_NUMVERSION < 10300000)
#undef  MPI_UNWEIGHTED
#define MPI_UNWEIGHTED ((int *)0)
#endif /* MPICH2 < 1.3.0 */

#if !defined(MPICH2_NUMVERSION) || (MPICH2_NUMVERSION < 10100000)
#define PyMPI_MISSING_MPI_Type_create_f90_integer 1
#define PyMPI_MISSING_MPI_Type_create_f90_real 1
#define PyMPI_MISSING_MPI_Type_create_f90_complex 1
#endif /* MPICH2 < 1.1.0 */

#ifndef ROMIO_VERSION
#include "mpich2io.h"
#endif /* !ROMIO_VERSION */

#endif /* !PyMPI_CONFIG_MPICH2_H */
