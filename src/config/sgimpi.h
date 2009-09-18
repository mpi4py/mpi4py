#ifndef PyMPI_CONFIG_SGIMPI_H
#define PyMPI_CONFIG_SGIMPI_H

#define PyMPI_MISSING_MPI_ROOT 1
#define PyMPI_MISSING_MPI_WCHAR 1
#define PyMPI_MISSING_MPI_SIGNED_CHAR 1
#define PyMPI_MISSING_MPI_UNSIGNED_LONG_LONG 1
#define PyMPI_MISSING_MPI_Type_create_indexed_block 1
#define PyMPI_MISSING_MPI_Type_create_f90_integer 1
#define PyMPI_MISSING_MPI_Type_create_f90_real 1
#define PyMPI_MISSING_MPI_Type_create_f90_complex 1
#define PyMPI_MISSING_MPI_TYPECLASS_INTEGER 1
#define PyMPI_MISSING_MPI_TYPECLASS_REAL 1
#define PyMPI_MISSING_MPI_TYPECLASS_COMPLEX 1
#define PyMPI_MISSING_MPI_Type_match_size 1
#define PyMPI_MISSING_MPI_Pack_external 1
#define PyMPI_MISSING_MPI_Unpack_external 1
#define PyMPI_MISSING_MPI_Pack_external_size 1
#define PyMPI_MISSING_MPI_REPLACE 1
#define PyMPI_MISSING_MPI_Comm_errhandler_fn 1
#define PyMPI_MISSING_MPI_Comm_create_errhandler 1
#define PyMPI_MISSING_MPI_Comm_call_errhandler 1
#define PyMPI_MISSING_MPI_Comm_get_errhandler 1
#define PyMPI_MISSING_MPI_Comm_set_errhandler 1
#define PyMPI_MISSING_MPI_LASTUSEDCODE 1
#define PyMPI_MISSING_MPI_ALLTOALLW 1
#define PyMPI_MISSING_MPI_EXSCAN 1
#define PyMPI_MISSING_MPI_COMM_JOIN 1
/*#define PyMPI_MISSING_MPI_ARGV_NULL 1*/
/*#define PyMPI_MISSING_MPI_ARGVS_NULL 1*/
/*#define PyMPI_MISSING_MPI_ERRCODES_IGNORE 1*/
#define PyMPI_MISSING_MPI_Win_errhandler_fn 1
#define PyMPI_MISSING_MPI_Win_create_errhandler 1
#define PyMPI_MISSING_MPI_Win_call_errhandler 1
#define PyMPI_MISSING_MPI_File_errhandler_fn 1
#define PyMPI_MISSING_MPI_File_create_errhandler 1
#define PyMPI_MISSING_MPI_File_call_errhandler 1
#define PyMPI_MISSING_MPI_Datarep_conversion_function 1
#define PyMPI_MISSING_MPI_Datarep_extent_function 1
#define PyMPI_MISSING_MPI_Register_datarep 1
#define PyMPI_MISSING_MPI_Add_error_class 1
#define PyMPI_MISSING_MPI_Add_error_code 1
#define PyMPI_MISSING_MPI_Add_error_string 1
#define PyMPI_MISSING_MPI_F_STATUS_IGNORE 1
#define PyMPI_MISSING_MPI_F_STATUSES_IGNORE 1
#define PyMPI_MISSING_MPI_Status_c2f 1
#define PyMPI_MISSING_MPI_Status_f2c 1
#define PyMPI_MISSING_MPI_Errhandler_c2f 1
#define PyMPI_MISSING_MPI_Errhandler_f2c 1

#if defined(_ABIN32) && _ABIN32
#define PyMPI_MISSING_MPI_WIN_NULL 1
#define PyMPI_MISSING_MPI_Win_free 1
#define PyMPI_MISSING_MPI_Win_create 1
#define PyMPI_MISSING_MPI_Win_get_group 1
#define PyMPI_MISSING_MPI_Get 1
#define PyMPI_MISSING_MPI_Put 1
#define PyMPI_MISSING_MPI_Accumulate 1
#define PyMPI_MISSING_MPI_MODE_NOCHECK 1
#define PyMPI_MISSING_MPI_MODE_NOSTORE 1
#define PyMPI_MISSING_MPI_MODE_NOPUT 1
#define PyMPI_MISSING_MPI_MODE_NOPRECEDE 1
#define PyMPI_MISSING_MPI_MODE_NOSUCCEED 1
#define PyMPI_MISSING_MPI_Win_fence 1
#define PyMPI_MISSING_MPI_Win_post 1
#define PyMPI_MISSING_MPI_Win_start 1
#define PyMPI_MISSING_MPI_Win_complete 1
#define PyMPI_MISSING_MPI_Win_lock 1
#define PyMPI_MISSING_MPI_Win_unlock 1
#define PyMPI_MISSING_MPI_Win_wait 1
#define PyMPI_MISSING_MPI_Win_test 1
#define PyMPI_MISSING_MPI_Win_c2f 1
#define PyMPI_MISSING_MPI_Win_f2c 1
#endif /* !_ABIN32 */

#endif /* !PyMPI_CONFIG_SGIMPI_H */
