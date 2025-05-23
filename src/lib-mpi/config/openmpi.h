#ifndef PyMPI_CONFIG_OPENMPI_H
#define PyMPI_CONFIG_OPENMPI_H

#include "mpiapi.h"

#ifndef OMPI_HAVE_FORTRAN_LOGICAL1
#define OMPI_HAVE_FORTRAN_LOGICAL1 0
#endif
#ifndef OMPI_HAVE_FORTRAN_LOGICAL2
#define OMPI_HAVE_FORTRAN_LOGICAL2 0
#endif
#ifndef OMPI_HAVE_FORTRAN_LOGICAL4
#define OMPI_HAVE_FORTRAN_LOGICAL4 0
#endif
#ifndef OMPI_HAVE_FORTRAN_LOGICAL8
#define OMPI_HAVE_FORTRAN_LOGICAL8 0
#endif
#ifndef OMPI_HAVE_FORTRAN_LOGICAL16
#define OMPI_HAVE_FORTRAN_LOGICAL16 0
#endif

#if !OMPI_HAVE_FORTRAN_LOGICAL1
#undef PyMPI_HAVE_MPI_LOGICAL1
#endif
#if !OMPI_HAVE_FORTRAN_LOGICAL2
#undef PyMPI_HAVE_MPI_LOGICAL2
#endif
#if !OMPI_HAVE_FORTRAN_LOGICAL4
#undef PyMPI_HAVE_MPI_LOGICAL4
#endif
#if !OMPI_HAVE_FORTRAN_LOGICAL8
#undef PyMPI_HAVE_MPI_LOGICAL8
#endif
#if !OMPI_HAVE_FORTRAN_LOGICAL16
#undef PyMPI_HAVE_MPI_LOGICAL16
#endif
#if !OMPI_HAVE_FORTRAN_INTEGER1
#undef PyMPI_HAVE_MPI_INTEGER1
#endif
#if !OMPI_HAVE_FORTRAN_INTEGER2
#undef PyMPI_HAVE_MPI_INTEGER2
#endif
#if !OMPI_HAVE_FORTRAN_INTEGER4
#undef PyMPI_HAVE_MPI_INTEGER4
#endif
#if !OMPI_HAVE_FORTRAN_INTEGER8
#undef PyMPI_HAVE_MPI_INTEGER8
#endif
#if !OMPI_HAVE_FORTRAN_INTEGER16
#undef PyMPI_HAVE_MPI_INTEGER16
#endif
#if !OMPI_HAVE_FORTRAN_REAL2
#undef PyMPI_HAVE_MPI_REAL2
#undef PyMPI_HAVE_MPI_COMPLEX4
#endif
#if !OMPI_HAVE_FORTRAN_REAL4
#undef PyMPI_HAVE_MPI_REAL4
#undef PyMPI_HAVE_MPI_COMPLEX8
#endif
#if !OMPI_HAVE_FORTRAN_REAL8
#undef PyMPI_HAVE_MPI_REAL8
#undef PyMPI_HAVE_MPI_COMPLEX16
#endif
#if !OMPI_HAVE_FORTRAN_REAL16
#undef PyMPI_HAVE_MPI_REAL16
#undef PyMPI_HAVE_MPI_COMPLEX32
#endif

#ifdef OMPI_PROVIDE_MPI_FILE_INTERFACE
#if OMPI_PROVIDE_MPI_FILE_INTERFACE == 0
#include "mpiio.h"
#endif
#endif

#if (defined(OMPI_MAJOR_VERSION) && \
     defined(OMPI_MINOR_VERSION) && \
     defined(OMPI_RELEASE_VERSION))
#define OMPI_NUMVERSION (OMPI_MAJOR_VERSION*10000 + \
                         OMPI_MINOR_VERSION*100 + \
                         OMPI_RELEASE_VERSION)
#else
#define OMPI_NUMVERSION (10100)
#endif

#if MPI_VERSION < 3

