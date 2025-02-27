/* Generated with `python conf/mpiapigen.py` */
#if defined(__linux__) || defined(__APPLE__)

#define _pympi_Pragma(arg) _Pragma(#arg)
#ifdef __linux__
#  define _pympi_WEAK(func) _pympi_Pragma(weak func)
#endif
#ifdef __APPLE__
#  define _pympi_WEAK(func) _pympi_Pragma(weak_import func)
#endif
#define _pympi_CALL(func, ...) \
(func ? func(__VA_ARGS__) : _pympi__##func(__VA_ARGS__))

#ifdef __cplusplus
extern "C"
#endif

#ifdef MPICH
PyMPI_LOCAL MPI_Fint _pympi__MPI_Type_c2f(MPI_Datatype a0) { return MPI_Type_c2f(a0); }
#undef MPI_Type_c2f
#ifndef PyMPI_HAVE_MPI_Type_c2f
extern MPI_Fint MPI_Type_c2f(MPI_Datatype a0);
#endif
_pympi_WEAK(MPI_Type_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Type_c2f(MPI_Datatype a0) { return _pympi_CALL(MPI_Type_c2f,a0); }
#define MPI_Type_c2f _pympi_MPI_Type_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Request_c2f(MPI_Request a0) { return MPI_Request_c2f(a0); }
#undef MPI_Request_c2f
#ifndef PyMPI_HAVE_MPI_Request_c2f
extern MPI_Fint MPI_Request_c2f(MPI_Request a0);
#endif
_pympi_WEAK(MPI_Request_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Request_c2f(MPI_Request a0) { return _pympi_CALL(MPI_Request_c2f,a0); }
#define MPI_Request_c2f _pympi_MPI_Request_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Message_c2f(MPI_Message a0) { return MPI_Message_c2f(a0); }
#undef MPI_Message_c2f
#ifndef PyMPI_HAVE_MPI_Message_c2f
extern MPI_Fint MPI_Message_c2f(MPI_Message a0);
#endif
_pympi_WEAK(MPI_Message_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Message_c2f(MPI_Message a0) { return _pympi_CALL(MPI_Message_c2f,a0); }
#define MPI_Message_c2f _pympi_MPI_Message_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Op_c2f(MPI_Op a0) { return MPI_Op_c2f(a0); }
#undef MPI_Op_c2f
#ifndef PyMPI_HAVE_MPI_Op_c2f
extern MPI_Fint MPI_Op_c2f(MPI_Op a0);
#endif
_pympi_WEAK(MPI_Op_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Op_c2f(MPI_Op a0) { return _pympi_CALL(MPI_Op_c2f,a0); }
#define MPI_Op_c2f _pympi_MPI_Op_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Group_c2f(MPI_Group a0) { return MPI_Group_c2f(a0); }
#undef MPI_Group_c2f
#ifndef PyMPI_HAVE_MPI_Group_c2f
extern MPI_Fint MPI_Group_c2f(MPI_Group a0);
#endif
_pympi_WEAK(MPI_Group_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Group_c2f(MPI_Group a0) { return _pympi_CALL(MPI_Group_c2f,a0); }
#define MPI_Group_c2f _pympi_MPI_Group_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Info_c2f(MPI_Info a0) { return MPI_Info_c2f(a0); }
#undef MPI_Info_c2f
#ifndef PyMPI_HAVE_MPI_Info_c2f
extern MPI_Fint MPI_Info_c2f(MPI_Info a0);
#endif
_pympi_WEAK(MPI_Info_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Info_c2f(MPI_Info a0) { return _pympi_CALL(MPI_Info_c2f,a0); }
#define MPI_Info_c2f _pympi_MPI_Info_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Comm_c2f(MPI_Comm a0) { return MPI_Comm_c2f(a0); }
#undef MPI_Comm_c2f
#ifndef PyMPI_HAVE_MPI_Comm_c2f
extern MPI_Fint MPI_Comm_c2f(MPI_Comm a0);
#endif
_pympi_WEAK(MPI_Comm_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Comm_c2f(MPI_Comm a0) { return _pympi_CALL(MPI_Comm_c2f,a0); }
#define MPI_Comm_c2f _pympi_MPI_Comm_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Win_c2f(MPI_Win a0) { return MPI_Win_c2f(a0); }
#undef MPI_Win_c2f
#ifndef PyMPI_HAVE_MPI_Win_c2f
extern MPI_Fint MPI_Win_c2f(MPI_Win a0);
#endif
_pympi_WEAK(MPI_Win_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Win_c2f(MPI_Win a0) { return _pympi_CALL(MPI_Win_c2f,a0); }
#define MPI_Win_c2f _pympi_MPI_Win_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_File_c2f(MPI_File a0) { return MPI_File_c2f(a0); }
#undef MPI_File_c2f
#ifndef PyMPI_HAVE_MPI_File_c2f
extern MPI_Fint MPI_File_c2f(MPI_File a0);
#endif
_pympi_WEAK(MPI_File_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_File_c2f(MPI_File a0) { return _pympi_CALL(MPI_File_c2f,a0); }
#define MPI_File_c2f _pympi_MPI_File_c2f
PyMPI_LOCAL MPI_Fint _pympi__MPI_Errhandler_c2f(MPI_Errhandler a0) { return MPI_Errhandler_c2f(a0); }
#undef MPI_Errhandler_c2f
#ifndef PyMPI_HAVE_MPI_Errhandler_c2f
extern MPI_Fint MPI_Errhandler_c2f(MPI_Errhandler a0);
#endif
_pympi_WEAK(MPI_Errhandler_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Errhandler_c2f(MPI_Errhandler a0) { return _pympi_CALL(MPI_Errhandler_c2f,a0); }
#define MPI_Errhandler_c2f _pympi_MPI_Errhandler_c2f
PyMPI_LOCAL MPI_Datatype _pympi__MPI_Type_f2c(MPI_Fint a0) { return MPI_Type_f2c(a0); }
#undef MPI_Type_f2c
#ifndef PyMPI_HAVE_MPI_Type_f2c
extern MPI_Datatype MPI_Type_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Type_f2c)
PyMPI_LOCAL MPI_Datatype _pympi_MPI_Type_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Type_f2c,a0); }
#define MPI_Type_f2c _pympi_MPI_Type_f2c
PyMPI_LOCAL MPI_Request _pympi__MPI_Request_f2c(MPI_Fint a0) { return MPI_Request_f2c(a0); }
#undef MPI_Request_f2c
#ifndef PyMPI_HAVE_MPI_Request_f2c
extern MPI_Request MPI_Request_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Request_f2c)
PyMPI_LOCAL MPI_Request _pympi_MPI_Request_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Request_f2c,a0); }
#define MPI_Request_f2c _pympi_MPI_Request_f2c
PyMPI_LOCAL MPI_Message _pympi__MPI_Message_f2c(MPI_Fint a0) { return MPI_Message_f2c(a0); }
#undef MPI_Message_f2c
#ifndef PyMPI_HAVE_MPI_Message_f2c
extern MPI_Message MPI_Message_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Message_f2c)
PyMPI_LOCAL MPI_Message _pympi_MPI_Message_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Message_f2c,a0); }
#define MPI_Message_f2c _pympi_MPI_Message_f2c
PyMPI_LOCAL MPI_Op _pympi__MPI_Op_f2c(MPI_Fint a0) { return MPI_Op_f2c(a0); }
#undef MPI_Op_f2c
#ifndef PyMPI_HAVE_MPI_Op_f2c
extern MPI_Op MPI_Op_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Op_f2c)
PyMPI_LOCAL MPI_Op _pympi_MPI_Op_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Op_f2c,a0); }
#define MPI_Op_f2c _pympi_MPI_Op_f2c
PyMPI_LOCAL MPI_Group _pympi__MPI_Group_f2c(MPI_Fint a0) { return MPI_Group_f2c(a0); }
#undef MPI_Group_f2c
#ifndef PyMPI_HAVE_MPI_Group_f2c
extern MPI_Group MPI_Group_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Group_f2c)
PyMPI_LOCAL MPI_Group _pympi_MPI_Group_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Group_f2c,a0); }
#define MPI_Group_f2c _pympi_MPI_Group_f2c
PyMPI_LOCAL MPI_Info _pympi__MPI_Info_f2c(MPI_Fint a0) { return MPI_Info_f2c(a0); }
#undef MPI_Info_f2c
#ifndef PyMPI_HAVE_MPI_Info_f2c
extern MPI_Info MPI_Info_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Info_f2c)
PyMPI_LOCAL MPI_Info _pympi_MPI_Info_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Info_f2c,a0); }
#define MPI_Info_f2c _pympi_MPI_Info_f2c
PyMPI_LOCAL MPI_Comm _pympi__MPI_Comm_f2c(MPI_Fint a0) { return MPI_Comm_f2c(a0); }
#undef MPI_Comm_f2c
#ifndef PyMPI_HAVE_MPI_Comm_f2c
extern MPI_Comm MPI_Comm_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Comm_f2c)
PyMPI_LOCAL MPI_Comm _pympi_MPI_Comm_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Comm_f2c,a0); }
#define MPI_Comm_f2c _pympi_MPI_Comm_f2c
PyMPI_LOCAL MPI_Win _pympi__MPI_Win_f2c(MPI_Fint a0) { return MPI_Win_f2c(a0); }
#undef MPI_Win_f2c
#ifndef PyMPI_HAVE_MPI_Win_f2c
extern MPI_Win MPI_Win_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Win_f2c)
PyMPI_LOCAL MPI_Win _pympi_MPI_Win_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Win_f2c,a0); }
#define MPI_Win_f2c _pympi_MPI_Win_f2c
PyMPI_LOCAL MPI_File _pympi__MPI_File_f2c(MPI_Fint a0) { return MPI_File_f2c(a0); }
#undef MPI_File_f2c
#ifndef PyMPI_HAVE_MPI_File_f2c
extern MPI_File MPI_File_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_File_f2c)
PyMPI_LOCAL MPI_File _pympi_MPI_File_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_File_f2c,a0); }
#define MPI_File_f2c _pympi_MPI_File_f2c
PyMPI_LOCAL MPI_Errhandler _pympi__MPI_Errhandler_f2c(MPI_Fint a0) { return MPI_Errhandler_f2c(a0); }
#undef MPI_Errhandler_f2c
#ifndef PyMPI_HAVE_MPI_Errhandler_f2c
extern MPI_Errhandler MPI_Errhandler_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Errhandler_f2c)
PyMPI_LOCAL MPI_Errhandler _pympi_MPI_Errhandler_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Errhandler_f2c,a0); }
#define MPI_Errhandler_f2c _pympi_MPI_Errhandler_f2c
#endif /* MPICH */

#ifdef OPEN_MPI
_pympi_WEAK(ompi_mpi_datatype_null)
_pympi_WEAK(ompi_mpi_packed)
_pympi_WEAK(ompi_mpi_byte)
_pympi_WEAK(ompi_mpi_aint)
_pympi_WEAK(ompi_mpi_offset)
_pympi_WEAK(ompi_mpi_count)
_pympi_WEAK(ompi_mpi_char)
_pympi_WEAK(ompi_mpi_wchar)
_pympi_WEAK(ompi_mpi_signed_char)
_pympi_WEAK(ompi_mpi_short)
_pympi_WEAK(ompi_mpi_int)
_pympi_WEAK(ompi_mpi_long)
_pympi_WEAK(ompi_mpi_long_long)
_pympi_WEAK(ompi_mpi_long_long_int)
_pympi_WEAK(ompi_mpi_unsigned_char)
_pympi_WEAK(ompi_mpi_unsigned_short)
_pympi_WEAK(ompi_mpi_unsigned)
_pympi_WEAK(ompi_mpi_unsigned_long)
_pympi_WEAK(ompi_mpi_unsigned_long_long)
_pympi_WEAK(ompi_mpi_float)
_pympi_WEAK(ompi_mpi_double)
_pympi_WEAK(ompi_mpi_long_double)
_pympi_WEAK(ompi_mpi_c_bool)
_pympi_WEAK(ompi_mpi_int8_t)
_pympi_WEAK(ompi_mpi_int16_t)
_pympi_WEAK(ompi_mpi_int32_t)
_pympi_WEAK(ompi_mpi_int64_t)
_pympi_WEAK(ompi_mpi_uint8_t)
_pympi_WEAK(ompi_mpi_uint16_t)
_pympi_WEAK(ompi_mpi_uint32_t)
_pympi_WEAK(ompi_mpi_uint64_t)
_pympi_WEAK(ompi_mpi_c_complex)
_pympi_WEAK(ompi_mpi_c_float_complex)
_pympi_WEAK(ompi_mpi_c_double_complex)
_pympi_WEAK(ompi_mpi_c_long_double_complex)
_pympi_WEAK(ompi_mpi_cxx_bool)
_pympi_WEAK(ompi_mpi_cxx_cplex)
_pympi_WEAK(ompi_mpi_cxx_dblcplex)
_pympi_WEAK(ompi_mpi_cxx_ldblcplex)
_pympi_WEAK(ompi_mpi_short_int)
_pympi_WEAK(ompi_mpi_2int)
_pympi_WEAK(ompi_mpi_long_int)
_pympi_WEAK(ompi_mpi_float_int)
_pympi_WEAK(ompi_mpi_double_int)
_pympi_WEAK(ompi_mpi_longdbl_int)
_pympi_WEAK(ompi_mpi_character)
_pympi_WEAK(ompi_mpi_logical)
_pympi_WEAK(ompi_mpi_integer)
_pympi_WEAK(ompi_mpi_real)
_pympi_WEAK(ompi_mpi_dblprec)
_pympi_WEAK(ompi_mpi_cplex)
_pympi_WEAK(ompi_mpi_dblcplex)
_pympi_WEAK(ompi_mpi_logical1)
_pympi_WEAK(ompi_mpi_logical2)
_pympi_WEAK(ompi_mpi_logical4)
_pympi_WEAK(ompi_mpi_logical8)
_pympi_WEAK(ompi_mpi_integer1)
_pympi_WEAK(ompi_mpi_integer2)
_pympi_WEAK(ompi_mpi_integer4)
_pympi_WEAK(ompi_mpi_integer8)
_pympi_WEAK(ompi_mpi_integer16)
_pympi_WEAK(ompi_mpi_real2)
_pympi_WEAK(ompi_mpi_real4)
_pympi_WEAK(ompi_mpi_real8)
_pympi_WEAK(ompi_mpi_real16)
_pympi_WEAK(ompi_mpi_complex4)
_pympi_WEAK(ompi_mpi_complex8)
_pympi_WEAK(ompi_mpi_complex16)
_pympi_WEAK(ompi_mpi_complex32)
_pympi_WEAK(ompi_request_null)
_pympi_WEAK(ompi_mpi_op_null)
_pympi_WEAK(ompi_mpi_op_max)
_pympi_WEAK(ompi_mpi_op_min)
_pympi_WEAK(ompi_mpi_op_sum)
_pympi_WEAK(ompi_mpi_op_prod)
_pympi_WEAK(ompi_mpi_op_land)
_pympi_WEAK(ompi_mpi_op_band)
_pympi_WEAK(ompi_mpi_op_lor)
_pympi_WEAK(ompi_mpi_op_bor)
_pympi_WEAK(ompi_mpi_op_lxor)
_pympi_WEAK(ompi_mpi_op_bxor)
_pympi_WEAK(ompi_mpi_op_maxloc)
_pympi_WEAK(ompi_mpi_op_minloc)
_pympi_WEAK(ompi_mpi_op_replace)
_pympi_WEAK(ompi_mpi_op_no_op)
_pympi_WEAK(ompi_mpi_group_null)
_pympi_WEAK(ompi_mpi_group_empty)
_pympi_WEAK(ompi_mpi_info_null)
_pympi_WEAK(ompi_mpi_info_env)
_pympi_WEAK(ompi_mpi_errhandler_null)
_pympi_WEAK(ompi_mpi_errors_return)
_pympi_WEAK(ompi_mpi_errors_abort)
_pympi_WEAK(ompi_mpi_errors_are_fatal)
_pympi_WEAK(ompi_mpi_instance_null)
_pympi_WEAK(ompi_mpi_comm_null)
_pympi_WEAK(ompi_mpi_comm_self)
_pympi_WEAK(ompi_mpi_comm_world)
_pympi_WEAK(ompi_message_null)
_pympi_WEAK(ompi_message_no_proc)
_pympi_WEAK(ompi_mpi_win_null)
_pympi_WEAK(ompi_mpi_file_null)
#ifdef MPI_Aint_add
#undef PyMPI_HAVE_MPI_Aint_add
#endif
#ifdef MPI_Aint_diff
#undef PyMPI_HAVE_MPI_Aint_diff
#endif
#endif /* OPEN_MPI */

PyMPI_LOCAL MPI_Aint _pympi__MPI_Aint_add(MPI_Aint a0,MPI_Aint a1) { return MPI_Aint_add(a0,a1); }
#undef MPI_Aint_add
#ifndef PyMPI_HAVE_MPI_Aint_add
extern MPI_Aint MPI_Aint_add(MPI_Aint a0,MPI_Aint a1);
#endif
_pympi_WEAK(MPI_Aint_add)
PyMPI_LOCAL MPI_Aint _pympi_MPI_Aint_add(MPI_Aint a0,MPI_Aint a1) { return _pympi_CALL(MPI_Aint_add,a0,a1); }
#define MPI_Aint_add _pympi_MPI_Aint_add

PyMPI_LOCAL MPI_Aint _pympi__MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1) { return MPI_Aint_diff(a0,a1); }
#undef MPI_Aint_diff
#ifndef PyMPI_HAVE_MPI_Aint_diff
extern MPI_Aint MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1);
#endif
_pympi_WEAK(MPI_Aint_diff)
PyMPI_LOCAL MPI_Aint _pympi_MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1) { return _pympi_CALL(MPI_Aint_diff,a0,a1); }
#define MPI_Aint_diff _pympi_MPI_Aint_diff

PyMPI_LOCAL int _pympi__MPI_Type_get_value_index(MPI_Datatype a0,MPI_Datatype a1,MPI_Datatype* a2) { return MPI_Type_get_value_index(a0,a1,a2); }
#undef MPI_Type_get_value_index
#ifndef PyMPI_HAVE_MPI_Type_get_value_index
extern int MPI_Type_get_value_index(MPI_Datatype a0,MPI_Datatype a1,MPI_Datatype* a2);
#endif
_pympi_WEAK(MPI_Type_get_value_index)
PyMPI_LOCAL int _pympi_MPI_Type_get_value_index(MPI_Datatype a0,MPI_Datatype a1,MPI_Datatype* a2) { return _pympi_CALL(MPI_Type_get_value_index,a0,a1,a2); }
#define MPI_Type_get_value_index _pympi_MPI_Type_get_value_index

