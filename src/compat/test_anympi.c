/* this is just for testing */

#include <mpi.h>

#define PyMPI_MISSING_MPI_VERSION
#define PyMPI_MISSING_MPI_SUBVERSION
#define PyMPI_MISSING_MPI_GET_VERSION
#define PyMPI_MISSING_MPI_INIT_THREAD
#define PyMPI_MISSING_MPI_QUERY_THREAD
#define PyMPI_MISSING_MPI_IS_THREAD_MAIN
#define PyMPI_MISSING_MPI_STATUS_IGNORE
#define PyMPI_MISSING_MPI_STATUSES_IGNORE
#define PyMPI_MISSING_MPI_TYPE_GET_EXTENT
#define PyMPI_MISSING_MPI_TYPE_DUP
#define PyMPI_MISSING_MPI_TYPE_CREATE_SUBARRAY
#define PyMPI_MISSING_MPI_TYPE_CREATE_DARRAY
#define PyMPI_MISSING_MPI_ALLOC_MEM
#define PyMPI_MISSING_MPI_FREE_MEM

#include "anympi.h"

#if !defined(MPI_VERSION)
#error "'MPI_VERSION' not defined"
#endif

#if !defined(MPI_SUBVERSION)
#error "'MPI_SUBVERSION' not defined"
#endif

#if !defined(MPI_Get_version)
#error "'MPI_Get_version' not defined"
#endif

#if !defined(MPI_Init_thread)
#error "'MPI_Init_thread' not defined"
#endif

#if !defined(MPI_Query_thread)
#error "'MPI_Query_thread' not defined"
#endif

#if !defined(MPI_Is_thread_main)
#error "'MPI_Is_thread_main' not defined"
#endif

#if !defined(MPI_STATUS_IGNORE)
#error "'MPI_STATUS_IGNORE' not defined"
#endif

#if !defined(MPI_STATUSES_IGNORE)
#error "'MPI_STATUSES_IGNORE' not defined"
#endif

#if !defined(MPI_Type_get_extent)
#error "'MPI_Type_get_extent' not defined"
#endif

#if !defined(MPI_Type_dup)
#error "'MPI_Type_dup' not defined"
#endif

#if !defined(MPI_Type_create_subarray)
#error "'MPI_Type_create_subarray' not defined"
#endif

#if !defined(MPI_Type_create_darray)
#error "'MPI_Type_create_darray' not defined"
#endif

#if !defined(MPI_Alloc_mem)
#error "'MPI_Alloc_mem' not defined"
#endif

#if !defined(MPI_Free_mem)
#error "'MPI_Free_mem' not defined"
#endif

int main(int argc, char *argv[])
{ 
  return 0; 
}
