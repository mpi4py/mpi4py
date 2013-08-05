#if defined(MS_WINDOWS)
#if defined(MSMPI_VER) || (defined(MPICH2) && defined(MPIAPI))
  #define MS_MPI 1
#endif
#if (defined(MS_MPI) || defined(DEINO_MPI)) && !defined(MPICH2)
  #define MPICH2 1
#endif
#endif
#if defined(MPICH_NAME) && (MPICH_NAME==3)
  #define MPICH3 1
#endif
#if defined(MPICH_NAME) && (MPICH_NAME==1)
  #define MPICH1 1
#endif

#if defined(MS_WINDOWS) && !defined(MPIAPI)
#if defined(MPI_CALL) /* DeinoMPI */
  #define MPIAPI MPI_CALL
#endif
#endif
#if !defined(MPIAPI)
  #define MPIAPI
#endif

/* XXX describe */
#if defined(HAVE_CONFIG_H)
#include "config/config.h"
#elif defined(MPICH3)
#include "config/mpich3.h"
#elif defined(MPICH2)
#include "config/mpich2.h"
#elif defined(OPEN_MPI)
#include "config/openmpi.h"
#else /* Unknown MPI*/
#include "config/unknown.h"
#endif

#ifdef PyMPI_MISSING_MPI_Type_create_f90_integer
#undef PyMPI_HAVE_MPI_Type_create_f90_integer
#endif
#ifdef PyMPI_MISSING_MPI_Type_create_f90_real
#undef PyMPI_HAVE_MPI_Type_create_f90_real
#endif
#ifdef PyMPI_MISSING_MPI_Type_create_f90_complex
#undef PyMPI_HAVE_MPI_Type_create_f90_complex
#endif
