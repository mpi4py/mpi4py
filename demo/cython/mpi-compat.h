/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

#ifndef MPI_COMPAT_H
#define MPI_COMPAT_H

#include <mpi.h>

#if (MPI_VERSION < 3) && !defined(PyMPI_HAVE_MPI_Message)
typedef void *PyMPI_MPI_Message;
#define MPI_Message PyMPI_MPI_Message
#endif

#endif/*MPI_COMPAT_H*/
