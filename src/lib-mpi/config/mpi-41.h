#if defined(MPI_VERSION)
#if (MPI_VERSION > 4) || (MPI_VERSION == 4 && MPI_SUBVERSION >= 1)

#define PyMPI_HAVE_MPI_ERR_ERRHANDLER 1

#endif
#endif
