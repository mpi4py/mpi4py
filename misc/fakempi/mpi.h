#if !defined(PyMPI_FAKE_MPI_H)
#define PyMPI_FAKE_MPI_H

#ifdef __GNUC__
#warning Using a fake "mpi.h" include file, just for testing!!!
#endif

#define MPI_Init(a,b)  0
#define MPI_Finalize() 0
#define MPI_Initialized(a) ((*(a)=1),0)
#define MPI_Finalized(a) ((*(a)=1),0)
#define MPI_COMM_WORLD 0
#define MPI_Abort(a,b) 0

#endif /*!PyMPI_FAKE_MPI_H */
