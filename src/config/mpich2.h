#ifndef PyMPI_CONFIG_MPICH2_H
#define PyMPI_CONFIG_MPICH2_H

#include "mpi-22.h"
#include "mpi-30.h"

/* These types are Open MPI extensions */
#define PyMPI_MISSING_MPI_LOGICAL1 1
#define PyMPI_MISSING_MPI_LOGICAL2 1
#define PyMPI_MISSING_MPI_LOGICAL4 1
#define PyMPI_MISSING_MPI_LOGICAL8 1

/* These types are difficult to implement portably */
#define PyMPI_MISSING_MPI_REAL2 1
#define PyMPI_MISSING_MPI_COMPLEX4 1

#if defined(MPI_UNWEIGHTED) && (MPICH2_NUMVERSION < 10300000)
#undef  MPI_UNWEIGHTED
#define MPI_UNWEIGHTED ((int *)0)
#endif /* MPICH2 < 1.3.0 */

#if !defined(MPICH2_NUMVERSION) || (MPICH2_NUMVERSION < 10100000)
#define PyMPI_MISSING_MPI_Type_create_f90_integer 1
#define PyMPI_MISSING_MPI_Type_create_f90_real 1
#define PyMPI_MISSING_MPI_Type_create_f90_complex 1
#endif /* MPICH2 < 1.1.0 */

#ifndef ROMIO_VERSION
#include "mpich2-io.h"
#endif

