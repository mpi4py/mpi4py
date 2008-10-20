#ifndef PyMPI_CONFIG_MPICH2_H
#define PyMPI_CONFIG_MPICH2_H
#if defined(MPICH_NAME) && MPICH_NAME==2

#ifndef ROMIO_VERSION
#include "mpich2io.h"
#endif /* !ROMIO_VERSION */

#endif /* !MPICH_NAME==2 */
#endif /* !PyMPI_CONFIG_MPICH2_H */