#if OMPI_NUMVERSION >= 10700
#define PyMPI_HAVE_MPI_Message 1
#define PyMPI_HAVE_MPI_MESSAGE_NULL 1
#define PyMPI_HAVE_MPI_MESSAGE_NO_PROC 1
#define PyMPI_HAVE_MPI_Message_c2f 1
#define PyMPI_HAVE_MPI_Message_f2c 1
#define PyMPI_HAVE_MPI_Mprobe 1
#define PyMPI_HAVE_MPI_Improbe 1
#define PyMPI_HAVE_MPI_Mrecv 1
#define PyMPI_HAVE_MPI_Imrecv 1
#define PyMPI_HAVE_MPI_Ibarrier 1
#define PyMPI_HAVE_MPI_Ibcast 1
#define PyMPI_HAVE_MPI_Igather 1
#define PyMPI_HAVE_MPI_Igatherv 1
#define PyMPI_HAVE_MPI_Iscatter 1
#define PyMPI_HAVE_MPI_Iscatterv 1
#define PyMPI_HAVE_MPI_Iallgather 1
#define PyMPI_HAVE_MPI_Iallgatherv 1
#define PyMPI_HAVE_MPI_Ialltoall 1
#define PyMPI_HAVE_MPI_Ialltoallv 1
#define PyMPI_HAVE_MPI_Ialltoallw 1
#define PyMPI_HAVE_MPI_Ireduce 1
#define PyMPI_HAVE_MPI_Iallreduce 1
#define PyMPI_HAVE_MPI_Ireduce_scatter_block 1
#define PyMPI_HAVE_MPI_Ireduce_scatter 1
#define PyMPI_HAVE_MPI_Iscan 1
#define PyMPI_HAVE_MPI_Iexscan 1
#define PyMPI_HAVE_MPI_MAX_LIBRARY_VERSION_STRING 1
#define PyMPI_HAVE_MPI_Get_library_version 1
#endif /* OMPI >= 1.7.0 */

#if OMPI_NUMVERSION >= 10704
#define PyMPI_HAVE_MPI_Neighbor_allgather 1
#define PyMPI_HAVE_MPI_Neighbor_allgatherv 1
#define PyMPI_HAVE_MPI_Neighbor_alltoall 1
#define PyMPI_HAVE_MPI_Neighbor_alltoallv 1
#define PyMPI_HAVE_MPI_Neighbor_alltoallw 1
#define PyMPI_HAVE_MPI_Ineighbor_allgather 1
#define PyMPI_HAVE_MPI_Ineighbor_allgatherv 1
#define PyMPI_HAVE_MPI_Ineighbor_alltoall 1
#define PyMPI_HAVE_MPI_Ineighbor_alltoallv 1
#define PyMPI_HAVE_MPI_Ineighbor_alltoallw 1
#endif /* OMPI >= 1.7.4 */

#endif

#if MPI_VERSION == 3

#if OMPI_NUMVERSION <= 10705
#undef PyMPI_HAVE_MPI_Comm_set_info
#undef PyMPI_HAVE_MPI_Comm_get_info
#undef PyMPI_HAVE_MPI_WEIGHTS_EMPTY
#undef PyMPI_HAVE_MPI_ERR_RMA_SHARED
#endif /* OMPI <= 1.7.5 */

#endif

#if MPI_VERSION == 3
#if OMPI_NUMVERSION >= 50000

