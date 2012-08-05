#if defined(MPI_VERSION) && (MPI_VERSION < 3)

#define PyMPI_MISSING_MPI_Ibarrier 1
#define PyMPI_MISSING_MPI_Ibcast 1
#define PyMPI_MISSING_MPI_Igather 1
#define PyMPI_MISSING_MPI_Igatherv 1
#define PyMPI_MISSING_MPI_Iscatter 1
#define PyMPI_MISSING_MPI_Iscatterv 1
#define PyMPI_MISSING_MPI_Iallgather 1
#define PyMPI_MISSING_MPI_Iallgatherv 1
#define PyMPI_MISSING_MPI_Ialltoall 1
#define PyMPI_MISSING_MPI_Ialltoallv 1
#define PyMPI_MISSING_MPI_Ialltoallw 1
#define PyMPI_MISSING_MPI_Ireduce 1
#define PyMPI_MISSING_MPI_Iallreduce 1
#define PyMPI_MISSING_MPI_Ireduce_scatter_block 1
#define PyMPI_MISSING_MPI_Ireduce_scatter 1
#define PyMPI_MISSING_MPI_Iscan 1
#define PyMPI_MISSING_MPI_Iexscan 1

#endif /* MPI < 3.0 */
