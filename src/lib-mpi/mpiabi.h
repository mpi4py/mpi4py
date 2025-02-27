#ifndef PyMPI_MPIABI_H
#define PyMPI_MPIABI_H

PyMPI_LOCAL int pympi_numversion(void)
{
  static int numversion = 0;
  if (!numversion) {
    int ierr, version = 0, subversion = 0;
    ierr = MPI_Get_version(&version, &subversion);
    if (ierr == MPI_SUCCESS)
      numversion = 10 * version + subversion;
  }
  return numversion;
}

#if defined(CIBUILDWHEEL)
#if defined(MPI_ABI_VERSION) && MPI_ABI_VERSION >= 1
#include "mpiabi1.h"
#else
#include "mpiabi0.h"
#endif /* MPI_ABI_VERSION */
#endif /* CIBUILDWHEEL */

#endif /* PyMPI_MPIABI_H */
