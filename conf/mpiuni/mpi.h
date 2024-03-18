/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

#ifndef PyMPI_MPIUNI_H
#define PyMPI_MPIUNI_H

#include <petscconf.h>
#undef PETSC_HAVE_HIP
#undef PETSC_HAVE_CUDA
#undef PETSC_HAVE_FORTRAN
#undef PETSC_HAVE_I_MPI_NUMVERSION
#undef PETSC_HAVE_MVAPICH_NUMVERSION
#undef PETSC_HAVE_MVAPICH2_NUMVERSION
#undef PETSC_HAVE_MPICH_NUMVERSION
#undef PETSC_HAVE_OMPI_MAJOR_VERSION
#undef PETSC_HAVE_MSMPI_VERSION
#undef PETSC_HAVE_MPI_PROCESS_SHARED_MEMORY
#include <petscmacros.h>
#include <petsc/mpiuni/mpi.h>

#define PETSCSYS_H
#define PETSCIMPL_H
#define PETSCDEVICE_CUPM_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int PETSC_COMM_WORLD = MPI_COMM_NULL;
#include <../src/sys/mpiuni/mpi.c>
#include <../src/sys/mpiuni/mpitime.c>

#endif