#if MPI_VERSION < 3
#if defined(MPICH2_NUMVERSION) && MPICH2_NUMVERSION >= 10500000
/**/
#if 0 /*XXX*/
#undef  PyMPI_MISSING_MPI_Count
#undef  PyMPI_MISSING_MPI_COUNT
#undef  PyMPI_MISSING_MPI_Type_size_x
#undef  PyMPI_MISSING_MPI_Type_get_extent_x
#undef  PyMPI_MISSING_MPI_Type_get_true_extent_x
#undef  PyMPI_MISSING_MPI_Get_elements_x
#undef  PyMPI_MISSING_MPI_Status_set_elements_x
#define MPI_Count                  MPIX_Count
#define MPI_COUNT                  MPIX_COUNT
#define MPI_Type_size_x            MPIX_Type_size_x
#define MPI_Type_get_extent_x      MPIX_Type_get_extent_x
#define MPI_Type_get_true_extent_x MPIX_Type_get_true_extent_x
#define MPI_Get_elements_x         MPIX_Get_elements_x
#define MPI_Status_set_elements_x  MPIX_Status_set_elements_x
#endif
/**/
#undef  PyMPI_MISSING_MPI_COMBINER_HINDEXED_BLOCK
#undef  PyMPI_MISSING_MPI_Type_create_hindexed_block
#define MPI_COMBINER_HINDEXED_BLOCK    MPIX_COMBINER_HINDEXED_BLOCK
#define MPI_Type_create_hindexed_block MPIX_Type_create_hindexed_block
/**/
#undef  PyMPI_MISSING_MPI_NO_OP
#define MPI_NO_OP MPIX_NO_OP
/**/
#undef  PyMPI_MISSING_MPI_Message
#undef  PyMPI_MISSING_MPI_MESSAGE_NULL
#undef  PyMPI_MISSING_MPI_MESSAGE_NO_PROC
#undef  PyMPI_MISSING_MPI_Message_c2f
#undef  PyMPI_MISSING_MPI_Message_f2c
#undef  PyMPI_MISSING_MPI_Mprobe
#undef  PyMPI_MISSING_MPI_Improbe
#undef  PyMPI_MISSING_MPI_Mrecv
#undef  PyMPI_MISSING_MPI_Imrecv
#define MPI_Message         MPIX_Message
#define MPI_MESSAGE_NULL    MPIX_MESSAGE_NULL
#define MPI_MESSAGE_NO_PROC MPIX_MESSAGE_NO_PROC
#define MPI_Message_c2f     MPIX_Message_c2f
#define MPI_Message_f2c     MPIX_Message_f2c
#define MPI_Mprobe          MPIX_Mprobe
#define MPI_Improbe         MPIX_Improbe
#define MPI_Mrecv           MPIX_Mrecv
#define MPI_Imrecv          MPIX_Imrecv
/**/
#undef  PyMPI_MISSING_MPI_Ibarrier
#undef  PyMPI_MISSING_MPI_Ibcast
#undef  PyMPI_MISSING_MPI_Igather
#undef  PyMPI_MISSING_MPI_Igatherv
#undef  PyMPI_MISSING_MPI_Iscatter
#undef  PyMPI_MISSING_MPI_Iscatterv
#undef  PyMPI_MISSING_MPI_Iallgather
#undef  PyMPI_MISSING_MPI_Iallgatherv
#undef  PyMPI_MISSING_MPI_Ialltoall
#undef  PyMPI_MISSING_MPI_Ialltoallv
#undef  PyMPI_MISSING_MPI_Ialltoallw
#undef  PyMPI_MISSING_MPI_Ireduce
#undef  PyMPI_MISSING_MPI_Iallreduce
#undef  PyMPI_MISSING_MPI_Ireduce_scatter_block
#undef  PyMPI_MISSING_MPI_Ireduce_scatter
#undef  PyMPI_MISSING_MPI_Iscan
#undef  PyMPI_MISSING_MPI_Iexscan
#define MPI_Ibarrier              MPIX_Ibarrier
#define MPI_Ibcast                MPIX_Ibcast
#define MPI_Igather               MPIX_Igather
#define MPI_Igatherv              MPIX_Igatherv
#define MPI_Iscatter              MPIX_Iscatter
#define MPI_Iscatterv             MPIX_Iscatterv
#define MPI_Iallgather            MPIX_Iallgather
#define MPI_Iallgatherv           MPIX_Iallgatherv
#define MPI_Ialltoall             MPIX_Ialltoall
#define MPI_Ialltoallv            MPIX_Ialltoallv
#define MPI_Ialltoallw            MPIX_Ialltoallw
#define MPI_Ireduce               MPIX_Ireduce
#define MPI_Iallreduce            MPIX_Iallreduce
#define MPI_Ireduce_scatter_block MPIX_Ireduce_scatter_block
#define MPI_Ireduce_scatter       MPIX_Ireduce_scatter
#define MPI_Iscan                 MPIX_Iscan
#define MPI_Iexscan               MPIX_Iexscan
/**/
#undef  PyMPI_MISSING_MPI_Comm_idup
#undef  PyMPI_MISSING_MPI_Comm_create_group
#undef  PyMPI_MISSING_MPI_COMM_TYPE_SHARED
#undef  PyMPI_MISSING_MPI_Comm_split_type
#define MPI_Comm_idup             MPIX_Comm_idup
#define MPI_Comm_create_group     MPIX_Comm_create_group
#define MPI_COMM_TYPE_SHARED      MPIX_COMM_TYPE_SHARED
#define MPI_Comm_split_type       MPIX_Comm_split_type
/**/
#undef  PyMPI_MISSING_MPI_WIN_CREATE_FLAVOR
#undef  PyMPI_MISSING_MPI_WIN_FLAVOR_CREATE
#undef  PyMPI_MISSING_MPI_WIN_FLAVOR_ALLOCATE
#undef  PyMPI_MISSING_MPI_WIN_FLAVOR_DYNAMIC
#undef  PyMPI_MISSING_MPI_WIN_FLAVOR_SHARED
#define MPI_WIN_CREATE_FLAVOR   MPIX_WIN_CREATE_FLAVOR
#define MPI_WIN_FLAVOR_CREATE   MPIX_WIN_FLAVOR_CREATE
#define MPI_WIN_FLAVOR_ALLOCATE MPIX_WIN_FLAVOR_ALLOCATE
#define MPI_WIN_FLAVOR_DYNAMIC  MPIX_WIN_FLAVOR_DYNAMIC
#define MPI_WIN_FLAVOR_SHARED   MPIX_WIN_FLAVOR_SHARED
#undef  PyMPI_MISSING_MPI_WIN_MODEL
#undef  PyMPI_MISSING_MPI_WIN_SEPARATE
#undef  PyMPI_MISSING_MPI_WIN_UNIFIED
#define MPI_WIN_MODEL    MPIX_WIN_MODEL
#define MPI_WIN_SEPARATE MPIX_WIN_SEPARATE
#define MPI_WIN_UNIFIED  MPIX_WIN_UNIFIED
#undef  PyMPI_MISSING_MPI_Win_allocate
#define MPI_Win_allocate MPIX_Win_allocate
#undef  PyMPI_MISSING_MPI_Win_allocate_shared
#undef  PyMPI_MISSING_MPI_Win_shared_query
#define MPI_Win_allocate_shared MPIX_Win_allocate_shared
#define MPI_Win_shared_query    MPIX_Win_shared_query
#undef  PyMPI_MISSING_MPI_Win_create_dynamic
#undef  PyMPI_MISSING_MPI_Win_attach
#undef  PyMPI_MISSING_MPI_Win_detach
#define MPI_Win_create_dynamic  MPIX_Win_create_dynamic
#define MPI_Win_attach          MPIX_Win_attach
#define MPI_Win_detach          MPIX_Win_detach

