#ifndef PyMPI_CONFIG_MPICH2_H
#define PyMPI_CONFIG_MPICH2_H

#define PyMPI_MISSING_MPI_LOGICAL1 1
#define PyMPI_MISSING_MPI_LOGICAL2 1
#define PyMPI_MISSING_MPI_LOGICAL4 1
#define PyMPI_MISSING_MPI_LOGICAL8 1
#define PyMPI_MISSING_MPI_REAL2 1
#define PyMPI_MISSING_MPI_COMPLEX4 1
#ifdef MS_WINDOWS
#if !defined(MPICH2_NUMVERSION) || (MPICH2_NUMVERSION < 10100000)
#define PyMPI_MISSING_MPI_Type_create_f90_integer 1
#define PyMPI_MISSING_MPI_Type_create_f90_real 1
#define PyMPI_MISSING_MPI_Type_create_f90_complex 1
#endif /* MPICH2 < 1.1.0 */
#endif /* MS_WINDOWS */
#if MPI_VERSION==2 && MPI_SUBVERSION<2
#define PyMPI_MISSING_MPI_Op_commutative 1
#define PyMPI_MISSING_MPI_Reduce_local 1
#define PyMPI_MISSING_MPI_Reduce_scatter_block 1
#endif

#ifndef ROMIO_VERSION
#include "mpich2io.h"
#endif /* !ROMIO_VERSION */

#endif /* !PyMPI_CONFIG_MPICH2_H */
