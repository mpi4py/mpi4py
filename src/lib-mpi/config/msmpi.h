#ifndef PyMPI_CONFIG_MSMPI_H
#define PyMPI_CONFIG_MSMPI_H

#include "mpi-11.h"
#include "mpi-12.h"
#include "mpi-20.h"
#include "mpi-22.h"
#include "mpi-30.h"

#if MSMPI_VER >= 0x402
#define PyMPI_HAVE_MPI_AINT 1
#define PyMPI_HAVE_MPI_OFFSET 1
#define PyMPI_HAVE_MPI_C_BOOL 1
#define PyMPI_HAVE_MPI_INT8_T 1
#define PyMPI_HAVE_MPI_INT16_T 1
#define PyMPI_HAVE_MPI_INT32_T 1
#define PyMPI_HAVE_MPI_INT64_T 1
#define PyMPI_HAVE_MPI_UINT8_T 1
#define PyMPI_HAVE_MPI_UINT16_T 1
#define PyMPI_HAVE_MPI_UINT32_T 1
#define PyMPI_HAVE_MPI_UINT64_T 1
#define PyMPI_HAVE_MPI_C_COMPLEX 1
#define PyMPI_HAVE_MPI_C_FLOAT_COMPLEX 1
#define PyMPI_HAVE_MPI_C_DOUBLE_COMPLEX 1
#define PyMPI_HAVE_MPI_C_LONG_DOUBLE_COMPLEX 1
#define PyMPI_HAVE_MPI_REAL2 1
#define PyMPI_HAVE_MPI_COMPLEX4 1
#define PyMPI_HAVE_MPI_Reduce_local 1
#endif

#if MSMPI_VER >= 0x500
#define PyMPI_HAVE_MPI_COMM_TYPE_SHARED 1
#define PyMPI_HAVE_MPI_Comm_split_type 1
#define PyMPI_HAVE_MPI_MAX_LIBRARY_VERSION_STRING 1
#define PyMPI_HAVE_MPI_Get_library_version 1
#define PyMPI_HAVE_MPI_Win_allocate_shared 1
#define PyMPI_HAVE_MPI_Win_shared_query 1
#endif

#endif /* !PyMPI_CONFIG_MSMPI_H */