#if 0 /*XXX*/
#undef  PyMPI_MISSING_MPI_Win_set_info
#undef  PyMPI_MISSING_MPI_Win_get_info
#define MPI_Win_set_info MPIX_Win_set_info
#define MPI_Win_get_info MPIX_Win_get_info
#endif/*XXX*/
#undef  PyMPI_MISSING_MPI_Get_accumulate
#undef  PyMPI_MISSING_MPI_Fetch_and_op
#undef  PyMPI_MISSING_MPI_Compare_and_swap
#define MPI_Get_accumulate   MPIX_Get_accumulate
#define MPI_Fetch_and_op     MPIX_Fetch_and_op
#define MPI_Compare_and_swap MPIX_Compare_and_swap
#undef  PyMPI_MISSING_MPI_Rget
#undef  PyMPI_MISSING_MPI_Rput
#undef  PyMPI_MISSING_MPI_Raccumulate
#undef  PyMPI_MISSING_MPI_Rget_accumulate
#define MPI_Rget            MPIX_Rget
#define MPI_Rput            MPIX_Rput
#define MPI_Raccumulate     MPIX_Raccumulate
#define MPI_Rget_accumulate MPIX_Rget_accumulate
#undef  PyMPI_MISSING_MPI_Win_lock_all
#undef  PyMPI_MISSING_MPI_Win_unlock_all
#undef  PyMPI_MISSING_MPI_Win_flush
#undef  PyMPI_MISSING_MPI_Win_flush_all
#undef  PyMPI_MISSING_MPI_Win_flush_local
#undef  PyMPI_MISSING_MPI_Win_flush_local_all
#undef  PyMPI_MISSING_MPI_Win_sync
#define MPI_Win_lock_all        MPIX_Win_lock_all
#define MPI_Win_unlock_all      MPIX_Win_unlock_all
#define MPI_Win_flush           MPIX_Win_flush
#define MPI_Win_flush_all       MPIX_Win_flush_all
#define MPI_Win_flush_local     MPIX_Win_flush_local
#define MPI_Win_flush_local_all MPIX_Win_flush_local_all
#define MPI_Win_sync            MPIX_Win_sync
#undef  PyMPI_MISSING_MPI_ERR_RMA_RANGE
#undef  PyMPI_MISSING_MPI_ERR_RMA_ATTACH
#undef  PyMPI_MISSING_MPI_ERR_RMA_SHARED
#undef  PyMPI_MISSING_MPI_ERR_RMA_WRONG_FLAVOR
#define MPI_ERR_RMA_RANGE        MPIX_ERR_RMA_RANGE
#define MPI_ERR_RMA_ATTACH       MPIX_ERR_RMA_ATTACH
#define MPI_ERR_RMA_SHARED       MPIX_ERR_RMA_SHARED
#define MPI_ERR_RMA_WRONG_FLAVOR MPIX_ERR_RMA_WRONG_FLAVOR
/**/
#if 0 /*XXX*/
#undef  PyMPI_MISSING_MPI_Comm_dup_with_info
#undef  PyMPI_MISSING_MPI_Comm_set_info
#undef  PyMPI_MISSING_MPI_Comm_get_info
#define MPI_Comm_dup_with_info    MPIX_Comm_dup_with_info
#define MPI_Comm_set_info         MPIX_Comm_set_info
#define MPI_Comm_get_info         MPIX_Comm_get_info
#endif/*XXX*/
/**/
#if 0 /*XXX*/
#undef  PyMPI_MISSING_MPI_MAX_LIBRARY_VERSION_STRING
#undef  PyMPI_MISSING_MPI_Get_library_version
#undef  PyMPI_MISSING_MPI_INFO_ENV
#define MPI_MAX_LIBRARY_VERSION_STRING MPIX_MAX_LIBRARY_VERSION_STRING
#define MPI_Get_library_version        MPIX_Get_library_version
#define MPI_INFO_ENV                   MPIX_INFO_ENV
#endif/*XXX*/
/**/
#endif /* MPICH2 < 1.5*/
#endif /* MPI    < 3.0*/

#endif /* !PyMPI_CONFIG_MPICH2_H */