PyMPI_LOCAL int _pympi__MPI_Type_contiguous_c(MPI_Count a0,MPI_Datatype a1,MPI_Datatype* a2) { return MPI_Type_contiguous_c(a0,a1,a2); }
#undef MPI_Type_contiguous_c
#ifndef PyMPI_HAVE_MPI_Type_contiguous_c
extern int MPI_Type_contiguous_c(MPI_Count a0,MPI_Datatype a1,MPI_Datatype* a2);
#endif
_pympi_WEAK(MPI_Type_contiguous_c)
PyMPI_LOCAL int _pympi_MPI_Type_contiguous_c(MPI_Count a0,MPI_Datatype a1,MPI_Datatype* a2) { return _pympi_CALL(MPI_Type_contiguous_c,a0,a1,a2); }
#define MPI_Type_contiguous_c _pympi_MPI_Type_contiguous_c

PyMPI_LOCAL int _pympi__MPI_Type_vector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4) { return MPI_Type_vector_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_vector_c
#ifndef PyMPI_HAVE_MPI_Type_vector_c
extern int MPI_Type_vector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_vector_c)
PyMPI_LOCAL int _pympi_MPI_Type_vector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_vector_c,a0,a1,a2,a3,a4); }
#define MPI_Type_vector_c _pympi_MPI_Type_vector_c

PyMPI_LOCAL int _pympi__MPI_Type_indexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return MPI_Type_indexed_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_indexed_c
#ifndef PyMPI_HAVE_MPI_Type_indexed_c
extern int MPI_Type_indexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_indexed_c)
PyMPI_LOCAL int _pympi_MPI_Type_indexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_indexed_c,a0,a1,a2,a3,a4); }
#define MPI_Type_indexed_c _pympi_MPI_Type_indexed_c

PyMPI_LOCAL int _pympi__MPI_Type_create_indexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return MPI_Type_create_indexed_block_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_create_indexed_block_c
#ifndef PyMPI_HAVE_MPI_Type_create_indexed_block_c
extern int MPI_Type_create_indexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_create_indexed_block_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_indexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_create_indexed_block_c,a0,a1,a2,a3,a4); }
#define MPI_Type_create_indexed_block_c _pympi_MPI_Type_create_indexed_block_c

PyMPI_LOCAL int _pympi__MPI_Type_create_subarray_c(int a0,MPI_Count a1[],MPI_Count a2[],MPI_Count a3[],int a4,MPI_Datatype a5,MPI_Datatype* a6) { return MPI_Type_create_subarray_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Type_create_subarray_c
#ifndef PyMPI_HAVE_MPI_Type_create_subarray_c
extern int MPI_Type_create_subarray_c(int a0,MPI_Count a1[],MPI_Count a2[],MPI_Count a3[],int a4,MPI_Datatype a5,MPI_Datatype* a6);
#endif
_pympi_WEAK(MPI_Type_create_subarray_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_subarray_c(int a0,MPI_Count a1[],MPI_Count a2[],MPI_Count a3[],int a4,MPI_Datatype a5,MPI_Datatype* a6) { return _pympi_CALL(MPI_Type_create_subarray_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Type_create_subarray_c _pympi_MPI_Type_create_subarray_c

PyMPI_LOCAL int _pympi__MPI_Type_create_darray_c(int a0,int a1,int a2,MPI_Count a3[],int a4[],int a5[],int a6[],int a7,MPI_Datatype a8,MPI_Datatype* a9) { return MPI_Type_create_darray_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Type_create_darray_c
#ifndef PyMPI_HAVE_MPI_Type_create_darray_c
extern int MPI_Type_create_darray_c(int a0,int a1,int a2,MPI_Count a3[],int a4[],int a5[],int a6[],int a7,MPI_Datatype a8,MPI_Datatype* a9);
#endif
_pympi_WEAK(MPI_Type_create_darray_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_darray_c(int a0,int a1,int a2,MPI_Count a3[],int a4[],int a5[],int a6[],int a7,MPI_Datatype a8,MPI_Datatype* a9) { return _pympi_CALL(MPI_Type_create_darray_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Type_create_darray_c _pympi_MPI_Type_create_darray_c

PyMPI_LOCAL int _pympi__MPI_Type_create_hvector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4) { return MPI_Type_create_hvector_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_create_hvector_c
#ifndef PyMPI_HAVE_MPI_Type_create_hvector_c
extern int MPI_Type_create_hvector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_create_hvector_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_hvector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_create_hvector_c,a0,a1,a2,a3,a4); }
#define MPI_Type_create_hvector_c _pympi_MPI_Type_create_hvector_c

PyMPI_LOCAL int _pympi__MPI_Type_create_hindexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return MPI_Type_create_hindexed_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_create_hindexed_c
#ifndef PyMPI_HAVE_MPI_Type_create_hindexed_c
extern int MPI_Type_create_hindexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_create_hindexed_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_hindexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_create_hindexed_c,a0,a1,a2,a3,a4); }
#define MPI_Type_create_hindexed_c _pympi_MPI_Type_create_hindexed_c

PyMPI_LOCAL int _pympi__MPI_Type_create_hindexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return MPI_Type_create_hindexed_block_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_create_hindexed_block_c
#ifndef PyMPI_HAVE_MPI_Type_create_hindexed_block_c
extern int MPI_Type_create_hindexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_create_hindexed_block_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_hindexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_create_hindexed_block_c,a0,a1,a2,a3,a4); }
#define MPI_Type_create_hindexed_block_c _pympi_MPI_Type_create_hindexed_block_c

PyMPI_LOCAL int _pympi__MPI_Type_create_struct_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3[],MPI_Datatype* a4) { return MPI_Type_create_struct_c(a0,a1,a2,a3,a4); }
#undef MPI_Type_create_struct_c
#ifndef PyMPI_HAVE_MPI_Type_create_struct_c
extern int MPI_Type_create_struct_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3[],MPI_Datatype* a4);
#endif
_pympi_WEAK(MPI_Type_create_struct_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_struct_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3[],MPI_Datatype* a4) { return _pympi_CALL(MPI_Type_create_struct_c,a0,a1,a2,a3,a4); }
#define MPI_Type_create_struct_c _pympi_MPI_Type_create_struct_c

PyMPI_LOCAL int _pympi__MPI_Type_create_resized_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Datatype* a3) { return MPI_Type_create_resized_c(a0,a1,a2,a3); }
#undef MPI_Type_create_resized_c
#ifndef PyMPI_HAVE_MPI_Type_create_resized_c
extern int MPI_Type_create_resized_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Datatype* a3);
#endif
_pympi_WEAK(MPI_Type_create_resized_c)
PyMPI_LOCAL int _pympi_MPI_Type_create_resized_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Datatype* a3) { return _pympi_CALL(MPI_Type_create_resized_c,a0,a1,a2,a3); }
#define MPI_Type_create_resized_c _pympi_MPI_Type_create_resized_c

PyMPI_LOCAL int _pympi__MPI_Type_size_c(MPI_Datatype a0,MPI_Count* a1) { return MPI_Type_size_c(a0,a1); }
#undef MPI_Type_size_c
#ifndef PyMPI_HAVE_MPI_Type_size_c
extern int MPI_Type_size_c(MPI_Datatype a0,MPI_Count* a1);
#endif
_pympi_WEAK(MPI_Type_size_c)
PyMPI_LOCAL int _pympi_MPI_Type_size_c(MPI_Datatype a0,MPI_Count* a1) { return _pympi_CALL(MPI_Type_size_c,a0,a1); }
#define MPI_Type_size_c _pympi_MPI_Type_size_c

PyMPI_LOCAL int _pympi__MPI_Type_get_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2) { return MPI_Type_get_extent_c(a0,a1,a2); }
#undef MPI_Type_get_extent_c
#ifndef PyMPI_HAVE_MPI_Type_get_extent_c
extern int MPI_Type_get_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_Type_get_extent_c)
PyMPI_LOCAL int _pympi_MPI_Type_get_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2) { return _pympi_CALL(MPI_Type_get_extent_c,a0,a1,a2); }
#define MPI_Type_get_extent_c _pympi_MPI_Type_get_extent_c

PyMPI_LOCAL int _pympi__MPI_Type_get_true_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2) { return MPI_Type_get_true_extent_c(a0,a1,a2); }
#undef MPI_Type_get_true_extent_c
#ifndef PyMPI_HAVE_MPI_Type_get_true_extent_c
extern int MPI_Type_get_true_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_Type_get_true_extent_c)
PyMPI_LOCAL int _pympi_MPI_Type_get_true_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2) { return _pympi_CALL(MPI_Type_get_true_extent_c,a0,a1,a2); }
#define MPI_Type_get_true_extent_c _pympi_MPI_Type_get_true_extent_c

PyMPI_LOCAL int _pympi__MPI_Type_get_envelope_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2,MPI_Count* a3,MPI_Count* a4,int* a5) { return MPI_Type_get_envelope_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Type_get_envelope_c
#ifndef PyMPI_HAVE_MPI_Type_get_envelope_c
extern int MPI_Type_get_envelope_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2,MPI_Count* a3,MPI_Count* a4,int* a5);
#endif
_pympi_WEAK(MPI_Type_get_envelope_c)
PyMPI_LOCAL int _pympi_MPI_Type_get_envelope_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2,MPI_Count* a3,MPI_Count* a4,int* a5) { return _pympi_CALL(MPI_Type_get_envelope_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Type_get_envelope_c _pympi_MPI_Type_get_envelope_c

PyMPI_LOCAL int _pympi__MPI_Type_get_contents_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Count a3,MPI_Count a4,int a5[],MPI_Aint a6[],MPI_Count a7[],MPI_Datatype a8[]) { return MPI_Type_get_contents_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Type_get_contents_c
#ifndef PyMPI_HAVE_MPI_Type_get_contents_c
extern int MPI_Type_get_contents_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Count a3,MPI_Count a4,int a5[],MPI_Aint a6[],MPI_Count a7[],MPI_Datatype a8[]);
#endif
_pympi_WEAK(MPI_Type_get_contents_c)
PyMPI_LOCAL int _pympi_MPI_Type_get_contents_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Count a3,MPI_Count a4,int a5[],MPI_Aint a6[],MPI_Count a7[],MPI_Datatype a8[]) { return _pympi_CALL(MPI_Type_get_contents_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Type_get_contents_c _pympi_MPI_Type_get_contents_c

PyMPI_LOCAL int _pympi__MPI_Pack_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Count* a5,MPI_Comm a6) { return MPI_Pack_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Pack_c
#ifndef PyMPI_HAVE_MPI_Pack_c
extern int MPI_Pack_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Count* a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Pack_c)
PyMPI_LOCAL int _pympi_MPI_Pack_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Count* a5,MPI_Comm a6) { return _pympi_CALL(MPI_Pack_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Pack_c _pympi_MPI_Pack_c

PyMPI_LOCAL int _pympi__MPI_Unpack_c(void* a0,MPI_Count a1,MPI_Count* a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return MPI_Unpack_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Unpack_c
#ifndef PyMPI_HAVE_MPI_Unpack_c
extern int MPI_Unpack_c(void* a0,MPI_Count a1,MPI_Count* a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Unpack_c)
PyMPI_LOCAL int _pympi_MPI_Unpack_c(void* a0,MPI_Count a1,MPI_Count* a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return _pympi_CALL(MPI_Unpack_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Unpack_c _pympi_MPI_Unpack_c

PyMPI_LOCAL int _pympi__MPI_Pack_size_c(MPI_Count a0,MPI_Datatype a1,MPI_Comm a2,MPI_Count* a3) { return MPI_Pack_size_c(a0,a1,a2,a3); }
#undef MPI_Pack_size_c
#ifndef PyMPI_HAVE_MPI_Pack_size_c
extern int MPI_Pack_size_c(MPI_Count a0,MPI_Datatype a1,MPI_Comm a2,MPI_Count* a3);
#endif
_pympi_WEAK(MPI_Pack_size_c)
PyMPI_LOCAL int _pympi_MPI_Pack_size_c(MPI_Count a0,MPI_Datatype a1,MPI_Comm a2,MPI_Count* a3) { return _pympi_CALL(MPI_Pack_size_c,a0,a1,a2,a3); }
#define MPI_Pack_size_c _pympi_MPI_Pack_size_c

PyMPI_LOCAL int _pympi__MPI_Pack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Count* a6) { return MPI_Pack_external_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Pack_external_c
#ifndef PyMPI_HAVE_MPI_Pack_external_c
extern int MPI_Pack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Count* a6);
#endif
_pympi_WEAK(MPI_Pack_external_c)
PyMPI_LOCAL int _pympi_MPI_Pack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Count* a6) { return _pympi_CALL(MPI_Pack_external_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Pack_external_c _pympi_MPI_Pack_external_c

PyMPI_LOCAL int _pympi__MPI_Unpack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Count* a3,void* a4,MPI_Count a5,MPI_Datatype a6) { return MPI_Unpack_external_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Unpack_external_c
#ifndef PyMPI_HAVE_MPI_Unpack_external_c
extern int MPI_Unpack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Count* a3,void* a4,MPI_Count a5,MPI_Datatype a6);
#endif
_pympi_WEAK(MPI_Unpack_external_c)
PyMPI_LOCAL int _pympi_MPI_Unpack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Count* a3,void* a4,MPI_Count a5,MPI_Datatype a6) { return _pympi_CALL(MPI_Unpack_external_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Unpack_external_c _pympi_MPI_Unpack_external_c

PyMPI_LOCAL int _pympi__MPI_Pack_external_size_c(char a0[],MPI_Count a1,MPI_Datatype a2,MPI_Count* a3) { return MPI_Pack_external_size_c(a0,a1,a2,a3); }
#undef MPI_Pack_external_size_c
#ifndef PyMPI_HAVE_MPI_Pack_external_size_c
extern int MPI_Pack_external_size_c(char a0[],MPI_Count a1,MPI_Datatype a2,MPI_Count* a3);
#endif
_pympi_WEAK(MPI_Pack_external_size_c)
PyMPI_LOCAL int _pympi_MPI_Pack_external_size_c(char a0[],MPI_Count a1,MPI_Datatype a2,MPI_Count* a3) { return _pympi_CALL(MPI_Pack_external_size_c,a0,a1,a2,a3); }
#define MPI_Pack_external_size_c _pympi_MPI_Pack_external_size_c

PyMPI_LOCAL int _pympi__MPI_Get_count_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2) { return MPI_Get_count_c(a0,a1,a2); }
#undef MPI_Get_count_c
#ifndef PyMPI_HAVE_MPI_Get_count_c
extern int MPI_Get_count_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_Get_count_c)
PyMPI_LOCAL int _pympi_MPI_Get_count_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2) { return _pympi_CALL(MPI_Get_count_c,a0,a1,a2); }
#define MPI_Get_count_c _pympi_MPI_Get_count_c

PyMPI_LOCAL int _pympi__MPI_Get_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2) { return MPI_Get_elements_c(a0,a1,a2); }
#undef MPI_Get_elements_c
#ifndef PyMPI_HAVE_MPI_Get_elements_c
extern int MPI_Get_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_Get_elements_c)
PyMPI_LOCAL int _pympi_MPI_Get_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2) { return _pympi_CALL(MPI_Get_elements_c,a0,a1,a2); }
#define MPI_Get_elements_c _pympi_MPI_Get_elements_c

PyMPI_LOCAL int _pympi__MPI_Status_set_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count a2) { return MPI_Status_set_elements_c(a0,a1,a2); }
#undef MPI_Status_set_elements_c
#ifndef PyMPI_HAVE_MPI_Status_set_elements_c
extern int MPI_Status_set_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count a2);
#endif
_pympi_WEAK(MPI_Status_set_elements_c)
PyMPI_LOCAL int _pympi_MPI_Status_set_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count a2) { return _pympi_CALL(MPI_Status_set_elements_c,a0,a1,a2); }
#define MPI_Status_set_elements_c _pympi_MPI_Status_set_elements_c

PyMPI_LOCAL int _pympi__MPI_Status_get_source(MPI_Status* a0,int* a1) { return MPI_Status_get_source(a0,a1); }
#undef MPI_Status_get_source
#ifndef PyMPI_HAVE_MPI_Status_get_source
extern int MPI_Status_get_source(MPI_Status* a0,int* a1);
#endif
_pympi_WEAK(MPI_Status_get_source)
PyMPI_LOCAL int _pympi_MPI_Status_get_source(MPI_Status* a0,int* a1) { return _pympi_CALL(MPI_Status_get_source,a0,a1); }
#define MPI_Status_get_source _pympi_MPI_Status_get_source

PyMPI_LOCAL int _pympi__MPI_Status_set_source(MPI_Status* a0,int a1) { return MPI_Status_set_source(a0,a1); }
#undef MPI_Status_set_source
#ifndef PyMPI_HAVE_MPI_Status_set_source
extern int MPI_Status_set_source(MPI_Status* a0,int a1);
#endif
_pympi_WEAK(MPI_Status_set_source)
PyMPI_LOCAL int _pympi_MPI_Status_set_source(MPI_Status* a0,int a1) { return _pympi_CALL(MPI_Status_set_source,a0,a1); }
#define MPI_Status_set_source _pympi_MPI_Status_set_source

PyMPI_LOCAL int _pympi__MPI_Status_get_tag(MPI_Status* a0,int* a1) { return MPI_Status_get_tag(a0,a1); }
#undef MPI_Status_get_tag
#ifndef PyMPI_HAVE_MPI_Status_get_tag
extern int MPI_Status_get_tag(MPI_Status* a0,int* a1);
#endif
_pympi_WEAK(MPI_Status_get_tag)
PyMPI_LOCAL int _pympi_MPI_Status_get_tag(MPI_Status* a0,int* a1) { return _pympi_CALL(MPI_Status_get_tag,a0,a1); }
#define MPI_Status_get_tag _pympi_MPI_Status_get_tag

PyMPI_LOCAL int _pympi__MPI_Status_set_tag(MPI_Status* a0,int a1) { return MPI_Status_set_tag(a0,a1); }
#undef MPI_Status_set_tag
#ifndef PyMPI_HAVE_MPI_Status_set_tag
extern int MPI_Status_set_tag(MPI_Status* a0,int a1);
#endif
_pympi_WEAK(MPI_Status_set_tag)
PyMPI_LOCAL int _pympi_MPI_Status_set_tag(MPI_Status* a0,int a1) { return _pympi_CALL(MPI_Status_set_tag,a0,a1); }
#define MPI_Status_set_tag _pympi_MPI_Status_set_tag