#define PyMPI_HAVE_MPI_Pready 1
#define PyMPI_HAVE_MPI_Pready_range 1
#define PyMPI_HAVE_MPI_Pready_list 1
#define PyMPI_HAVE_MPI_Parrived 1
#define PyMPI_HAVE_MPI_Info_create_env 1
#define PyMPI_HAVE_MPI_Info_get_string 1
#define PyMPI_HAVE_MPI_ERRORS_ABORT 1
#define PyMPI_HAVE_MPI_Session 1
#define PyMPI_HAVE_MPI_SESSION_NULL 1
#define PyMPI_HAVE_MPI_Session_c2f 1
#define PyMPI_HAVE_MPI_Session_f2c 1
#define PyMPI_HAVE_MPI_MAX_PSET_NAME_LEN 1
#define PyMPI_HAVE_MPI_Session_init 1
#define PyMPI_HAVE_MPI_Session_finalize 1
#define PyMPI_HAVE_MPI_Session_get_num_psets 1
#define PyMPI_HAVE_MPI_Session_get_nth_pset 1
#define PyMPI_HAVE_MPI_Session_get_info 1
#define PyMPI_HAVE_MPI_Session_get_pset_info 1
#define PyMPI_HAVE_MPI_Group_from_session_pset 1
#define PyMPI_HAVE_MPI_Session_errhandler_function 1
#define PyMPI_HAVE_MPI_Session_create_errhandler 1
#define PyMPI_HAVE_MPI_Session_get_errhandler 1
#define PyMPI_HAVE_MPI_Session_set_errhandler 1
#define PyMPI_HAVE_MPI_Session_call_errhandler 1
#define PyMPI_HAVE_MPI_Isendrecv 1
#define PyMPI_HAVE_MPI_Isendrecv_replace 1
#define PyMPI_HAVE_MPI_Psend_init 1
#define PyMPI_HAVE_MPI_Precv_init 1
#define PyMPI_HAVE_MPI_Barrier_init 1
#define PyMPI_HAVE_MPI_Bcast_init 1
#define PyMPI_HAVE_MPI_Gather_init 1
#define PyMPI_HAVE_MPI_Gatherv_init 1
#define PyMPI_HAVE_MPI_Scatter_init 1
#define PyMPI_HAVE_MPI_Scatterv_init 1
#define PyMPI_HAVE_MPI_Allgather_init 1
#define PyMPI_HAVE_MPI_Allgatherv_init 1
#define PyMPI_HAVE_MPI_Alltoall_init 1
#define PyMPI_HAVE_MPI_Alltoallv_init 1
#define PyMPI_HAVE_MPI_Alltoallw_init 1
#define PyMPI_HAVE_MPI_Reduce_init 1
#define PyMPI_HAVE_MPI_Allreduce_init 1
#define PyMPI_HAVE_MPI_Reduce_scatter_block_init 1
#define PyMPI_HAVE_MPI_Reduce_scatter_init 1
#define PyMPI_HAVE_MPI_Scan_init 1
#define PyMPI_HAVE_MPI_Exscan_init 1
#define PyMPI_HAVE_MPI_Neighbor_allgather_init 1
#define PyMPI_HAVE_MPI_Neighbor_allgatherv_init 1
#define PyMPI_HAVE_MPI_Neighbor_alltoall_init 1
#define PyMPI_HAVE_MPI_Neighbor_alltoallv_init 1
#define PyMPI_HAVE_MPI_Neighbor_alltoallw_init 1
#define PyMPI_HAVE_MPI_Comm_idup_with_info 1
#define PyMPI_HAVE_MPI_MAX_STRINGTAG_LEN 1
#define PyMPI_HAVE_MPI_Comm_create_from_group 1
#define PyMPI_HAVE_MPI_COMM_TYPE_HW_GUIDED 1
#define PyMPI_HAVE_MPI_COMM_TYPE_HW_UNGUIDED 1
#define PyMPI_HAVE_MPI_Intercomm_create_from_groups 1
#define PyMPI_HAVE_MPI_ERR_PROC_ABORTED 1
#define PyMPI_HAVE_MPI_ERR_VALUE_TOO_LARGE 1
#define PyMPI_HAVE_MPI_ERR_SESSION 1
#define PyMPI_HAVE_MPI_F_SOURCE 1
#define PyMPI_HAVE_MPI_F_TAG 1
#define PyMPI_HAVE_MPI_F_ERROR 1
#define PyMPI_HAVE_MPI_F_STATUS_SIZE 1

#endif
#endif

#if MPI_VERSION < 5

#ifdef MPI_ERR_REVOKED
#define PyMPI_HAVE_MPI_ERR_REVOKED 1
#endif
#ifdef MPI_ERR_PROC_FAILED
#define PyMPI_HAVE_MPI_ERR_PROC_FAILED 1
#endif
#ifdef MPI_ERR_PROC_FAILED_PENDING
#define PyMPI_HAVE_MPI_ERR_PROC_FAILED_PENDING 1
#endif

#endif

#endif /* !PyMPI_CONFIG_OPENMPI_H */
