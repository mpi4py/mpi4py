#if !defined(PyMPI_FAKE_MPI_H)
#define PyMPI_FAKE_MPI_H

#ifdef __GNUC__
#warning "Using a fake "mpi.h" include file, just for testing!!!"
#endif

#if !defined(PyMPI_HAVE_CONFIG_H)
#define PyMPI_HAVE_CONFIG_H
#endif

#if !defined(PyMPI_MPI_STATUSES_IGNORE_SIZE)
#define PyMPI_MPI_STATUSES_IGNORE_SIZE 4096
#endif

#endif /*!PyMPI_FAKE_MPI_H */