PyMPI_LOCAL int _pympi__MPI_Status_get_error(MPI_Status* a0,int* a1) { return MPI_Status_get_error(a0,a1); }
#undef MPI_Status_get_error
#ifndef PyMPI_HAVE_MPI_Status_get_error
extern int MPI_Status_get_error(MPI_Status* a0,int* a1);
#endif
_pympi_WEAK(MPI_Status_get_error)
PyMPI_LOCAL int _pympi_MPI_Status_get_error(MPI_Status* a0,int* a1) { return _pympi_CALL(MPI_Status_get_error,a0,a1); }
#define MPI_Status_get_error _pympi_MPI_Status_get_error

PyMPI_LOCAL int _pympi__MPI_Status_set_error(MPI_Status* a0,int a1) { return MPI_Status_set_error(a0,a1); }
#undef MPI_Status_set_error
#ifndef PyMPI_HAVE_MPI_Status_set_error
extern int MPI_Status_set_error(MPI_Status* a0,int a1);
#endif
_pympi_WEAK(MPI_Status_set_error)
PyMPI_LOCAL int _pympi_MPI_Status_set_error(MPI_Status* a0,int a1) { return _pympi_CALL(MPI_Status_set_error,a0,a1); }
#define MPI_Status_set_error _pympi_MPI_Status_set_error

PyMPI_LOCAL int _pympi__MPI_Request_get_status_any(int a0,MPI_Request a1[],int* a2,int* a3,MPI_Status* a4) { return MPI_Request_get_status_any(a0,a1,a2,a3,a4); }
#undef MPI_Request_get_status_any
#ifndef PyMPI_HAVE_MPI_Request_get_status_any
extern int MPI_Request_get_status_any(int a0,MPI_Request a1[],int* a2,int* a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_Request_get_status_any)
PyMPI_LOCAL int _pympi_MPI_Request_get_status_any(int a0,MPI_Request a1[],int* a2,int* a3,MPI_Status* a4) { return _pympi_CALL(MPI_Request_get_status_any,a0,a1,a2,a3,a4); }
#define MPI_Request_get_status_any _pympi_MPI_Request_get_status_any

PyMPI_LOCAL int _pympi__MPI_Request_get_status_all(int a0,MPI_Request  a1[],int* a2,MPI_Status a3[]) { return MPI_Request_get_status_all(a0,a1,a2,a3); }
#undef MPI_Request_get_status_all
#ifndef PyMPI_HAVE_MPI_Request_get_status_all
extern int MPI_Request_get_status_all(int a0,MPI_Request  a1[],int* a2,MPI_Status a3[]);
#endif
_pympi_WEAK(MPI_Request_get_status_all)
PyMPI_LOCAL int _pympi_MPI_Request_get_status_all(int a0,MPI_Request  a1[],int* a2,MPI_Status a3[]) { return _pympi_CALL(MPI_Request_get_status_all,a0,a1,a2,a3); }
#define MPI_Request_get_status_all _pympi_MPI_Request_get_status_all

PyMPI_LOCAL int _pympi__MPI_Request_get_status_some(int a0,MPI_Request a1[],int* a2,int a3[],MPI_Status a4[]) { return MPI_Request_get_status_some(a0,a1,a2,a3,a4); }
#undef MPI_Request_get_status_some
#ifndef PyMPI_HAVE_MPI_Request_get_status_some
extern int MPI_Request_get_status_some(int a0,MPI_Request a1[],int* a2,int a3[],MPI_Status a4[]);
#endif
_pympi_WEAK(MPI_Request_get_status_some)
PyMPI_LOCAL int _pympi_MPI_Request_get_status_some(int a0,MPI_Request a1[],int* a2,int a3[],MPI_Status a4[]) { return _pympi_CALL(MPI_Request_get_status_some,a0,a1,a2,a3,a4); }
#define MPI_Request_get_status_some _pympi_MPI_Request_get_status_some

PyMPI_LOCAL int _pympi__MPI_Pready(int a0,MPI_Request a1) { return MPI_Pready(a0,a1); }
#undef MPI_Pready
#ifndef PyMPI_HAVE_MPI_Pready
extern int MPI_Pready(int a0,MPI_Request a1);
#endif
_pympi_WEAK(MPI_Pready)
PyMPI_LOCAL int _pympi_MPI_Pready(int a0,MPI_Request a1) { return _pympi_CALL(MPI_Pready,a0,a1); }
#define MPI_Pready _pympi_MPI_Pready

PyMPI_LOCAL int _pympi__MPI_Pready_range(int a0,int a1,MPI_Request a2) { return MPI_Pready_range(a0,a1,a2); }
#undef MPI_Pready_range
#ifndef PyMPI_HAVE_MPI_Pready_range
extern int MPI_Pready_range(int a0,int a1,MPI_Request a2);
#endif
_pympi_WEAK(MPI_Pready_range)
PyMPI_LOCAL int _pympi_MPI_Pready_range(int a0,int a1,MPI_Request a2) { return _pympi_CALL(MPI_Pready_range,a0,a1,a2); }
#define MPI_Pready_range _pympi_MPI_Pready_range

PyMPI_LOCAL int _pympi__MPI_Pready_list(int a0,int a1[],MPI_Request a2) { return MPI_Pready_list(a0,a1,a2); }
#undef MPI_Pready_list
#ifndef PyMPI_HAVE_MPI_Pready_list
extern int MPI_Pready_list(int a0,int a1[],MPI_Request a2);
#endif
_pympi_WEAK(MPI_Pready_list)
PyMPI_LOCAL int _pympi_MPI_Pready_list(int a0,int a1[],MPI_Request a2) { return _pympi_CALL(MPI_Pready_list,a0,a1,a2); }
#define MPI_Pready_list _pympi_MPI_Pready_list

PyMPI_LOCAL int _pympi__MPI_Parrived(MPI_Request a0,int a1,int* a2) { return MPI_Parrived(a0,a1,a2); }
#undef MPI_Parrived
#ifndef PyMPI_HAVE_MPI_Parrived
extern int MPI_Parrived(MPI_Request a0,int a1,int* a2);
#endif
_pympi_WEAK(MPI_Parrived)
PyMPI_LOCAL int _pympi_MPI_Parrived(MPI_Request a0,int a1,int* a2) { return _pympi_CALL(MPI_Parrived,a0,a1,a2); }
#define MPI_Parrived _pympi_MPI_Parrived

PyMPI_LOCAL int _pympi__MPI_Op_create_c(MPI_User_function_c* a0,int a1,MPI_Op* a2) { return MPI_Op_create_c(a0,a1,a2); }
#undef MPI_Op_create_c
#ifndef PyMPI_HAVE_MPI_Op_create_c
extern int MPI_Op_create_c(MPI_User_function_c* a0,int a1,MPI_Op* a2);
#endif
_pympi_WEAK(MPI_Op_create_c)
PyMPI_LOCAL int _pympi_MPI_Op_create_c(MPI_User_function_c* a0,int a1,MPI_Op* a2) { return _pympi_CALL(MPI_Op_create_c,a0,a1,a2); }
#define MPI_Op_create_c _pympi_MPI_Op_create_c

PyMPI_LOCAL int _pympi__MPI_Info_create_env(int a0,char* a1[],MPI_Info* a2) { return MPI_Info_create_env(a0,a1,a2); }
#undef MPI_Info_create_env
#ifndef PyMPI_HAVE_MPI_Info_create_env
extern int MPI_Info_create_env(int a0,char* a1[],MPI_Info* a2);
#endif
_pympi_WEAK(MPI_Info_create_env)
PyMPI_LOCAL int _pympi_MPI_Info_create_env(int a0,char* a1[],MPI_Info* a2) { return _pympi_CALL(MPI_Info_create_env,a0,a1,a2); }
#define MPI_Info_create_env _pympi_MPI_Info_create_env

PyMPI_LOCAL int _pympi__MPI_Info_get_string(MPI_Info a0,char a1[],int* a2,char a3[],int* a4) { return MPI_Info_get_string(a0,a1,a2,a3,a4); }
#undef MPI_Info_get_string
#ifndef PyMPI_HAVE_MPI_Info_get_string
extern int MPI_Info_get_string(MPI_Info a0,char a1[],int* a2,char a3[],int* a4);
#endif
_pympi_WEAK(MPI_Info_get_string)
PyMPI_LOCAL int _pympi_MPI_Info_get_string(MPI_Info a0,char a1[],int* a2,char a3[],int* a4) { return _pympi_CALL(MPI_Info_get_string,a0,a1,a2,a3,a4); }
#define MPI_Info_get_string _pympi_MPI_Info_get_string

PyMPI_LOCAL int _pympi__MPI_Session_init(MPI_Info a0,MPI_Errhandler a1,MPI_Session* a2) { return MPI_Session_init(a0,a1,a2); }
#undef MPI_Session_init
#ifndef PyMPI_HAVE_MPI_Session_init
extern int MPI_Session_init(MPI_Info a0,MPI_Errhandler a1,MPI_Session* a2);
#endif
_pympi_WEAK(MPI_Session_init)
PyMPI_LOCAL int _pympi_MPI_Session_init(MPI_Info a0,MPI_Errhandler a1,MPI_Session* a2) { return _pympi_CALL(MPI_Session_init,a0,a1,a2); }
#define MPI_Session_init _pympi_MPI_Session_init

PyMPI_LOCAL int _pympi__MPI_Session_finalize(MPI_Session* a0) { return MPI_Session_finalize(a0); }
#undef MPI_Session_finalize
#ifndef PyMPI_HAVE_MPI_Session_finalize
extern int MPI_Session_finalize(MPI_Session* a0);
#endif
_pympi_WEAK(MPI_Session_finalize)
PyMPI_LOCAL int _pympi_MPI_Session_finalize(MPI_Session* a0) { return _pympi_CALL(MPI_Session_finalize,a0); }
#define MPI_Session_finalize _pympi_MPI_Session_finalize

PyMPI_LOCAL int _pympi__MPI_Session_get_num_psets(MPI_Session a0,MPI_Info a1,int* a2) { return MPI_Session_get_num_psets(a0,a1,a2); }
#undef MPI_Session_get_num_psets
#ifndef PyMPI_HAVE_MPI_Session_get_num_psets
extern int MPI_Session_get_num_psets(MPI_Session a0,MPI_Info a1,int* a2);
#endif
_pympi_WEAK(MPI_Session_get_num_psets)
PyMPI_LOCAL int _pympi_MPI_Session_get_num_psets(MPI_Session a0,MPI_Info a1,int* a2) { return _pympi_CALL(MPI_Session_get_num_psets,a0,a1,a2); }
#define MPI_Session_get_num_psets _pympi_MPI_Session_get_num_psets

PyMPI_LOCAL int _pympi__MPI_Session_get_nth_pset(MPI_Session a0,MPI_Info a1,int a2,int* a3,char a4[]) { return MPI_Session_get_nth_pset(a0,a1,a2,a3,a4); }
#undef MPI_Session_get_nth_pset
#ifndef PyMPI_HAVE_MPI_Session_get_nth_pset
extern int MPI_Session_get_nth_pset(MPI_Session a0,MPI_Info a1,int a2,int* a3,char a4[]);
#endif
_pympi_WEAK(MPI_Session_get_nth_pset)
PyMPI_LOCAL int _pympi_MPI_Session_get_nth_pset(MPI_Session a0,MPI_Info a1,int a2,int* a3,char a4[]) { return _pympi_CALL(MPI_Session_get_nth_pset,a0,a1,a2,a3,a4); }
#define MPI_Session_get_nth_pset _pympi_MPI_Session_get_nth_pset

PyMPI_LOCAL int _pympi__MPI_Session_get_info(MPI_Session a0,MPI_Info* a1) { return MPI_Session_get_info(a0,a1); }
#undef MPI_Session_get_info
#ifndef PyMPI_HAVE_MPI_Session_get_info
extern int MPI_Session_get_info(MPI_Session a0,MPI_Info* a1);
#endif
_pympi_WEAK(MPI_Session_get_info)
PyMPI_LOCAL int _pympi_MPI_Session_get_info(MPI_Session a0,MPI_Info* a1) { return _pympi_CALL(MPI_Session_get_info,a0,a1); }
#define MPI_Session_get_info _pympi_MPI_Session_get_info

PyMPI_LOCAL int _pympi__MPI_Session_get_pset_info(MPI_Session a0,char a1[],MPI_Info* a2) { return MPI_Session_get_pset_info(a0,a1,a2); }
#undef MPI_Session_get_pset_info
#ifndef PyMPI_HAVE_MPI_Session_get_pset_info
extern int MPI_Session_get_pset_info(MPI_Session a0,char a1[],MPI_Info* a2);
#endif
_pympi_WEAK(MPI_Session_get_pset_info)
PyMPI_LOCAL int _pympi_MPI_Session_get_pset_info(MPI_Session a0,char a1[],MPI_Info* a2) { return _pympi_CALL(MPI_Session_get_pset_info,a0,a1,a2); }
#define MPI_Session_get_pset_info _pympi_MPI_Session_get_pset_info

PyMPI_LOCAL int _pympi__MPI_Group_from_session_pset(MPI_Session a0,char a1[],MPI_Group* a2) { return MPI_Group_from_session_pset(a0,a1,a2); }
#undef MPI_Group_from_session_pset
#ifndef PyMPI_HAVE_MPI_Group_from_session_pset
extern int MPI_Group_from_session_pset(MPI_Session a0,char a1[],MPI_Group* a2);
#endif
_pympi_WEAK(MPI_Group_from_session_pset)
PyMPI_LOCAL int _pympi_MPI_Group_from_session_pset(MPI_Session a0,char a1[],MPI_Group* a2) { return _pympi_CALL(MPI_Group_from_session_pset,a0,a1,a2); }
#define MPI_Group_from_session_pset _pympi_MPI_Group_from_session_pset

PyMPI_LOCAL int _pympi__MPI_Session_create_errhandler(MPI_Session_errhandler_function* a0,MPI_Errhandler* a1) { return MPI_Session_create_errhandler(a0,a1); }
#undef MPI_Session_create_errhandler
#ifndef PyMPI_HAVE_MPI_Session_create_errhandler
extern int MPI_Session_create_errhandler(MPI_Session_errhandler_function* a0,MPI_Errhandler* a1);
#endif
_pympi_WEAK(MPI_Session_create_errhandler)
PyMPI_LOCAL int _pympi_MPI_Session_create_errhandler(MPI_Session_errhandler_function* a0,MPI_Errhandler* a1) { return _pympi_CALL(MPI_Session_create_errhandler,a0,a1); }
#define MPI_Session_create_errhandler _pympi_MPI_Session_create_errhandler

PyMPI_LOCAL int _pympi__MPI_Session_get_errhandler(MPI_Session a0,MPI_Errhandler* a1) { return MPI_Session_get_errhandler(a0,a1); }
#undef MPI_Session_get_errhandler
#ifndef PyMPI_HAVE_MPI_Session_get_errhandler
extern int MPI_Session_get_errhandler(MPI_Session a0,MPI_Errhandler* a1);
#endif
_pympi_WEAK(MPI_Session_get_errhandler)
PyMPI_LOCAL int _pympi_MPI_Session_get_errhandler(MPI_Session a0,MPI_Errhandler* a1) { return _pympi_CALL(MPI_Session_get_errhandler,a0,a1); }
#define MPI_Session_get_errhandler _pympi_MPI_Session_get_errhandler

PyMPI_LOCAL int _pympi__MPI_Session_set_errhandler(MPI_Session a0,MPI_Errhandler a1) { return MPI_Session_set_errhandler(a0,a1); }
#undef MPI_Session_set_errhandler
#ifndef PyMPI_HAVE_MPI_Session_set_errhandler
extern int MPI_Session_set_errhandler(MPI_Session a0,MPI_Errhandler a1);
#endif
_pympi_WEAK(MPI_Session_set_errhandler)
PyMPI_LOCAL int _pympi_MPI_Session_set_errhandler(MPI_Session a0,MPI_Errhandler a1) { return _pympi_CALL(MPI_Session_set_errhandler,a0,a1); }
#define MPI_Session_set_errhandler _pympi_MPI_Session_set_errhandler

PyMPI_LOCAL int _pympi__MPI_Session_call_errhandler(MPI_Session a0,int a1) { return MPI_Session_call_errhandler(a0,a1); }
#undef MPI_Session_call_errhandler
#ifndef PyMPI_HAVE_MPI_Session_call_errhandler
extern int MPI_Session_call_errhandler(MPI_Session a0,int a1);
#endif
_pympi_WEAK(MPI_Session_call_errhandler)
PyMPI_LOCAL int _pympi_MPI_Session_call_errhandler(MPI_Session a0,int a1) { return _pympi_CALL(MPI_Session_call_errhandler,a0,a1); }
#define MPI_Session_call_errhandler _pympi_MPI_Session_call_errhandler

PyMPI_LOCAL int _pympi__MPI_Buffer_flush(void) { return MPI_Buffer_flush(); }
#undef MPI_Buffer_flush
#ifndef PyMPI_HAVE_MPI_Buffer_flush
extern int MPI_Buffer_flush(void);
#endif
_pympi_WEAK(MPI_Buffer_flush)
PyMPI_LOCAL int _pympi_MPI_Buffer_flush(void) { return _pympi_CALL(MPI_Buffer_flush,); }
#define MPI_Buffer_flush _pympi_MPI_Buffer_flush

PyMPI_LOCAL int _pympi__MPI_Buffer_iflush(MPI_Request* a0) { return MPI_Buffer_iflush(a0); }
#undef MPI_Buffer_iflush
#ifndef PyMPI_HAVE_MPI_Buffer_iflush
extern int MPI_Buffer_iflush(MPI_Request* a0);
#endif
_pympi_WEAK(MPI_Buffer_iflush)
PyMPI_LOCAL int _pympi_MPI_Buffer_iflush(MPI_Request* a0) { return _pympi_CALL(MPI_Buffer_iflush,a0); }
#define MPI_Buffer_iflush _pympi_MPI_Buffer_iflush

