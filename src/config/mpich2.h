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
#include "mpich2io.h"
#endif /* !ROMIO_VERSION */

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
#if 0 /*XXX*/
#undef  PyMPI_MISSING_MPI_Comm_dup_with_info
#undef  PyMPI_MISSING_MPI_Comm_set_info
#undef  PyMPI_MISSING_MPI_Comm_get_info
#define MPI_Comm_dup_with_info    MPIX_Comm_dup_with_info
#define MPI_Comm_set_info         MPIX_Comm_set_info
#define MPI_Comm_get_info         MPIX_Comm_get_info
#endif
/**/
#if 0 /*XXX*/
#undef  PyMPI_MISSING_MPI_MAX_LIBRARY_VERSION_STRING
#undef  PyMPI_MISSING_MPI_Get_library_version
#undef  PyMPI_MISSING_MPI_INFO_ENV
#define MPI_MAX_LIBRARY_VERSION_STRING MPIX_MAX_LIBRARY_VERSION_STRING
#define MPI_Get_library_version        MPIX_Get_library_version
#define MPI_INFO_ENV                   MPIX_INFO_ENV
#endif
/**/
#endif /* MPICH2 < 1.5*/
#endif /* MPI    < 3.0*/

#endif /* !PyMPI_CONFIG_MPICH2_H */
