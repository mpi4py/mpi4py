/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

#ifndef PyMPI_MPIUNI_H
#define PyMPI_MPIUNI_H

#include <petscconf.h>
#undef PETSC_HAVE_HIP
#undef PETSC_HAVE_CUDA
#undef PETSC_HAVE_FORTRAN
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