PyMPI_LOCAL int _pympi__MPI_Comm_attach_buffer(MPI_Comm a0,void* a1,int a2) { return MPI_Comm_attach_buffer(a0,a1,a2); }
#undef MPI_Comm_attach_buffer
#ifndef PyMPI_HAVE_MPI_Comm_attach_buffer
extern int MPI_Comm_attach_buffer(MPI_Comm a0,void* a1,int a2);
#endif
_pympi_WEAK(MPI_Comm_attach_buffer)
PyMPI_LOCAL int _pympi_MPI_Comm_attach_buffer(MPI_Comm a0,void* a1,int a2) { return _pympi_CALL(MPI_Comm_attach_buffer,a0,a1,a2); }
#define MPI_Comm_attach_buffer _pympi_MPI_Comm_attach_buffer

PyMPI_LOCAL int _pympi__MPI_Comm_detach_buffer(MPI_Comm a0,void* a1,int* a2) { return MPI_Comm_detach_buffer(a0,a1,a2); }
#undef MPI_Comm_detach_buffer
#ifndef PyMPI_HAVE_MPI_Comm_detach_buffer
extern int MPI_Comm_detach_buffer(MPI_Comm a0,void* a1,int* a2);
#endif
_pympi_WEAK(MPI_Comm_detach_buffer)
PyMPI_LOCAL int _pympi_MPI_Comm_detach_buffer(MPI_Comm a0,void* a1,int* a2) { return _pympi_CALL(MPI_Comm_detach_buffer,a0,a1,a2); }
#define MPI_Comm_detach_buffer _pympi_MPI_Comm_detach_buffer

PyMPI_LOCAL int _pympi__MPI_Comm_flush_buffer(MPI_Comm a0) { return MPI_Comm_flush_buffer(a0); }
#undef MPI_Comm_flush_buffer
#ifndef PyMPI_HAVE_MPI_Comm_flush_buffer
extern int MPI_Comm_flush_buffer(MPI_Comm a0);
#endif
_pympi_WEAK(MPI_Comm_flush_buffer)
PyMPI_LOCAL int _pympi_MPI_Comm_flush_buffer(MPI_Comm a0) { return _pympi_CALL(MPI_Comm_flush_buffer,a0); }
#define MPI_Comm_flush_buffer _pympi_MPI_Comm_flush_buffer

PyMPI_LOCAL int _pympi__MPI_Comm_iflush_buffer(MPI_Comm a0,MPI_Request* a1) { return MPI_Comm_iflush_buffer(a0,a1); }
#undef MPI_Comm_iflush_buffer
#ifndef PyMPI_HAVE_MPI_Comm_iflush_buffer
extern int MPI_Comm_iflush_buffer(MPI_Comm a0,MPI_Request* a1);
#endif
_pympi_WEAK(MPI_Comm_iflush_buffer)
PyMPI_LOCAL int _pympi_MPI_Comm_iflush_buffer(MPI_Comm a0,MPI_Request* a1) { return _pympi_CALL(MPI_Comm_iflush_buffer,a0,a1); }
#define MPI_Comm_iflush_buffer _pympi_MPI_Comm_iflush_buffer

PyMPI_LOCAL int _pympi__MPI_Session_attach_buffer(MPI_Session a0,void* a1,int a2) { return MPI_Session_attach_buffer(a0,a1,a2); }
#undef MPI_Session_attach_buffer
#ifndef PyMPI_HAVE_MPI_Session_attach_buffer
extern int MPI_Session_attach_buffer(MPI_Session a0,void* a1,int a2);
#endif
_pympi_WEAK(MPI_Session_attach_buffer)
PyMPI_LOCAL int _pympi_MPI_Session_attach_buffer(MPI_Session a0,void* a1,int a2) { return _pympi_CALL(MPI_Session_attach_buffer,a0,a1,a2); }
#define MPI_Session_attach_buffer _pympi_MPI_Session_attach_buffer

PyMPI_LOCAL int _pympi__MPI_Session_detach_buffer(MPI_Session a0,void* a1,int* a2) { return MPI_Session_detach_buffer(a0,a1,a2); }
#undef MPI_Session_detach_buffer
#ifndef PyMPI_HAVE_MPI_Session_detach_buffer
extern int MPI_Session_detach_buffer(MPI_Session a0,void* a1,int* a2);
#endif
_pympi_WEAK(MPI_Session_detach_buffer)
PyMPI_LOCAL int _pympi_MPI_Session_detach_buffer(MPI_Session a0,void* a1,int* a2) { return _pympi_CALL(MPI_Session_detach_buffer,a0,a1,a2); }
#define MPI_Session_detach_buffer _pympi_MPI_Session_detach_buffer

PyMPI_LOCAL int _pympi__MPI_Session_flush_buffer(MPI_Session a0) { return MPI_Session_flush_buffer(a0); }
#undef MPI_Session_flush_buffer
#ifndef PyMPI_HAVE_MPI_Session_flush_buffer
extern int MPI_Session_flush_buffer(MPI_Session a0);
#endif
_pympi_WEAK(MPI_Session_flush_buffer)
PyMPI_LOCAL int _pympi_MPI_Session_flush_buffer(MPI_Session a0) { return _pympi_CALL(MPI_Session_flush_buffer,a0); }
#define MPI_Session_flush_buffer _pympi_MPI_Session_flush_buffer

PyMPI_LOCAL int _pympi__MPI_Session_iflush_buffer(MPI_Session a0,MPI_Request* a1) { return MPI_Session_iflush_buffer(a0,a1); }
#undef MPI_Session_iflush_buffer
#ifndef PyMPI_HAVE_MPI_Session_iflush_buffer
extern int MPI_Session_iflush_buffer(MPI_Session a0,MPI_Request* a1);
#endif
_pympi_WEAK(MPI_Session_iflush_buffer)
PyMPI_LOCAL int _pympi_MPI_Session_iflush_buffer(MPI_Session a0,MPI_Request* a1) { return _pympi_CALL(MPI_Session_iflush_buffer,a0,a1); }
#define MPI_Session_iflush_buffer _pympi_MPI_Session_iflush_buffer

