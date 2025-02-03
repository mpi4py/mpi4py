/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

#ifndef MPI4PY_H
#define MPI4PY_H

#include <mpi.h>

#if (MPI_VERSION < 3) && !defined(PyMPI_HAVE_MPI_Message)
#if !defined(MPI_Message) && !defined(MPI_MESSAGE_NULL)
typedef void *PyMPI_MPI_Message;
#define MPI_Message PyMPI_MPI_Message
#endif
#endif

#if (MPI_VERSION < 4) && !defined(PyMPI_HAVE_MPI_Session)
#if !defined(MPI_Session) && !defined(MPI_SESSION_NULL)
typedef void *PyMPI_MPI_Session;
#define MPI_Session PyMPI_MPI_Session
#endif
#endif

#if defined(MPI4PY_LIMITED_API)
#include "pycapi.h"
#else
#include "../../MPI_api.h"
#endif

static int import_mpi4py(void) {
  return import_mpi4py__MPI();
}

#endif /* MPI4PY_H */
