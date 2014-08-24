#ifndef PyMPI_CONFIG_MSMPI_H
#define PyMPI_CONFIG_MSMPI_H

#include "mpi-11.h"
#include "mpi-12.h"
#include "mpi-20.h"
#include "mpi-22.h"
#include "mpi-30.h"

#if defined(MPICH_NAME)
#undef PyMPI_HAVE_MPI_REAL2
#undef PyMPI_HAVE_MPI_COMPLEX4
#endif

#undef PyMPI_HAVE_MPI_Type_create_f90_integer
#undef PyMPI_HAVE_MPI_Type_create_f90_real
#undef PyMPI_HAVE_MPI_Type_create_f90_complex

#endif /* !PyMPI_CONFIG_MSMPI_H */