PyMPI_LOCAL int _pympi__MPI_Isendrecv(void* a0,int a1,MPI_Datatype a2,int a3,int a4,void* a5,int a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11) { return MPI_Isendrecv(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#undef MPI_Isendrecv
#ifndef PyMPI_HAVE_MPI_Isendrecv
extern int MPI_Isendrecv(void* a0,int a1,MPI_Datatype a2,int a3,int a4,void* a5,int a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11);
#endif
_pympi_WEAK(MPI_Isendrecv)
PyMPI_LOCAL int _pympi_MPI_Isendrecv(void* a0,int a1,MPI_Datatype a2,int a3,int a4,void* a5,int a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11) { return _pympi_CALL(MPI_Isendrecv,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#define MPI_Isendrecv _pympi_MPI_Isendrecv

PyMPI_LOCAL int _pympi__MPI_Isendrecv_replace(void* a0,int a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8) { return MPI_Isendrecv_replace(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Isendrecv_replace
#ifndef PyMPI_HAVE_MPI_Isendrecv_replace
extern int MPI_Isendrecv_replace(void* a0,int a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Isendrecv_replace)
PyMPI_LOCAL int _pympi_MPI_Isendrecv_replace(void* a0,int a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8) { return _pympi_CALL(MPI_Isendrecv_replace,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Isendrecv_replace _pympi_MPI_Isendrecv_replace

PyMPI_LOCAL int _pympi__MPI_Psend_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Psend_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Psend_init
#ifndef PyMPI_HAVE_MPI_Psend_init
extern int MPI_Psend_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Psend_init)
PyMPI_LOCAL int _pympi_MPI_Psend_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Psend_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Psend_init _pympi_MPI_Psend_init

PyMPI_LOCAL int _pympi__MPI_Precv_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Precv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Precv_init
#ifndef PyMPI_HAVE_MPI_Precv_init
extern int MPI_Precv_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Precv_init)
PyMPI_LOCAL int _pympi_MPI_Precv_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Precv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Precv_init _pympi_MPI_Precv_init

PyMPI_LOCAL int _pympi__MPI_Barrier_init(MPI_Comm a0,MPI_Info a1,MPI_Request* a2) { return MPI_Barrier_init(a0,a1,a2); }
#undef MPI_Barrier_init
#ifndef PyMPI_HAVE_MPI_Barrier_init
extern int MPI_Barrier_init(MPI_Comm a0,MPI_Info a1,MPI_Request* a2);
#endif
_pympi_WEAK(MPI_Barrier_init)
PyMPI_LOCAL int _pympi_MPI_Barrier_init(MPI_Comm a0,MPI_Info a1,MPI_Request* a2) { return _pympi_CALL(MPI_Barrier_init,a0,a1,a2); }
#define MPI_Barrier_init _pympi_MPI_Barrier_init

PyMPI_LOCAL int _pympi__MPI_Bcast_init(void* a0,int a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6) { return MPI_Bcast_init(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Bcast_init
#ifndef PyMPI_HAVE_MPI_Bcast_init
extern int MPI_Bcast_init(void* a0,int a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Bcast_init)
PyMPI_LOCAL int _pympi_MPI_Bcast_init(void* a0,int a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6) { return _pympi_CALL(MPI_Bcast_init,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Bcast_init _pympi_MPI_Bcast_init

PyMPI_LOCAL int _pympi__MPI_Gather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Gather_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Gather_init
#ifndef PyMPI_HAVE_MPI_Gather_init
extern int MPI_Gather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Gather_init)
PyMPI_LOCAL int _pympi_MPI_Gather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Gather_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Gather_init _pympi_MPI_Gather_init

PyMPI_LOCAL int _pympi__MPI_Gatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Gatherv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Gatherv_init
#ifndef PyMPI_HAVE_MPI_Gatherv_init
extern int MPI_Gatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Gatherv_init)
PyMPI_LOCAL int _pympi_MPI_Gatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Gatherv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Gatherv_init _pympi_MPI_Gatherv_init

PyMPI_LOCAL int _pympi__MPI_Scatter_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Scatter_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Scatter_init
#ifndef PyMPI_HAVE_MPI_Scatter_init
extern int MPI_Scatter_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Scatter_init)
PyMPI_LOCAL int _pympi_MPI_Scatter_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Scatter_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Scatter_init _pympi_MPI_Scatter_init

PyMPI_LOCAL int _pympi__MPI_Scatterv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Scatterv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Scatterv_init
#ifndef PyMPI_HAVE_MPI_Scatterv_init
extern int MPI_Scatterv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Scatterv_init)
PyMPI_LOCAL int _pympi_MPI_Scatterv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Scatterv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Scatterv_init _pympi_MPI_Scatterv_init

PyMPI_LOCAL int _pympi__MPI_Allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Allgather_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Allgather_init
#ifndef PyMPI_HAVE_MPI_Allgather_init
extern int MPI_Allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Allgather_init)
PyMPI_LOCAL int _pympi_MPI_Allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Allgather_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Allgather_init _pympi_MPI_Allgather_init

PyMPI_LOCAL int _pympi__MPI_Allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Allgatherv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Allgatherv_init
#ifndef PyMPI_HAVE_MPI_Allgatherv_init
extern int MPI_Allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Allgatherv_init)
PyMPI_LOCAL int _pympi_MPI_Allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Allgatherv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Allgatherv_init _pympi_MPI_Allgatherv_init

PyMPI_LOCAL int _pympi__MPI_Alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Alltoall_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Alltoall_init
#ifndef PyMPI_HAVE_MPI_Alltoall_init
extern int MPI_Alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Alltoall_init)
PyMPI_LOCAL int _pympi_MPI_Alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Alltoall_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Alltoall_init _pympi_MPI_Alltoall_init

PyMPI_LOCAL int _pympi__MPI_Alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Alltoallv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Alltoallv_init
#ifndef PyMPI_HAVE_MPI_Alltoallv_init
extern int MPI_Alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Alltoallv_init)
PyMPI_LOCAL int _pympi_MPI_Alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Alltoallv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Alltoallv_init _pympi_MPI_Alltoallv_init

PyMPI_LOCAL int _pympi__MPI_Alltoallw_init(void* a0,int a1[],int a2[],MPI_Datatype a3[],void* a4,int a5[],int a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Alltoallw_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Alltoallw_init
#ifndef PyMPI_HAVE_MPI_Alltoallw_init
extern int MPI_Alltoallw_init(void* a0,int a1[],int a2[],MPI_Datatype a3[],void* a4,int a5[],int a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Alltoallw_init)
PyMPI_LOCAL int _pympi_MPI_Alltoallw_init(void* a0,int a1[],int a2[],MPI_Datatype a3[],void* a4,int a5[],int a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Alltoallw_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Alltoallw_init _pympi_MPI_Alltoallw_init

PyMPI_LOCAL int _pympi__MPI_Reduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Reduce_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Reduce_init
#ifndef PyMPI_HAVE_MPI_Reduce_init
extern int MPI_Reduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Reduce_init)
PyMPI_LOCAL int _pympi_MPI_Reduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Reduce_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Reduce_init _pympi_MPI_Reduce_init

PyMPI_LOCAL int _pympi__MPI_Allreduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Allreduce_init(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Allreduce_init
#ifndef PyMPI_HAVE_MPI_Allreduce_init
extern int MPI_Allreduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Allreduce_init)
PyMPI_LOCAL int _pympi_MPI_Allreduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Allreduce_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Allreduce_init _pympi_MPI_Allreduce_init

PyMPI_LOCAL int _pympi__MPI_Reduce_scatter_block_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Reduce_scatter_block_init(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Reduce_scatter_block_init
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_block_init
extern int MPI_Reduce_scatter_block_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Reduce_scatter_block_init)
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_block_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Reduce_scatter_block_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Reduce_scatter_block_init _pympi_MPI_Reduce_scatter_block_init

PyMPI_LOCAL int _pympi__MPI_Reduce_scatter_init(void* a0,void* a1,int a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Reduce_scatter_init(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Reduce_scatter_init
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_init
extern int MPI_Reduce_scatter_init(void* a0,void* a1,int a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Reduce_scatter_init)
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_init(void* a0,void* a1,int a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Reduce_scatter_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Reduce_scatter_init _pympi_MPI_Reduce_scatter_init

PyMPI_LOCAL int _pympi__MPI_Scan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Scan_init(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Scan_init
#ifndef PyMPI_HAVE_MPI_Scan_init
extern int MPI_Scan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Scan_init)
PyMPI_LOCAL int _pympi_MPI_Scan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Scan_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Scan_init _pympi_MPI_Scan_init

PyMPI_LOCAL int _pympi__MPI_Exscan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Exscan_init(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Exscan_init
#ifndef PyMPI_HAVE_MPI_Exscan_init
extern int MPI_Exscan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Exscan_init)
PyMPI_LOCAL int _pympi_MPI_Exscan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Exscan_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Exscan_init _pympi_MPI_Exscan_init

PyMPI_LOCAL int _pympi__MPI_Neighbor_allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Neighbor_allgather_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Neighbor_allgather_init
#ifndef PyMPI_HAVE_MPI_Neighbor_allgather_init
extern int MPI_Neighbor_allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Neighbor_allgather_init)
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Neighbor_allgather_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_allgather_init _pympi_MPI_Neighbor_allgather_init

PyMPI_LOCAL int _pympi__MPI_Neighbor_allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Neighbor_allgatherv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Neighbor_allgatherv_init
#ifndef PyMPI_HAVE_MPI_Neighbor_allgatherv_init
extern int MPI_Neighbor_allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Neighbor_allgatherv_init)
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Neighbor_allgatherv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Neighbor_allgatherv_init _pympi_MPI_Neighbor_allgatherv_init

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Neighbor_alltoall_init(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Neighbor_alltoall_init
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoall_init
extern int MPI_Neighbor_alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Neighbor_alltoall_init)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Neighbor_alltoall_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_alltoall_init _pympi_MPI_Neighbor_alltoall_init

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Neighbor_alltoallv_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Neighbor_alltoallv_init
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallv_init
extern int MPI_Neighbor_alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Neighbor_alltoallv_init)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Neighbor_alltoallv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Neighbor_alltoallv_init _pympi_MPI_Neighbor_alltoallv_init

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoallw_init(void* a0,int a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,int a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Neighbor_alltoallw_init(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Neighbor_alltoallw_init
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallw_init
extern int MPI_Neighbor_alltoallw_init(void* a0,int a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,int a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Neighbor_alltoallw_init)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallw_init(void* a0,int a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,int a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Neighbor_alltoallw_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Neighbor_alltoallw_init _pympi_MPI_Neighbor_alltoallw_init

PyMPI_LOCAL int _pympi__MPI_Comm_idup_with_info(MPI_Comm a0,MPI_Info a1,MPI_Comm* a2,MPI_Request* a3) { return MPI_Comm_idup_with_info(a0,a1,a2,a3); }
#undef MPI_Comm_idup_with_info
#ifndef PyMPI_HAVE_MPI_Comm_idup_with_info
extern int MPI_Comm_idup_with_info(MPI_Comm a0,MPI_Info a1,MPI_Comm* a2,MPI_Request* a3);
#endif
_pympi_WEAK(MPI_Comm_idup_with_info)
PyMPI_LOCAL int _pympi_MPI_Comm_idup_with_info(MPI_Comm a0,MPI_Info a1,MPI_Comm* a2,MPI_Request* a3) { return _pympi_CALL(MPI_Comm_idup_with_info,a0,a1,a2,a3); }
#define MPI_Comm_idup_with_info _pympi_MPI_Comm_idup_with_info

PyMPI_LOCAL int _pympi__MPI_Comm_create_from_group(MPI_Group a0,char a1[],MPI_Info a2,MPI_Errhandler a3,MPI_Comm* a4) { return MPI_Comm_create_from_group(a0,a1,a2,a3,a4); }
#undef MPI_Comm_create_from_group
#ifndef PyMPI_HAVE_MPI_Comm_create_from_group
extern int MPI_Comm_create_from_group(MPI_Group a0,char a1[],MPI_Info a2,MPI_Errhandler a3,MPI_Comm* a4);
#endif
_pympi_WEAK(MPI_Comm_create_from_group)
PyMPI_LOCAL int _pympi_MPI_Comm_create_from_group(MPI_Group a0,char a1[],MPI_Info a2,MPI_Errhandler a3,MPI_Comm* a4) { return _pympi_CALL(MPI_Comm_create_from_group,a0,a1,a2,a3,a4); }
#define MPI_Comm_create_from_group _pympi_MPI_Comm_create_from_group

PyMPI_LOCAL int _pympi__MPI_Intercomm_create_from_groups(MPI_Group a0,int a1,MPI_Group a2,int a3,char a4[],MPI_Info a5,MPI_Errhandler a6,MPI_Comm* a7) { return MPI_Intercomm_create_from_groups(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Intercomm_create_from_groups
#ifndef PyMPI_HAVE_MPI_Intercomm_create_from_groups
extern int MPI_Intercomm_create_from_groups(MPI_Group a0,int a1,MPI_Group a2,int a3,char a4[],MPI_Info a5,MPI_Errhandler a6,MPI_Comm* a7);
#endif
_pympi_WEAK(MPI_Intercomm_create_from_groups)
PyMPI_LOCAL int _pympi_MPI_Intercomm_create_from_groups(MPI_Group a0,int a1,MPI_Group a2,int a3,char a4[],MPI_Info a5,MPI_Errhandler a6,MPI_Comm* a7) { return _pympi_CALL(MPI_Intercomm_create_from_groups,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Intercomm_create_from_groups _pympi_MPI_Intercomm_create_from_groups

PyMPI_LOCAL int _pympi__MPI_Buffer_attach_c(void* a0,MPI_Count a1) { return MPI_Buffer_attach_c(a0,a1); }
#undef MPI_Buffer_attach_c
#ifndef PyMPI_HAVE_MPI_Buffer_attach_c
extern int MPI_Buffer_attach_c(void* a0,MPI_Count a1);
#endif
_pympi_WEAK(MPI_Buffer_attach_c)
PyMPI_LOCAL int _pympi_MPI_Buffer_attach_c(void* a0,MPI_Count a1) { return _pympi_CALL(MPI_Buffer_attach_c,a0,a1); }
#define MPI_Buffer_attach_c _pympi_MPI_Buffer_attach_c

PyMPI_LOCAL int _pympi__MPI_Buffer_detach_c(void* a0,MPI_Count* a1) { return MPI_Buffer_detach_c(a0,a1); }
#undef MPI_Buffer_detach_c
#ifndef PyMPI_HAVE_MPI_Buffer_detach_c
extern int MPI_Buffer_detach_c(void* a0,MPI_Count* a1);
#endif
_pympi_WEAK(MPI_Buffer_detach_c)
PyMPI_LOCAL int _pympi_MPI_Buffer_detach_c(void* a0,MPI_Count* a1) { return _pympi_CALL(MPI_Buffer_detach_c,a0,a1); }
#define MPI_Buffer_detach_c _pympi_MPI_Buffer_detach_c

PyMPI_LOCAL int _pympi__MPI_Comm_attach_buffer_c(MPI_Comm a0,void* a1,MPI_Count a2) { return MPI_Comm_attach_buffer_c(a0,a1,a2); }
#undef MPI_Comm_attach_buffer_c
#ifndef PyMPI_HAVE_MPI_Comm_attach_buffer_c
extern int MPI_Comm_attach_buffer_c(MPI_Comm a0,void* a1,MPI_Count a2);
#endif
_pympi_WEAK(MPI_Comm_attach_buffer_c)
PyMPI_LOCAL int _pympi_MPI_Comm_attach_buffer_c(MPI_Comm a0,void* a1,MPI_Count a2) { return _pympi_CALL(MPI_Comm_attach_buffer_c,a0,a1,a2); }
#define MPI_Comm_attach_buffer_c _pympi_MPI_Comm_attach_buffer_c

PyMPI_LOCAL int _pympi__MPI_Comm_detach_buffer_c(MPI_Comm a0,void* a1,MPI_Count* a2) { return MPI_Comm_detach_buffer_c(a0,a1,a2); }
#undef MPI_Comm_detach_buffer_c
#ifndef PyMPI_HAVE_MPI_Comm_detach_buffer_c
extern int MPI_Comm_detach_buffer_c(MPI_Comm a0,void* a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_Comm_detach_buffer_c)
PyMPI_LOCAL int _pympi_MPI_Comm_detach_buffer_c(MPI_Comm a0,void* a1,MPI_Count* a2) { return _pympi_CALL(MPI_Comm_detach_buffer_c,a0,a1,a2); }
#define MPI_Comm_detach_buffer_c _pympi_MPI_Comm_detach_buffer_c

PyMPI_LOCAL int _pympi__MPI_Session_attach_buffer_c(MPI_Session a0,void* a1,MPI_Count a2) { return MPI_Session_attach_buffer_c(a0,a1,a2); }
#undef MPI_Session_attach_buffer_c
#ifndef PyMPI_HAVE_MPI_Session_attach_buffer_c
extern int MPI_Session_attach_buffer_c(MPI_Session a0,void* a1,MPI_Count a2);
#endif
_pympi_WEAK(MPI_Session_attach_buffer_c)
PyMPI_LOCAL int _pympi_MPI_Session_attach_buffer_c(MPI_Session a0,void* a1,MPI_Count a2) { return _pympi_CALL(MPI_Session_attach_buffer_c,a0,a1,a2); }
#define MPI_Session_attach_buffer_c _pympi_MPI_Session_attach_buffer_c

PyMPI_LOCAL int _pympi__MPI_Session_detach_buffer_c(MPI_Session a0,void* a1,MPI_Count* a2) { return MPI_Session_detach_buffer_c(a0,a1,a2); }
#undef MPI_Session_detach_buffer_c
#ifndef PyMPI_HAVE_MPI_Session_detach_buffer_c
extern int MPI_Session_detach_buffer_c(MPI_Session a0,void* a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_Session_detach_buffer_c)
PyMPI_LOCAL int _pympi_MPI_Session_detach_buffer_c(MPI_Session a0,void* a1,MPI_Count* a2) { return _pympi_CALL(MPI_Session_detach_buffer_c,a0,a1,a2); }
#define MPI_Session_detach_buffer_c _pympi_MPI_Session_detach_buffer_c

PyMPI_LOCAL int _pympi__MPI_Send_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return MPI_Send_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Send_c
#ifndef PyMPI_HAVE_MPI_Send_c
extern int MPI_Send_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Send_c)
PyMPI_LOCAL int _pympi_MPI_Send_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return _pympi_CALL(MPI_Send_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Send_c _pympi_MPI_Send_c

PyMPI_LOCAL int _pympi__MPI_Recv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Status* a6) { return MPI_Recv_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Recv_c
#ifndef PyMPI_HAVE_MPI_Recv_c
extern int MPI_Recv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Status* a6);
#endif
_pympi_WEAK(MPI_Recv_c)
PyMPI_LOCAL int _pympi_MPI_Recv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Status* a6) { return _pympi_CALL(MPI_Recv_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Recv_c _pympi_MPI_Recv_c

PyMPI_LOCAL int _pympi__MPI_Sendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Status* a11) { return MPI_Sendrecv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#undef MPI_Sendrecv_c
#ifndef PyMPI_HAVE_MPI_Sendrecv_c
extern int MPI_Sendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Status* a11);
#endif
_pympi_WEAK(MPI_Sendrecv_c)
PyMPI_LOCAL int _pympi_MPI_Sendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Status* a11) { return _pympi_CALL(MPI_Sendrecv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#define MPI_Sendrecv_c _pympi_MPI_Sendrecv_c

PyMPI_LOCAL int _pympi__MPI_Sendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Status* a8) { return MPI_Sendrecv_replace_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Sendrecv_replace_c
#ifndef PyMPI_HAVE_MPI_Sendrecv_replace_c
extern int MPI_Sendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Status* a8);
#endif
_pympi_WEAK(MPI_Sendrecv_replace_c)
PyMPI_LOCAL int _pympi_MPI_Sendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Status* a8) { return _pympi_CALL(MPI_Sendrecv_replace_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Sendrecv_replace_c _pympi_MPI_Sendrecv_replace_c

PyMPI_LOCAL int _pympi__MPI_Bsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return MPI_Bsend_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Bsend_c
#ifndef PyMPI_HAVE_MPI_Bsend_c
extern int MPI_Bsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Bsend_c)
PyMPI_LOCAL int _pympi_MPI_Bsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return _pympi_CALL(MPI_Bsend_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Bsend_c _pympi_MPI_Bsend_c

PyMPI_LOCAL int _pympi__MPI_Ssend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return MPI_Ssend_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Ssend_c
#ifndef PyMPI_HAVE_MPI_Ssend_c
extern int MPI_Ssend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Ssend_c)
PyMPI_LOCAL int _pympi_MPI_Ssend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return _pympi_CALL(MPI_Ssend_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Ssend_c _pympi_MPI_Ssend_c

PyMPI_LOCAL int _pympi__MPI_Rsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return MPI_Rsend_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Rsend_c
#ifndef PyMPI_HAVE_MPI_Rsend_c
extern int MPI_Rsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Rsend_c)
PyMPI_LOCAL int _pympi_MPI_Rsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5) { return _pympi_CALL(MPI_Rsend_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Rsend_c _pympi_MPI_Rsend_c

PyMPI_LOCAL int _pympi__MPI_Isend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Isend_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Isend_c
#ifndef PyMPI_HAVE_MPI_Isend_c
extern int MPI_Isend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Isend_c)
PyMPI_LOCAL int _pympi_MPI_Isend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Isend_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Isend_c _pympi_MPI_Isend_c

PyMPI_LOCAL int _pympi__MPI_Irecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Irecv_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Irecv_c
#ifndef PyMPI_HAVE_MPI_Irecv_c
extern int MPI_Irecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Irecv_c)
PyMPI_LOCAL int _pympi_MPI_Irecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Irecv_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Irecv_c _pympi_MPI_Irecv_c

PyMPI_LOCAL int _pympi__MPI_Isendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11) { return MPI_Isendrecv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#undef MPI_Isendrecv_c
#ifndef PyMPI_HAVE_MPI_Isendrecv_c
extern int MPI_Isendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11);
#endif
_pympi_WEAK(MPI_Isendrecv_c)
PyMPI_LOCAL int _pympi_MPI_Isendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11) { return _pympi_CALL(MPI_Isendrecv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#define MPI_Isendrecv_c _pympi_MPI_Isendrecv_c

PyMPI_LOCAL int _pympi__MPI_Isendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8) { return MPI_Isendrecv_replace_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Isendrecv_replace_c
#ifndef PyMPI_HAVE_MPI_Isendrecv_replace_c
extern int MPI_Isendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Isendrecv_replace_c)
PyMPI_LOCAL int _pympi_MPI_Isendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8) { return _pympi_CALL(MPI_Isendrecv_replace_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Isendrecv_replace_c _pympi_MPI_Isendrecv_replace_c

PyMPI_LOCAL int _pympi__MPI_Ibsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Ibsend_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Ibsend_c
#ifndef PyMPI_HAVE_MPI_Ibsend_c
extern int MPI_Ibsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Ibsend_c)
PyMPI_LOCAL int _pympi_MPI_Ibsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Ibsend_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Ibsend_c _pympi_MPI_Ibsend_c

PyMPI_LOCAL int _pympi__MPI_Issend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Issend_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Issend_c
#ifndef PyMPI_HAVE_MPI_Issend_c
extern int MPI_Issend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Issend_c)
PyMPI_LOCAL int _pympi_MPI_Issend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Issend_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Issend_c _pympi_MPI_Issend_c

PyMPI_LOCAL int _pympi__MPI_Irsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Irsend_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Irsend_c
#ifndef PyMPI_HAVE_MPI_Irsend_c
extern int MPI_Irsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Irsend_c)
PyMPI_LOCAL int _pympi_MPI_Irsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Irsend_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Irsend_c _pympi_MPI_Irsend_c

PyMPI_LOCAL int _pympi__MPI_Send_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Send_init_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Send_init_c
#ifndef PyMPI_HAVE_MPI_Send_init_c
extern int MPI_Send_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Send_init_c)
PyMPI_LOCAL int _pympi_MPI_Send_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Send_init_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Send_init_c _pympi_MPI_Send_init_c

PyMPI_LOCAL int _pympi__MPI_Recv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Recv_init_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Recv_init_c
#ifndef PyMPI_HAVE_MPI_Recv_init_c
extern int MPI_Recv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Recv_init_c)
PyMPI_LOCAL int _pympi_MPI_Recv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Recv_init_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Recv_init_c _pympi_MPI_Recv_init_c

PyMPI_LOCAL int _pympi__MPI_Bsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Bsend_init_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Bsend_init_c
#ifndef PyMPI_HAVE_MPI_Bsend_init_c
extern int MPI_Bsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Bsend_init_c)
PyMPI_LOCAL int _pympi_MPI_Bsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Bsend_init_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Bsend_init_c _pympi_MPI_Bsend_init_c

PyMPI_LOCAL int _pympi__MPI_Ssend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Ssend_init_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Ssend_init_c
#ifndef PyMPI_HAVE_MPI_Ssend_init_c
extern int MPI_Ssend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Ssend_init_c)
PyMPI_LOCAL int _pympi_MPI_Ssend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Ssend_init_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Ssend_init_c _pympi_MPI_Ssend_init_c

PyMPI_LOCAL int _pympi__MPI_Rsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Rsend_init_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Rsend_init_c
#ifndef PyMPI_HAVE_MPI_Rsend_init_c
extern int MPI_Rsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Rsend_init_c)
PyMPI_LOCAL int _pympi_MPI_Rsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Rsend_init_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Rsend_init_c _pympi_MPI_Rsend_init_c

PyMPI_LOCAL int _pympi__MPI_Mrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Status* a4) { return MPI_Mrecv_c(a0,a1,a2,a3,a4); }
#undef MPI_Mrecv_c
#ifndef PyMPI_HAVE_MPI_Mrecv_c
extern int MPI_Mrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_Mrecv_c)
PyMPI_LOCAL int _pympi_MPI_Mrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Status* a4) { return _pympi_CALL(MPI_Mrecv_c,a0,a1,a2,a3,a4); }
#define MPI_Mrecv_c _pympi_MPI_Mrecv_c

PyMPI_LOCAL int _pympi__MPI_Imrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Request* a4) { return MPI_Imrecv_c(a0,a1,a2,a3,a4); }
#undef MPI_Imrecv_c
#ifndef PyMPI_HAVE_MPI_Imrecv_c
extern int MPI_Imrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_Imrecv_c)
PyMPI_LOCAL int _pympi_MPI_Imrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Request* a4) { return _pympi_CALL(MPI_Imrecv_c,a0,a1,a2,a3,a4); }
#define MPI_Imrecv_c _pympi_MPI_Imrecv_c

PyMPI_LOCAL int _pympi__MPI_Bcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4) { return MPI_Bcast_c(a0,a1,a2,a3,a4); }
#undef MPI_Bcast_c
#ifndef PyMPI_HAVE_MPI_Bcast_c
extern int MPI_Bcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4);
#endif
_pympi_WEAK(MPI_Bcast_c)
PyMPI_LOCAL int _pympi_MPI_Bcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4) { return _pympi_CALL(MPI_Bcast_c,a0,a1,a2,a3,a4); }
#define MPI_Bcast_c _pympi_MPI_Bcast_c

PyMPI_LOCAL int _pympi__MPI_Gather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7) { return MPI_Gather_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Gather_c
#ifndef PyMPI_HAVE_MPI_Gather_c
extern int MPI_Gather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7);
#endif
_pympi_WEAK(MPI_Gather_c)
PyMPI_LOCAL int _pympi_MPI_Gather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7) { return _pympi_CALL(MPI_Gather_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Gather_c _pympi_MPI_Gather_c

PyMPI_LOCAL int _pympi__MPI_Gatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8) { return MPI_Gatherv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Gatherv_c
#ifndef PyMPI_HAVE_MPI_Gatherv_c
extern int MPI_Gatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8);
#endif
_pympi_WEAK(MPI_Gatherv_c)
PyMPI_LOCAL int _pympi_MPI_Gatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8) { return _pympi_CALL(MPI_Gatherv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Gatherv_c _pympi_MPI_Gatherv_c

PyMPI_LOCAL int _pympi__MPI_Scatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7) { return MPI_Scatter_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Scatter_c
#ifndef PyMPI_HAVE_MPI_Scatter_c
extern int MPI_Scatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7);
#endif
_pympi_WEAK(MPI_Scatter_c)
PyMPI_LOCAL int _pympi_MPI_Scatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7) { return _pympi_CALL(MPI_Scatter_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Scatter_c _pympi_MPI_Scatter_c

PyMPI_LOCAL int _pympi__MPI_Scatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8) { return MPI_Scatterv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Scatterv_c
#ifndef PyMPI_HAVE_MPI_Scatterv_c
extern int MPI_Scatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8);
#endif
_pympi_WEAK(MPI_Scatterv_c)
PyMPI_LOCAL int _pympi_MPI_Scatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8) { return _pympi_CALL(MPI_Scatterv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Scatterv_c _pympi_MPI_Scatterv_c

PyMPI_LOCAL int _pympi__MPI_Allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return MPI_Allgather_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Allgather_c
#ifndef PyMPI_HAVE_MPI_Allgather_c
extern int MPI_Allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Allgather_c)
PyMPI_LOCAL int _pympi_MPI_Allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return _pympi_CALL(MPI_Allgather_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Allgather_c _pympi_MPI_Allgather_c

PyMPI_LOCAL int _pympi__MPI_Allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7) { return MPI_Allgatherv_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Allgatherv_c
#ifndef PyMPI_HAVE_MPI_Allgatherv_c
extern int MPI_Allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7);
#endif
_pympi_WEAK(MPI_Allgatherv_c)
PyMPI_LOCAL int _pympi_MPI_Allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7) { return _pympi_CALL(MPI_Allgatherv_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Allgatherv_c _pympi_MPI_Allgatherv_c

PyMPI_LOCAL int _pympi__MPI_Alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return MPI_Alltoall_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Alltoall_c
#ifndef PyMPI_HAVE_MPI_Alltoall_c
extern int MPI_Alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Alltoall_c)
PyMPI_LOCAL int _pympi_MPI_Alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return _pympi_CALL(MPI_Alltoall_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Alltoall_c _pympi_MPI_Alltoall_c

PyMPI_LOCAL int _pympi__MPI_Alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8) { return MPI_Alltoallv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Alltoallv_c
#ifndef PyMPI_HAVE_MPI_Alltoallv_c
extern int MPI_Alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8);
#endif
_pympi_WEAK(MPI_Alltoallv_c)
PyMPI_LOCAL int _pympi_MPI_Alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8) { return _pympi_CALL(MPI_Alltoallv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Alltoallv_c _pympi_MPI_Alltoallv_c

PyMPI_LOCAL int _pympi__MPI_Alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8) { return MPI_Alltoallw_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Alltoallw_c
#ifndef PyMPI_HAVE_MPI_Alltoallw_c
extern int MPI_Alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8);
#endif
_pympi_WEAK(MPI_Alltoallw_c)
PyMPI_LOCAL int _pympi_MPI_Alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8) { return _pympi_CALL(MPI_Alltoallw_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Alltoallw_c _pympi_MPI_Alltoallw_c

PyMPI_LOCAL int _pympi__MPI_Reduce_local_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4) { return MPI_Reduce_local_c(a0,a1,a2,a3,a4); }
#undef MPI_Reduce_local_c
#ifndef PyMPI_HAVE_MPI_Reduce_local_c
extern int MPI_Reduce_local_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4);
#endif
_pympi_WEAK(MPI_Reduce_local_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_local_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4) { return _pympi_CALL(MPI_Reduce_local_c,a0,a1,a2,a3,a4); }
#define MPI_Reduce_local_c _pympi_MPI_Reduce_local_c

