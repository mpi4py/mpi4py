#if defined(MPI_VERSION) && (MPI_VERSION < 3)

#define PyMPI_MISSING_MPI_COMBINER_HINDEXED_BLOCK
#define PyMPI_MISSING_MPI_Type_create_hindexed_block 1

#define PyMPI_MISSING_MPI_Message 1
#define PyMPI_MISSING_MPI_MESSAGE_NULL 1
#define PyMPI_MISSING_MPI_MESSAGE_NO_PROC 1
#define PyMPI_MISSING_MPI_Message_c2f 1
#define PyMPI_MISSING_MPI_Message_f2c 1
#define PyMPI_MISSING_MPI_Mprobe 1
#define PyMPI_MISSING_MPI_Improbe 1
#define PyMPI_MISSING_MPI_Mrecv 1
#define PyMPI_MISSING_MPI_Imrecv 1

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

#define PyMPI_MISSING_MPI_Comm_dup_with_info 1
#define PyMPI_MISSING_MPI_Comm_idup 1
#define PyMPI_MISSING_MPI_Comm_create_group 1
#define PyMPI_MISSING_MPI_COMM_TYPE_SHARED 1
#define PyMPI_MISSING_MPI_Comm_split_type 1
#define PyMPI_MISSING_MPI_Comm_set_info 1
#define PyMPI_MISSING_MPI_Comm_get_info 1

#define PyMPI_MISSING_MPI_MAX_LIBRARY_VERSION_STRING 1
#define PyMPI_MISSING_MPI_Get_library_version 1
#define PyMPI_MISSING_MPI_INFO_ENV 1

#endif /* MPI < 3.0 */
