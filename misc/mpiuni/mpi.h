#ifndef PyMPI_MPIUNI_H
#define PyMPI_MPIUNI_H

#include <petscconf.h>
#undef  PETSC_HAVE_FORTRAN
#include <petsc/mpiuni/mpi.h>

#define __PETSCSYS_H
#include <stdio.h>
#include <stdlib.h>
#include <../src/sys/mpiuni/mpi.c>
#include <../src/sys/mpiuni/mpitime.c>

#endif