PyMPI_LOCAL int _pympi__MPI_Reduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6) { return MPI_Reduce_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Reduce_c
#ifndef PyMPI_HAVE_MPI_Reduce_c
extern int MPI_Reduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Reduce_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6) { return _pympi_CALL(MPI_Reduce_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Reduce_c _pympi_MPI_Reduce_c

PyMPI_LOCAL int _pympi__MPI_Allreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return MPI_Allreduce_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Allreduce_c
#ifndef PyMPI_HAVE_MPI_Allreduce_c
extern int MPI_Allreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Allreduce_c)
PyMPI_LOCAL int _pympi_MPI_Allreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return _pympi_CALL(MPI_Allreduce_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Allreduce_c _pympi_MPI_Allreduce_c

PyMPI_LOCAL int _pympi__MPI_Reduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return MPI_Reduce_scatter_block_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Reduce_scatter_block_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_block_c
extern int MPI_Reduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Reduce_scatter_block_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return _pympi_CALL(MPI_Reduce_scatter_block_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Reduce_scatter_block_c _pympi_MPI_Reduce_scatter_block_c

PyMPI_LOCAL int _pympi__MPI_Reduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return MPI_Reduce_scatter_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Reduce_scatter_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_c
extern int MPI_Reduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Reduce_scatter_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return _pympi_CALL(MPI_Reduce_scatter_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Reduce_scatter_c _pympi_MPI_Reduce_scatter_c

PyMPI_LOCAL int _pympi__MPI_Scan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return MPI_Scan_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Scan_c
#ifndef PyMPI_HAVE_MPI_Scan_c
extern int MPI_Scan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Scan_c)
PyMPI_LOCAL int _pympi_MPI_Scan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return _pympi_CALL(MPI_Scan_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Scan_c _pympi_MPI_Scan_c

PyMPI_LOCAL int _pympi__MPI_Exscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return MPI_Exscan_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Exscan_c
#ifndef PyMPI_HAVE_MPI_Exscan_c
extern int MPI_Exscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif
_pympi_WEAK(MPI_Exscan_c)
PyMPI_LOCAL int _pympi_MPI_Exscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5) { return _pympi_CALL(MPI_Exscan_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Exscan_c _pympi_MPI_Exscan_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return MPI_Neighbor_allgather_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Neighbor_allgather_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgather_c
extern int MPI_Neighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Neighbor_allgather_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return _pympi_CALL(MPI_Neighbor_allgather_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Neighbor_allgather_c _pympi_MPI_Neighbor_allgather_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7) { return MPI_Neighbor_allgatherv_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Neighbor_allgatherv_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgatherv_c
extern int MPI_Neighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7);
#endif
_pympi_WEAK(MPI_Neighbor_allgatherv_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7) { return _pympi_CALL(MPI_Neighbor_allgatherv_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Neighbor_allgatherv_c _pympi_MPI_Neighbor_allgatherv_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return MPI_Neighbor_alltoall_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Neighbor_alltoall_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoall_c
extern int MPI_Neighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif
_pympi_WEAK(MPI_Neighbor_alltoall_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6) { return _pympi_CALL(MPI_Neighbor_alltoall_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Neighbor_alltoall_c _pympi_MPI_Neighbor_alltoall_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8) { return MPI_Neighbor_alltoallv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Neighbor_alltoallv_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallv_c
extern int MPI_Neighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8);
#endif
_pympi_WEAK(MPI_Neighbor_alltoallv_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8) { return _pympi_CALL(MPI_Neighbor_alltoallv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_alltoallv_c _pympi_MPI_Neighbor_alltoallv_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8) { return MPI_Neighbor_alltoallw_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Neighbor_alltoallw_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallw_c
extern int MPI_Neighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8);
#endif
_pympi_WEAK(MPI_Neighbor_alltoallw_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8) { return _pympi_CALL(MPI_Neighbor_alltoallw_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_alltoallw_c _pympi_MPI_Neighbor_alltoallw_c

PyMPI_LOCAL int _pympi__MPI_Ibcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Request* a5) { return MPI_Ibcast_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Ibcast_c
#ifndef PyMPI_HAVE_MPI_Ibcast_c
extern int MPI_Ibcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_Ibcast_c)
PyMPI_LOCAL int _pympi_MPI_Ibcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Request* a5) { return _pympi_CALL(MPI_Ibcast_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Ibcast_c _pympi_MPI_Ibcast_c

PyMPI_LOCAL int _pympi__MPI_Igather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8) { return MPI_Igather_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Igather_c
#ifndef PyMPI_HAVE_MPI_Igather_c
extern int MPI_Igather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Igather_c)
PyMPI_LOCAL int _pympi_MPI_Igather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8) { return _pympi_CALL(MPI_Igather_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Igather_c _pympi_MPI_Igather_c

PyMPI_LOCAL int _pympi__MPI_Igatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9) { return MPI_Igatherv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Igatherv_c
#ifndef PyMPI_HAVE_MPI_Igatherv_c
extern int MPI_Igatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Igatherv_c)
PyMPI_LOCAL int _pympi_MPI_Igatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9) { return _pympi_CALL(MPI_Igatherv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Igatherv_c _pympi_MPI_Igatherv_c

PyMPI_LOCAL int _pympi__MPI_Iscatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8) { return MPI_Iscatter_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Iscatter_c
#ifndef PyMPI_HAVE_MPI_Iscatter_c
extern int MPI_Iscatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Iscatter_c)
PyMPI_LOCAL int _pympi_MPI_Iscatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8) { return _pympi_CALL(MPI_Iscatter_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Iscatter_c _pympi_MPI_Iscatter_c

PyMPI_LOCAL int _pympi__MPI_Iscatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9) { return MPI_Iscatterv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Iscatterv_c
#ifndef PyMPI_HAVE_MPI_Iscatterv_c
extern int MPI_Iscatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Iscatterv_c)
PyMPI_LOCAL int _pympi_MPI_Iscatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9) { return _pympi_CALL(MPI_Iscatterv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Iscatterv_c _pympi_MPI_Iscatterv_c

PyMPI_LOCAL int _pympi__MPI_Iallgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return MPI_Iallgather_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Iallgather_c
#ifndef PyMPI_HAVE_MPI_Iallgather_c
extern int MPI_Iallgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Iallgather_c)
PyMPI_LOCAL int _pympi_MPI_Iallgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return _pympi_CALL(MPI_Iallgather_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Iallgather_c _pympi_MPI_Iallgather_c

PyMPI_LOCAL int _pympi__MPI_Iallgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8) { return MPI_Iallgatherv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Iallgatherv_c
#ifndef PyMPI_HAVE_MPI_Iallgatherv_c
extern int MPI_Iallgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Iallgatherv_c)
PyMPI_LOCAL int _pympi_MPI_Iallgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8) { return _pympi_CALL(MPI_Iallgatherv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Iallgatherv_c _pympi_MPI_Iallgatherv_c

PyMPI_LOCAL int _pympi__MPI_Ialltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return MPI_Ialltoall_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Ialltoall_c
#ifndef PyMPI_HAVE_MPI_Ialltoall_c
extern int MPI_Ialltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Ialltoall_c)
PyMPI_LOCAL int _pympi_MPI_Ialltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return _pympi_CALL(MPI_Ialltoall_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Ialltoall_c _pympi_MPI_Ialltoall_c

PyMPI_LOCAL int _pympi__MPI_Ialltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9) { return MPI_Ialltoallv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Ialltoallv_c
#ifndef PyMPI_HAVE_MPI_Ialltoallv_c
extern int MPI_Ialltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Ialltoallv_c)
PyMPI_LOCAL int _pympi_MPI_Ialltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9) { return _pympi_CALL(MPI_Ialltoallv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Ialltoallv_c _pympi_MPI_Ialltoallv_c

PyMPI_LOCAL int _pympi__MPI_Ialltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9) { return MPI_Ialltoallw_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Ialltoallw_c
#ifndef PyMPI_HAVE_MPI_Ialltoallw_c
extern int MPI_Ialltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Ialltoallw_c)
PyMPI_LOCAL int _pympi_MPI_Ialltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9) { return _pympi_CALL(MPI_Ialltoallw_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Ialltoallw_c _pympi_MPI_Ialltoallw_c

PyMPI_LOCAL int _pympi__MPI_Ireduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Request* a7) { return MPI_Ireduce_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Ireduce_c
#ifndef PyMPI_HAVE_MPI_Ireduce_c
extern int MPI_Ireduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Ireduce_c)
PyMPI_LOCAL int _pympi_MPI_Ireduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Request* a7) { return _pympi_CALL(MPI_Ireduce_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Ireduce_c _pympi_MPI_Ireduce_c

PyMPI_LOCAL int _pympi__MPI_Iallreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Iallreduce_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Iallreduce_c
#ifndef PyMPI_HAVE_MPI_Iallreduce_c
extern int MPI_Iallreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Iallreduce_c)
PyMPI_LOCAL int _pympi_MPI_Iallreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Iallreduce_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Iallreduce_c _pympi_MPI_Iallreduce_c

PyMPI_LOCAL int _pympi__MPI_Ireduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Ireduce_scatter_block_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Ireduce_scatter_block_c
#ifndef PyMPI_HAVE_MPI_Ireduce_scatter_block_c
extern int MPI_Ireduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Ireduce_scatter_block_c)
PyMPI_LOCAL int _pympi_MPI_Ireduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Ireduce_scatter_block_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Ireduce_scatter_block_c _pympi_MPI_Ireduce_scatter_block_c

PyMPI_LOCAL int _pympi__MPI_Ireduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Ireduce_scatter_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Ireduce_scatter_c
#ifndef PyMPI_HAVE_MPI_Ireduce_scatter_c
extern int MPI_Ireduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Ireduce_scatter_c)
PyMPI_LOCAL int _pympi_MPI_Ireduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Ireduce_scatter_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Ireduce_scatter_c _pympi_MPI_Ireduce_scatter_c

PyMPI_LOCAL int _pympi__MPI_Iscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Iscan_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Iscan_c
#ifndef PyMPI_HAVE_MPI_Iscan_c
extern int MPI_Iscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Iscan_c)
PyMPI_LOCAL int _pympi_MPI_Iscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Iscan_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Iscan_c _pympi_MPI_Iscan_c

PyMPI_LOCAL int _pympi__MPI_Iexscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return MPI_Iexscan_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Iexscan_c
#ifndef PyMPI_HAVE_MPI_Iexscan_c
extern int MPI_Iexscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Iexscan_c)
PyMPI_LOCAL int _pympi_MPI_Iexscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6) { return _pympi_CALL(MPI_Iexscan_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Iexscan_c _pympi_MPI_Iexscan_c

PyMPI_LOCAL int _pympi__MPI_Ineighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return MPI_Ineighbor_allgather_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Ineighbor_allgather_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_allgather_c
extern int MPI_Ineighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Ineighbor_allgather_c)
PyMPI_LOCAL int _pympi_MPI_Ineighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return _pympi_CALL(MPI_Ineighbor_allgather_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Ineighbor_allgather_c _pympi_MPI_Ineighbor_allgather_c

PyMPI_LOCAL int _pympi__MPI_Ineighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8) { return MPI_Ineighbor_allgatherv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Ineighbor_allgatherv_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_allgatherv_c
extern int MPI_Ineighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Ineighbor_allgatherv_c)
PyMPI_LOCAL int _pympi_MPI_Ineighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8) { return _pympi_CALL(MPI_Ineighbor_allgatherv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Ineighbor_allgatherv_c _pympi_MPI_Ineighbor_allgatherv_c

PyMPI_LOCAL int _pympi__MPI_Ineighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return MPI_Ineighbor_alltoall_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Ineighbor_alltoall_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_alltoall_c
extern int MPI_Ineighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Ineighbor_alltoall_c)
PyMPI_LOCAL int _pympi_MPI_Ineighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7) { return _pympi_CALL(MPI_Ineighbor_alltoall_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Ineighbor_alltoall_c _pympi_MPI_Ineighbor_alltoall_c

PyMPI_LOCAL int _pympi__MPI_Ineighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9) { return MPI_Ineighbor_alltoallv_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Ineighbor_alltoallv_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_alltoallv_c
extern int MPI_Ineighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Ineighbor_alltoallv_c)
PyMPI_LOCAL int _pympi_MPI_Ineighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9) { return _pympi_CALL(MPI_Ineighbor_alltoallv_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Ineighbor_alltoallv_c _pympi_MPI_Ineighbor_alltoallv_c

PyMPI_LOCAL int _pympi__MPI_Ineighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9) { return MPI_Ineighbor_alltoallw_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Ineighbor_alltoallw_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_alltoallw_c
extern int MPI_Ineighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Ineighbor_alltoallw_c)
PyMPI_LOCAL int _pympi_MPI_Ineighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9) { return _pympi_CALL(MPI_Ineighbor_alltoallw_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Ineighbor_alltoallw_c _pympi_MPI_Ineighbor_alltoallw_c

PyMPI_LOCAL int _pympi__MPI_Bcast_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6) { return MPI_Bcast_init_c(a0,a1,a2,a3,a4,a5,a6); }
#undef MPI_Bcast_init_c
#ifndef PyMPI_HAVE_MPI_Bcast_init_c
extern int MPI_Bcast_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6);
#endif
_pympi_WEAK(MPI_Bcast_init_c)
PyMPI_LOCAL int _pympi_MPI_Bcast_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6) { return _pympi_CALL(MPI_Bcast_init_c,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Bcast_init_c _pympi_MPI_Bcast_init_c

PyMPI_LOCAL int _pympi__MPI_Gather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Gather_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Gather_init_c
#ifndef PyMPI_HAVE_MPI_Gather_init_c
extern int MPI_Gather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Gather_init_c)
PyMPI_LOCAL int _pympi_MPI_Gather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Gather_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Gather_init_c _pympi_MPI_Gather_init_c

PyMPI_LOCAL int _pympi__MPI_Gatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Gatherv_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Gatherv_init_c
#ifndef PyMPI_HAVE_MPI_Gatherv_init_c
extern int MPI_Gatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Gatherv_init_c)
PyMPI_LOCAL int _pympi_MPI_Gatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Gatherv_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Gatherv_init_c _pympi_MPI_Gatherv_init_c

PyMPI_LOCAL int _pympi__MPI_Scatter_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Scatter_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Scatter_init_c
#ifndef PyMPI_HAVE_MPI_Scatter_init_c
extern int MPI_Scatter_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Scatter_init_c)
PyMPI_LOCAL int _pympi_MPI_Scatter_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Scatter_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Scatter_init_c _pympi_MPI_Scatter_init_c

PyMPI_LOCAL int _pympi__MPI_Scatterv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Scatterv_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Scatterv_init_c
#ifndef PyMPI_HAVE_MPI_Scatterv_init_c
extern int MPI_Scatterv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Scatterv_init_c)
PyMPI_LOCAL int _pympi_MPI_Scatterv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Scatterv_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Scatterv_init_c _pympi_MPI_Scatterv_init_c

PyMPI_LOCAL int _pympi__MPI_Allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Allgather_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Allgather_init_c
#ifndef PyMPI_HAVE_MPI_Allgather_init_c
extern int MPI_Allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Allgather_init_c)
PyMPI_LOCAL int _pympi_MPI_Allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Allgather_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Allgather_init_c _pympi_MPI_Allgather_init_c

PyMPI_LOCAL int _pympi__MPI_Allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Allgatherv_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Allgatherv_init_c
#ifndef PyMPI_HAVE_MPI_Allgatherv_init_c
extern int MPI_Allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Allgatherv_init_c)
PyMPI_LOCAL int _pympi_MPI_Allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Allgatherv_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Allgatherv_init_c _pympi_MPI_Allgatherv_init_c

PyMPI_LOCAL int _pympi__MPI_Alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Alltoall_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Alltoall_init_c
#ifndef PyMPI_HAVE_MPI_Alltoall_init_c
extern int MPI_Alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Alltoall_init_c)
PyMPI_LOCAL int _pympi_MPI_Alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Alltoall_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Alltoall_init_c _pympi_MPI_Alltoall_init_c

PyMPI_LOCAL int _pympi__MPI_Alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Alltoallv_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Alltoallv_init_c
#ifndef PyMPI_HAVE_MPI_Alltoallv_init_c
extern int MPI_Alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Alltoallv_init_c)
PyMPI_LOCAL int _pympi_MPI_Alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Alltoallv_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Alltoallv_init_c _pympi_MPI_Alltoallv_init_c

PyMPI_LOCAL int _pympi__MPI_Alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Alltoallw_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Alltoallw_init_c
#ifndef PyMPI_HAVE_MPI_Alltoallw_init_c
extern int MPI_Alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Alltoallw_init_c)
PyMPI_LOCAL int _pympi_MPI_Alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Alltoallw_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Alltoallw_init_c _pympi_MPI_Alltoallw_init_c

PyMPI_LOCAL int _pympi__MPI_Reduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Reduce_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Reduce_init_c
#ifndef PyMPI_HAVE_MPI_Reduce_init_c
extern int MPI_Reduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Reduce_init_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Reduce_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Reduce_init_c _pympi_MPI_Reduce_init_c

PyMPI_LOCAL int _pympi__MPI_Allreduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Allreduce_init_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Allreduce_init_c
#ifndef PyMPI_HAVE_MPI_Allreduce_init_c
extern int MPI_Allreduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Allreduce_init_c)
PyMPI_LOCAL int _pympi_MPI_Allreduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Allreduce_init_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Allreduce_init_c _pympi_MPI_Allreduce_init_c

PyMPI_LOCAL int _pympi__MPI_Reduce_scatter_block_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Reduce_scatter_block_init_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Reduce_scatter_block_init_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_block_init_c
extern int MPI_Reduce_scatter_block_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Reduce_scatter_block_init_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_block_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Reduce_scatter_block_init_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Reduce_scatter_block_init_c _pympi_MPI_Reduce_scatter_block_init_c

PyMPI_LOCAL int _pympi__MPI_Reduce_scatter_init_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Reduce_scatter_init_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Reduce_scatter_init_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_init_c
extern int MPI_Reduce_scatter_init_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Reduce_scatter_init_c)
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_init_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Reduce_scatter_init_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Reduce_scatter_init_c _pympi_MPI_Reduce_scatter_init_c

PyMPI_LOCAL int _pympi__MPI_Scan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Scan_init_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Scan_init_c
#ifndef PyMPI_HAVE_MPI_Scan_init_c
extern int MPI_Scan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Scan_init_c)
PyMPI_LOCAL int _pympi_MPI_Scan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Scan_init_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Scan_init_c _pympi_MPI_Scan_init_c

PyMPI_LOCAL int _pympi__MPI_Exscan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return MPI_Exscan_init_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Exscan_init_c
#ifndef PyMPI_HAVE_MPI_Exscan_init_c
extern int MPI_Exscan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
_pympi_WEAK(MPI_Exscan_init_c)
PyMPI_LOCAL int _pympi_MPI_Exscan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { return _pympi_CALL(MPI_Exscan_init_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Exscan_init_c _pympi_MPI_Exscan_init_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Neighbor_allgather_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Neighbor_allgather_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgather_init_c
extern int MPI_Neighbor_allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Neighbor_allgather_init_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Neighbor_allgather_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_allgather_init_c _pympi_MPI_Neighbor_allgather_init_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return MPI_Neighbor_allgatherv_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Neighbor_allgatherv_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgatherv_init_c
extern int MPI_Neighbor_allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Neighbor_allgatherv_init_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { return _pympi_CALL(MPI_Neighbor_allgatherv_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Neighbor_allgatherv_init_c _pympi_MPI_Neighbor_allgatherv_init_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return MPI_Neighbor_alltoall_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Neighbor_alltoall_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoall_init_c
extern int MPI_Neighbor_alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Neighbor_alltoall_init_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { return _pympi_CALL(MPI_Neighbor_alltoall_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_alltoall_init_c _pympi_MPI_Neighbor_alltoall_init_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Neighbor_alltoallv_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Neighbor_alltoallv_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallv_init_c
extern int MPI_Neighbor_alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Neighbor_alltoallv_init_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Neighbor_alltoallv_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Neighbor_alltoallv_init_c _pympi_MPI_Neighbor_alltoallv_init_c

PyMPI_LOCAL int _pympi__MPI_Neighbor_alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return MPI_Neighbor_alltoallw_init_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#undef MPI_Neighbor_alltoallw_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallw_init_c
extern int MPI_Neighbor_alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
_pympi_WEAK(MPI_Neighbor_alltoallw_init_c)
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { return _pympi_CALL(MPI_Neighbor_alltoallw_init_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Neighbor_alltoallw_init_c _pympi_MPI_Neighbor_alltoallw_init_c

PyMPI_LOCAL int _pympi__MPI_Win_create_c(void* a0,MPI_Aint a1,MPI_Aint a2,MPI_Info a3,MPI_Comm a4,MPI_Win* a5) { return MPI_Win_create_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Win_create_c
#ifndef PyMPI_HAVE_MPI_Win_create_c
extern int MPI_Win_create_c(void* a0,MPI_Aint a1,MPI_Aint a2,MPI_Info a3,MPI_Comm a4,MPI_Win* a5);
#endif
_pympi_WEAK(MPI_Win_create_c)
PyMPI_LOCAL int _pympi_MPI_Win_create_c(void* a0,MPI_Aint a1,MPI_Aint a2,MPI_Info a3,MPI_Comm a4,MPI_Win* a5) { return _pympi_CALL(MPI_Win_create_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Win_create_c _pympi_MPI_Win_create_c

PyMPI_LOCAL int _pympi__MPI_Win_allocate_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5) { return MPI_Win_allocate_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Win_allocate_c
#ifndef PyMPI_HAVE_MPI_Win_allocate_c
extern int MPI_Win_allocate_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5);
#endif
_pympi_WEAK(MPI_Win_allocate_c)
PyMPI_LOCAL int _pympi_MPI_Win_allocate_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5) { return _pympi_CALL(MPI_Win_allocate_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Win_allocate_c _pympi_MPI_Win_allocate_c

PyMPI_LOCAL int _pympi__MPI_Win_allocate_shared_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5) { return MPI_Win_allocate_shared_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_Win_allocate_shared_c
#ifndef PyMPI_HAVE_MPI_Win_allocate_shared_c
extern int MPI_Win_allocate_shared_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5);
#endif
_pympi_WEAK(MPI_Win_allocate_shared_c)
PyMPI_LOCAL int _pympi_MPI_Win_allocate_shared_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5) { return _pympi_CALL(MPI_Win_allocate_shared_c,a0,a1,a2,a3,a4,a5); }
#define MPI_Win_allocate_shared_c _pympi_MPI_Win_allocate_shared_c

PyMPI_LOCAL int _pympi__MPI_Win_shared_query_c(MPI_Win a0,int a1,MPI_Aint* a2,MPI_Aint* a3,void* a4) { return MPI_Win_shared_query_c(a0,a1,a2,a3,a4); }
#undef MPI_Win_shared_query_c
#ifndef PyMPI_HAVE_MPI_Win_shared_query_c
extern int MPI_Win_shared_query_c(MPI_Win a0,int a1,MPI_Aint* a2,MPI_Aint* a3,void* a4);
#endif
_pympi_WEAK(MPI_Win_shared_query_c)
PyMPI_LOCAL int _pympi_MPI_Win_shared_query_c(MPI_Win a0,int a1,MPI_Aint* a2,MPI_Aint* a3,void* a4) { return _pympi_CALL(MPI_Win_shared_query_c,a0,a1,a2,a3,a4); }
#define MPI_Win_shared_query_c _pympi_MPI_Win_shared_query_c

PyMPI_LOCAL int _pympi__MPI_Get_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7) { return MPI_Get_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Get_c
#ifndef PyMPI_HAVE_MPI_Get_c
extern int MPI_Get_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7);
#endif
_pympi_WEAK(MPI_Get_c)
PyMPI_LOCAL int _pympi_MPI_Get_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7) { return _pympi_CALL(MPI_Get_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Get_c _pympi_MPI_Get_c

PyMPI_LOCAL int _pympi__MPI_Put_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7) { return MPI_Put_c(a0,a1,a2,a3,a4,a5,a6,a7); }
#undef MPI_Put_c
#ifndef PyMPI_HAVE_MPI_Put_c
extern int MPI_Put_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7);
#endif
_pympi_WEAK(MPI_Put_c)
PyMPI_LOCAL int _pympi_MPI_Put_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7) { return _pympi_CALL(MPI_Put_c,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Put_c _pympi_MPI_Put_c

PyMPI_LOCAL int _pympi__MPI_Accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8) { return MPI_Accumulate_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Accumulate_c
#ifndef PyMPI_HAVE_MPI_Accumulate_c
extern int MPI_Accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8);
#endif
_pympi_WEAK(MPI_Accumulate_c)
PyMPI_LOCAL int _pympi_MPI_Accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8) { return _pympi_CALL(MPI_Accumulate_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Accumulate_c _pympi_MPI_Accumulate_c

PyMPI_LOCAL int _pympi__MPI_Get_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11) { return MPI_Get_accumulate_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#undef MPI_Get_accumulate_c
#ifndef PyMPI_HAVE_MPI_Get_accumulate_c
extern int MPI_Get_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11);
#endif
_pympi_WEAK(MPI_Get_accumulate_c)
PyMPI_LOCAL int _pympi_MPI_Get_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11) { return _pympi_CALL(MPI_Get_accumulate_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#define MPI_Get_accumulate_c _pympi_MPI_Get_accumulate_c

PyMPI_LOCAL int _pympi__MPI_Rget_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8) { return MPI_Rget_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Rget_c
#ifndef PyMPI_HAVE_MPI_Rget_c
extern int MPI_Rget_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Rget_c)
PyMPI_LOCAL int _pympi_MPI_Rget_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8) { return _pympi_CALL(MPI_Rget_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Rget_c _pympi_MPI_Rget_c

PyMPI_LOCAL int _pympi__MPI_Rput_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8) { return MPI_Rput_c(a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#undef MPI_Rput_c
#ifndef PyMPI_HAVE_MPI_Rput_c
extern int MPI_Rput_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8);
#endif
_pympi_WEAK(MPI_Rput_c)
PyMPI_LOCAL int _pympi_MPI_Rput_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8) { return _pympi_CALL(MPI_Rput_c,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Rput_c _pympi_MPI_Rput_c

PyMPI_LOCAL int _pympi__MPI_Raccumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8,MPI_Request* a9) { return MPI_Raccumulate_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#undef MPI_Raccumulate_c
#ifndef PyMPI_HAVE_MPI_Raccumulate_c
extern int MPI_Raccumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8,MPI_Request* a9);
#endif
_pympi_WEAK(MPI_Raccumulate_c)
PyMPI_LOCAL int _pympi_MPI_Raccumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8,MPI_Request* a9) { return _pympi_CALL(MPI_Raccumulate_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Raccumulate_c _pympi_MPI_Raccumulate_c

PyMPI_LOCAL int _pympi__MPI_Rget_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11,MPI_Request* a12) { return MPI_Rget_accumulate_c(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12); }
#undef MPI_Rget_accumulate_c
#ifndef PyMPI_HAVE_MPI_Rget_accumulate_c
extern int MPI_Rget_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11,MPI_Request* a12);
#endif
_pympi_WEAK(MPI_Rget_accumulate_c)
PyMPI_LOCAL int _pympi_MPI_Rget_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11,MPI_Request* a12) { return _pympi_CALL(MPI_Rget_accumulate_c,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12); }
#define MPI_Rget_accumulate_c _pympi_MPI_Rget_accumulate_c

PyMPI_LOCAL int _pympi__MPI_File_iread_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5) { return MPI_File_iread_at_all(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_iread_at_all
#ifndef PyMPI_HAVE_MPI_File_iread_at_all
extern int MPI_File_iread_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_File_iread_at_all)
PyMPI_LOCAL int _pympi_MPI_File_iread_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5) { return _pympi_CALL(MPI_File_iread_at_all,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iread_at_all _pympi_MPI_File_iread_at_all

PyMPI_LOCAL int _pympi__MPI_File_iwrite_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5) { return MPI_File_iwrite_at_all(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_iwrite_at_all
#ifndef PyMPI_HAVE_MPI_File_iwrite_at_all
extern int MPI_File_iwrite_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_File_iwrite_at_all)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5) { return _pympi_CALL(MPI_File_iwrite_at_all,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iwrite_at_all _pympi_MPI_File_iwrite_at_all

PyMPI_LOCAL int _pympi__MPI_File_iread_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iread_all(a0,a1,a2,a3,a4); }
#undef MPI_File_iread_all
#ifndef PyMPI_HAVE_MPI_File_iread_all
extern int MPI_File_iread_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iread_all)
PyMPI_LOCAL int _pympi_MPI_File_iread_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iread_all,a0,a1,a2,a3,a4); }
#define MPI_File_iread_all _pympi_MPI_File_iread_all

PyMPI_LOCAL int _pympi__MPI_File_iwrite_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iwrite_all(a0,a1,a2,a3,a4); }
#undef MPI_File_iwrite_all
#ifndef PyMPI_HAVE_MPI_File_iwrite_all
extern int MPI_File_iwrite_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iwrite_all)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iwrite_all,a0,a1,a2,a3,a4); }
#define MPI_File_iwrite_all _pympi_MPI_File_iwrite_all

PyMPI_LOCAL int _pympi__MPI_File_read_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return MPI_File_read_at_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_read_at_c
#ifndef PyMPI_HAVE_MPI_File_read_at_c
extern int MPI_File_read_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif
_pympi_WEAK(MPI_File_read_at_c)
PyMPI_LOCAL int _pympi_MPI_File_read_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return _pympi_CALL(MPI_File_read_at_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_read_at_c _pympi_MPI_File_read_at_c

PyMPI_LOCAL int _pympi__MPI_File_read_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return MPI_File_read_at_all_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_read_at_all_c
#ifndef PyMPI_HAVE_MPI_File_read_at_all_c
extern int MPI_File_read_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif
_pympi_WEAK(MPI_File_read_at_all_c)
PyMPI_LOCAL int _pympi_MPI_File_read_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return _pympi_CALL(MPI_File_read_at_all_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_read_at_all_c _pympi_MPI_File_read_at_all_c

PyMPI_LOCAL int _pympi__MPI_File_write_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return MPI_File_write_at_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_write_at_c
#ifndef PyMPI_HAVE_MPI_File_write_at_c
extern int MPI_File_write_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif
_pympi_WEAK(MPI_File_write_at_c)
PyMPI_LOCAL int _pympi_MPI_File_write_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return _pympi_CALL(MPI_File_write_at_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_write_at_c _pympi_MPI_File_write_at_c

PyMPI_LOCAL int _pympi__MPI_File_write_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return MPI_File_write_at_all_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_write_at_all_c
#ifndef PyMPI_HAVE_MPI_File_write_at_all_c
extern int MPI_File_write_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif
_pympi_WEAK(MPI_File_write_at_all_c)
PyMPI_LOCAL int _pympi_MPI_File_write_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5) { return _pympi_CALL(MPI_File_write_at_all_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_write_at_all_c _pympi_MPI_File_write_at_all_c

PyMPI_LOCAL int _pympi__MPI_File_iread_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return MPI_File_iread_at_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_iread_at_c
#ifndef PyMPI_HAVE_MPI_File_iread_at_c
extern int MPI_File_iread_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_File_iread_at_c)
PyMPI_LOCAL int _pympi_MPI_File_iread_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return _pympi_CALL(MPI_File_iread_at_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iread_at_c _pympi_MPI_File_iread_at_c

PyMPI_LOCAL int _pympi__MPI_File_iread_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return MPI_File_iread_at_all_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_iread_at_all_c
#ifndef PyMPI_HAVE_MPI_File_iread_at_all_c
extern int MPI_File_iread_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_File_iread_at_all_c)
PyMPI_LOCAL int _pympi_MPI_File_iread_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return _pympi_CALL(MPI_File_iread_at_all_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iread_at_all_c _pympi_MPI_File_iread_at_all_c

PyMPI_LOCAL int _pympi__MPI_File_iwrite_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return MPI_File_iwrite_at_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_iwrite_at_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_at_c
extern int MPI_File_iwrite_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_File_iwrite_at_c)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return _pympi_CALL(MPI_File_iwrite_at_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iwrite_at_c _pympi_MPI_File_iwrite_at_c

PyMPI_LOCAL int _pympi__MPI_File_iwrite_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return MPI_File_iwrite_at_all_c(a0,a1,a2,a3,a4,a5); }
#undef MPI_File_iwrite_at_all_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_at_all_c
extern int MPI_File_iwrite_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif
_pympi_WEAK(MPI_File_iwrite_at_all_c)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5) { return _pympi_CALL(MPI_File_iwrite_at_all_c,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iwrite_at_all_c _pympi_MPI_File_iwrite_at_all_c

PyMPI_LOCAL int _pympi__MPI_File_read_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_read_c(a0,a1,a2,a3,a4); }
#undef MPI_File_read_c
#ifndef PyMPI_HAVE_MPI_File_read_c
extern int MPI_File_read_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_read_c)
PyMPI_LOCAL int _pympi_MPI_File_read_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_read_c,a0,a1,a2,a3,a4); }
#define MPI_File_read_c _pympi_MPI_File_read_c

PyMPI_LOCAL int _pympi__MPI_File_read_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_read_all_c(a0,a1,a2,a3,a4); }
#undef MPI_File_read_all_c
#ifndef PyMPI_HAVE_MPI_File_read_all_c
extern int MPI_File_read_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_read_all_c)
PyMPI_LOCAL int _pympi_MPI_File_read_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_read_all_c,a0,a1,a2,a3,a4); }
#define MPI_File_read_all_c _pympi_MPI_File_read_all_c

PyMPI_LOCAL int _pympi__MPI_File_write_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_write_c(a0,a1,a2,a3,a4); }
#undef MPI_File_write_c
#ifndef PyMPI_HAVE_MPI_File_write_c
extern int MPI_File_write_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_write_c)
PyMPI_LOCAL int _pympi_MPI_File_write_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_write_c,a0,a1,a2,a3,a4); }
#define MPI_File_write_c _pympi_MPI_File_write_c

PyMPI_LOCAL int _pympi__MPI_File_write_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_write_all_c(a0,a1,a2,a3,a4); }
#undef MPI_File_write_all_c
#ifndef PyMPI_HAVE_MPI_File_write_all_c
extern int MPI_File_write_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_write_all_c)
PyMPI_LOCAL int _pympi_MPI_File_write_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_write_all_c,a0,a1,a2,a3,a4); }
#define MPI_File_write_all_c _pympi_MPI_File_write_all_c

PyMPI_LOCAL int _pympi__MPI_File_iread_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iread_c(a0,a1,a2,a3,a4); }
#undef MPI_File_iread_c
#ifndef PyMPI_HAVE_MPI_File_iread_c
extern int MPI_File_iread_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iread_c)
PyMPI_LOCAL int _pympi_MPI_File_iread_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iread_c,a0,a1,a2,a3,a4); }
#define MPI_File_iread_c _pympi_MPI_File_iread_c

PyMPI_LOCAL int _pympi__MPI_File_iread_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iread_all_c(a0,a1,a2,a3,a4); }
#undef MPI_File_iread_all_c
#ifndef PyMPI_HAVE_MPI_File_iread_all_c
extern int MPI_File_iread_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iread_all_c)
PyMPI_LOCAL int _pympi_MPI_File_iread_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iread_all_c,a0,a1,a2,a3,a4); }
#define MPI_File_iread_all_c _pympi_MPI_File_iread_all_c

PyMPI_LOCAL int _pympi__MPI_File_iwrite_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iwrite_c(a0,a1,a2,a3,a4); }
#undef MPI_File_iwrite_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_c
extern int MPI_File_iwrite_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iwrite_c)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iwrite_c,a0,a1,a2,a3,a4); }
#define MPI_File_iwrite_c _pympi_MPI_File_iwrite_c

PyMPI_LOCAL int _pympi__MPI_File_iwrite_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iwrite_all_c(a0,a1,a2,a3,a4); }
#undef MPI_File_iwrite_all_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_all_c
extern int MPI_File_iwrite_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iwrite_all_c)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iwrite_all_c,a0,a1,a2,a3,a4); }
#define MPI_File_iwrite_all_c _pympi_MPI_File_iwrite_all_c

PyMPI_LOCAL int _pympi__MPI_File_read_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_read_shared_c(a0,a1,a2,a3,a4); }
#undef MPI_File_read_shared_c
#ifndef PyMPI_HAVE_MPI_File_read_shared_c
extern int MPI_File_read_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_read_shared_c)
PyMPI_LOCAL int _pympi_MPI_File_read_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_read_shared_c,a0,a1,a2,a3,a4); }
#define MPI_File_read_shared_c _pympi_MPI_File_read_shared_c

PyMPI_LOCAL int _pympi__MPI_File_write_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_write_shared_c(a0,a1,a2,a3,a4); }
#undef MPI_File_write_shared_c
#ifndef PyMPI_HAVE_MPI_File_write_shared_c
extern int MPI_File_write_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_write_shared_c)
PyMPI_LOCAL int _pympi_MPI_File_write_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_write_shared_c,a0,a1,a2,a3,a4); }
#define MPI_File_write_shared_c _pympi_MPI_File_write_shared_c

PyMPI_LOCAL int _pympi__MPI_File_iread_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iread_shared_c(a0,a1,a2,a3,a4); }
#undef MPI_File_iread_shared_c
#ifndef PyMPI_HAVE_MPI_File_iread_shared_c
extern int MPI_File_iread_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iread_shared_c)
PyMPI_LOCAL int _pympi_MPI_File_iread_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iread_shared_c,a0,a1,a2,a3,a4); }
#define MPI_File_iread_shared_c _pympi_MPI_File_iread_shared_c

PyMPI_LOCAL int _pympi__MPI_File_iwrite_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return MPI_File_iwrite_shared_c(a0,a1,a2,a3,a4); }
#undef MPI_File_iwrite_shared_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_shared_c
extern int MPI_File_iwrite_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif
_pympi_WEAK(MPI_File_iwrite_shared_c)
PyMPI_LOCAL int _pympi_MPI_File_iwrite_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4) { return _pympi_CALL(MPI_File_iwrite_shared_c,a0,a1,a2,a3,a4); }
#define MPI_File_iwrite_shared_c _pympi_MPI_File_iwrite_shared_c

PyMPI_LOCAL int _pympi__MPI_File_read_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_read_ordered_c(a0,a1,a2,a3,a4); }
#undef MPI_File_read_ordered_c
#ifndef PyMPI_HAVE_MPI_File_read_ordered_c
extern int MPI_File_read_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_read_ordered_c)
PyMPI_LOCAL int _pympi_MPI_File_read_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_read_ordered_c,a0,a1,a2,a3,a4); }
#define MPI_File_read_ordered_c _pympi_MPI_File_read_ordered_c

PyMPI_LOCAL int _pympi__MPI_File_write_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return MPI_File_write_ordered_c(a0,a1,a2,a3,a4); }
#undef MPI_File_write_ordered_c
#ifndef PyMPI_HAVE_MPI_File_write_ordered_c
extern int MPI_File_write_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif
_pympi_WEAK(MPI_File_write_ordered_c)
PyMPI_LOCAL int _pympi_MPI_File_write_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4) { return _pympi_CALL(MPI_File_write_ordered_c,a0,a1,a2,a3,a4); }
#define MPI_File_write_ordered_c _pympi_MPI_File_write_ordered_c

PyMPI_LOCAL int _pympi__MPI_File_read_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4) { return MPI_File_read_at_all_begin_c(a0,a1,a2,a3,a4); }
#undef MPI_File_read_at_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_read_at_all_begin_c
extern int MPI_File_read_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4);
#endif
_pympi_WEAK(MPI_File_read_at_all_begin_c)
PyMPI_LOCAL int _pympi_MPI_File_read_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4) { return _pympi_CALL(MPI_File_read_at_all_begin_c,a0,a1,a2,a3,a4); }
#define MPI_File_read_at_all_begin_c _pympi_MPI_File_read_at_all_begin_c

PyMPI_LOCAL int _pympi__MPI_File_write_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4) { return MPI_File_write_at_all_begin_c(a0,a1,a2,a3,a4); }
#undef MPI_File_write_at_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_write_at_all_begin_c
extern int MPI_File_write_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4);
#endif
_pympi_WEAK(MPI_File_write_at_all_begin_c)
PyMPI_LOCAL int _pympi_MPI_File_write_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4) { return _pympi_CALL(MPI_File_write_at_all_begin_c,a0,a1,a2,a3,a4); }
#define MPI_File_write_at_all_begin_c _pympi_MPI_File_write_at_all_begin_c

PyMPI_LOCAL int _pympi__MPI_File_read_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return MPI_File_read_all_begin_c(a0,a1,a2,a3); }
#undef MPI_File_read_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_read_all_begin_c
extern int MPI_File_read_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif
_pympi_WEAK(MPI_File_read_all_begin_c)
PyMPI_LOCAL int _pympi_MPI_File_read_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return _pympi_CALL(MPI_File_read_all_begin_c,a0,a1,a2,a3); }
#define MPI_File_read_all_begin_c _pympi_MPI_File_read_all_begin_c

PyMPI_LOCAL int _pympi__MPI_File_write_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return MPI_File_write_all_begin_c(a0,a1,a2,a3); }
#undef MPI_File_write_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_write_all_begin_c
extern int MPI_File_write_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif
_pympi_WEAK(MPI_File_write_all_begin_c)
PyMPI_LOCAL int _pympi_MPI_File_write_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return _pympi_CALL(MPI_File_write_all_begin_c,a0,a1,a2,a3); }
#define MPI_File_write_all_begin_c _pympi_MPI_File_write_all_begin_c

PyMPI_LOCAL int _pympi__MPI_File_read_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return MPI_File_read_ordered_begin_c(a0,a1,a2,a3); }
#undef MPI_File_read_ordered_begin_c
#ifndef PyMPI_HAVE_MPI_File_read_ordered_begin_c
extern int MPI_File_read_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif
_pympi_WEAK(MPI_File_read_ordered_begin_c)
PyMPI_LOCAL int _pympi_MPI_File_read_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return _pympi_CALL(MPI_File_read_ordered_begin_c,a0,a1,a2,a3); }
#define MPI_File_read_ordered_begin_c _pympi_MPI_File_read_ordered_begin_c

PyMPI_LOCAL int _pympi__MPI_File_write_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return MPI_File_write_ordered_begin_c(a0,a1,a2,a3); }
#undef MPI_File_write_ordered_begin_c
#ifndef PyMPI_HAVE_MPI_File_write_ordered_begin_c
extern int MPI_File_write_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif
_pympi_WEAK(MPI_File_write_ordered_begin_c)
PyMPI_LOCAL int _pympi_MPI_File_write_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3) { return _pympi_CALL(MPI_File_write_ordered_begin_c,a0,a1,a2,a3); }
#define MPI_File_write_ordered_begin_c _pympi_MPI_File_write_ordered_begin_c

PyMPI_LOCAL int _pympi__MPI_File_get_type_extent_c(MPI_File a0,MPI_Datatype a1,MPI_Count* a2) { return MPI_File_get_type_extent_c(a0,a1,a2); }
#undef MPI_File_get_type_extent_c
#ifndef PyMPI_HAVE_MPI_File_get_type_extent_c
extern int MPI_File_get_type_extent_c(MPI_File a0,MPI_Datatype a1,MPI_Count* a2);
#endif
_pympi_WEAK(MPI_File_get_type_extent_c)
PyMPI_LOCAL int _pympi_MPI_File_get_type_extent_c(MPI_File a0,MPI_Datatype a1,MPI_Count* a2) { return _pympi_CALL(MPI_File_get_type_extent_c,a0,a1,a2); }
#define MPI_File_get_type_extent_c _pympi_MPI_File_get_type_extent_c

PyMPI_LOCAL int _pympi__MPI_Register_datarep_c(char a0[],MPI_Datarep_conversion_function_c* a1,MPI_Datarep_conversion_function_c* a2,MPI_Datarep_extent_function* a3,void* a4) { return MPI_Register_datarep_c(a0,a1,a2,a3,a4); }
#undef MPI_Register_datarep_c
#ifndef PyMPI_HAVE_MPI_Register_datarep_c
extern int MPI_Register_datarep_c(char a0[],MPI_Datarep_conversion_function_c* a1,MPI_Datarep_conversion_function_c* a2,MPI_Datarep_extent_function* a3,void* a4);
#endif
_pympi_WEAK(MPI_Register_datarep_c)
PyMPI_LOCAL int _pympi_MPI_Register_datarep_c(char a0[],MPI_Datarep_conversion_function_c* a1,MPI_Datarep_conversion_function_c* a2,MPI_Datarep_extent_function* a3,void* a4) { return _pympi_CALL(MPI_Register_datarep_c,a0,a1,a2,a3,a4); }
#define MPI_Register_datarep_c _pympi_MPI_Register_datarep_c

PyMPI_LOCAL int _pympi__MPI_Remove_error_class(int a0) { return MPI_Remove_error_class(a0); }
#undef MPI_Remove_error_class
#ifndef PyMPI_HAVE_MPI_Remove_error_class
extern int MPI_Remove_error_class(int a0);
#endif
_pympi_WEAK(MPI_Remove_error_class)
PyMPI_LOCAL int _pympi_MPI_Remove_error_class(int a0) { return _pympi_CALL(MPI_Remove_error_class,a0); }
#define MPI_Remove_error_class _pympi_MPI_Remove_error_class

PyMPI_LOCAL int _pympi__MPI_Remove_error_code(int a0) { return MPI_Remove_error_code(a0); }
#undef MPI_Remove_error_code
#ifndef PyMPI_HAVE_MPI_Remove_error_code
extern int MPI_Remove_error_code(int a0);
#endif
_pympi_WEAK(MPI_Remove_error_code)
PyMPI_LOCAL int _pympi_MPI_Remove_error_code(int a0) { return _pympi_CALL(MPI_Remove_error_code,a0); }
#define MPI_Remove_error_code _pympi_MPI_Remove_error_code

PyMPI_LOCAL int _pympi__MPI_Remove_error_string(int a0) { return MPI_Remove_error_string(a0); }
#undef MPI_Remove_error_string
#ifndef PyMPI_HAVE_MPI_Remove_error_string
extern int MPI_Remove_error_string(int a0);
#endif
_pympi_WEAK(MPI_Remove_error_string)
PyMPI_LOCAL int _pympi_MPI_Remove_error_string(int a0) { return _pympi_CALL(MPI_Remove_error_string,a0); }
#define MPI_Remove_error_string _pympi_MPI_Remove_error_string

PyMPI_LOCAL int _pympi__MPI_Get_hw_resource_info(MPI_Info* a0) { return MPI_Get_hw_resource_info(a0); }
#undef MPI_Get_hw_resource_info
#ifndef PyMPI_HAVE_MPI_Get_hw_resource_info
extern int MPI_Get_hw_resource_info(MPI_Info* a0);
#endif
_pympi_WEAK(MPI_Get_hw_resource_info)
PyMPI_LOCAL int _pympi_MPI_Get_hw_resource_info(MPI_Info* a0) { return _pympi_CALL(MPI_Get_hw_resource_info,a0); }
#define MPI_Get_hw_resource_info _pympi_MPI_Get_hw_resource_info

PyMPI_LOCAL MPI_Fint _pympi__MPI_Session_c2f(MPI_Session a0) { return MPI_Session_c2f(a0); }
#undef MPI_Session_c2f
#ifndef PyMPI_HAVE_MPI_Session_c2f
extern MPI_Fint MPI_Session_c2f(MPI_Session a0);
#endif
_pympi_WEAK(MPI_Session_c2f)
PyMPI_LOCAL MPI_Fint _pympi_MPI_Session_c2f(MPI_Session a0) { return _pympi_CALL(MPI_Session_c2f,a0); }
#define MPI_Session_c2f _pympi_MPI_Session_c2f

PyMPI_LOCAL MPI_Session _pympi__MPI_Session_f2c(MPI_Fint a0) { return MPI_Session_f2c(a0); }
#undef MPI_Session_f2c
#ifndef PyMPI_HAVE_MPI_Session_f2c
extern MPI_Session MPI_Session_f2c(MPI_Fint a0);
#endif
_pympi_WEAK(MPI_Session_f2c)
PyMPI_LOCAL MPI_Session _pympi_MPI_Session_f2c(MPI_Fint a0) { return _pympi_CALL(MPI_Session_f2c,a0); }
#define MPI_Session_f2c _pympi_MPI_Session_f2c

PyMPI_LOCAL int _pympi__MPI_Comm_revoke(MPI_Comm a0) { return MPI_Comm_revoke(a0); }
#undef MPI_Comm_revoke
#ifndef PyMPI_HAVE_MPI_Comm_revoke
extern int MPI_Comm_revoke(MPI_Comm a0);
#endif
_pympi_WEAK(MPI_Comm_revoke)
PyMPI_LOCAL int _pympi_MPI_Comm_revoke(MPI_Comm a0) { return _pympi_CALL(MPI_Comm_revoke,a0); }
#define MPI_Comm_revoke _pympi_MPI_Comm_revoke

PyMPI_LOCAL int _pympi__MPI_Comm_is_revoked(MPI_Comm a0,int* a1) { return MPI_Comm_is_revoked(a0,a1); }
#undef MPI_Comm_is_revoked
#ifndef PyMPI_HAVE_MPI_Comm_is_revoked
extern int MPI_Comm_is_revoked(MPI_Comm a0,int* a1);
#endif
_pympi_WEAK(MPI_Comm_is_revoked)
PyMPI_LOCAL int _pympi_MPI_Comm_is_revoked(MPI_Comm a0,int* a1) { return _pympi_CALL(MPI_Comm_is_revoked,a0,a1); }
#define MPI_Comm_is_revoked _pympi_MPI_Comm_is_revoked

PyMPI_LOCAL int _pympi__MPI_Comm_get_failed(MPI_Comm a0,MPI_Group* a1) { return MPI_Comm_get_failed(a0,a1); }
#undef MPI_Comm_get_failed
#ifndef PyMPI_HAVE_MPI_Comm_get_failed
extern int MPI_Comm_get_failed(MPI_Comm a0,MPI_Group* a1);
#endif
_pympi_WEAK(MPI_Comm_get_failed)
PyMPI_LOCAL int _pympi_MPI_Comm_get_failed(MPI_Comm a0,MPI_Group* a1) { return _pympi_CALL(MPI_Comm_get_failed,a0,a1); }
#define MPI_Comm_get_failed _pympi_MPI_Comm_get_failed

PyMPI_LOCAL int _pympi__MPI_Comm_ack_failed(MPI_Comm a0,int a1,int* a2) { return MPI_Comm_ack_failed(a0,a1,a2); }
#undef MPI_Comm_ack_failed
#ifndef PyMPI_HAVE_MPI_Comm_ack_failed
extern int MPI_Comm_ack_failed(MPI_Comm a0,int a1,int* a2);
#endif
_pympi_WEAK(MPI_Comm_ack_failed)
PyMPI_LOCAL int _pympi_MPI_Comm_ack_failed(MPI_Comm a0,int a1,int* a2) { return _pympi_CALL(MPI_Comm_ack_failed,a0,a1,a2); }
#define MPI_Comm_ack_failed _pympi_MPI_Comm_ack_failed

PyMPI_LOCAL int _pympi__MPI_Comm_agree(MPI_Comm a0,int* a1) { return MPI_Comm_agree(a0,a1); }
#undef MPI_Comm_agree
#ifndef PyMPI_HAVE_MPI_Comm_agree
extern int MPI_Comm_agree(MPI_Comm a0,int* a1);
#endif
_pympi_WEAK(MPI_Comm_agree)
PyMPI_LOCAL int _pympi_MPI_Comm_agree(MPI_Comm a0,int* a1) { return _pympi_CALL(MPI_Comm_agree,a0,a1); }
#define MPI_Comm_agree _pympi_MPI_Comm_agree

PyMPI_LOCAL int _pympi__MPI_Comm_iagree(MPI_Comm a0,int* a1,MPI_Request* a2) { return MPI_Comm_iagree(a0,a1,a2); }
#undef MPI_Comm_iagree
#ifndef PyMPI_HAVE_MPI_Comm_iagree
extern int MPI_Comm_iagree(MPI_Comm a0,int* a1,MPI_Request* a2);
#endif
_pympi_WEAK(MPI_Comm_iagree)
PyMPI_LOCAL int _pympi_MPI_Comm_iagree(MPI_Comm a0,int* a1,MPI_Request* a2) { return _pympi_CALL(MPI_Comm_iagree,a0,a1,a2); }
#define MPI_Comm_iagree _pympi_MPI_Comm_iagree

PyMPI_LOCAL int _pympi__MPI_Comm_shrink(MPI_Comm a0,MPI_Comm* a1) { return MPI_Comm_shrink(a0,a1); }
#undef MPI_Comm_shrink
#ifndef PyMPI_HAVE_MPI_Comm_shrink
extern int MPI_Comm_shrink(MPI_Comm a0,MPI_Comm* a1);
#endif
_pympi_WEAK(MPI_Comm_shrink)
PyMPI_LOCAL int _pympi_MPI_Comm_shrink(MPI_Comm a0,MPI_Comm* a1) { return _pympi_CALL(MPI_Comm_shrink,a0,a1); }
#define MPI_Comm_shrink _pympi_MPI_Comm_shrink

PyMPI_LOCAL int _pympi__MPI_Comm_ishrink(MPI_Comm a0,MPI_Comm* a1,MPI_Request* a2) { return MPI_Comm_ishrink(a0,a1,a2); }
#undef MPI_Comm_ishrink
#ifndef PyMPI_HAVE_MPI_Comm_ishrink
extern int MPI_Comm_ishrink(MPI_Comm a0,MPI_Comm* a1,MPI_Request* a2);
#endif
_pympi_WEAK(MPI_Comm_ishrink)
PyMPI_LOCAL int _pympi_MPI_Comm_ishrink(MPI_Comm a0,MPI_Comm* a1,MPI_Request* a2) { return _pympi_CALL(MPI_Comm_ishrink,a0,a1,a2); }
#define MPI_Comm_ishrink _pympi_MPI_Comm_ishrink

#ifdef __cplusplus
}
#endif

#undef _pympi_CALL
#undef _pympi_WEAK
#undef _pympi_Pragma

#endif /* linux || APPLE */
