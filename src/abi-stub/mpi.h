/* Generated with `python conf/mpiapigen.py` */
#ifndef MPI_H_ABI
#define MPI_H_ABI
#include <stdint.h>
#if defined(__cplusplus)
extern "C" {
#endif
typedef intptr_t MPI_Aint;
typedef int64_t MPI_Offset;
typedef MPI_Offset MPI_Count;
typedef struct { int MPI_SOURCE; int MPI_TAG; int MPI_ERROR; int MPI_internal[5]; } MPI_Status;
typedef struct MPI_ABI_Datatype* MPI_Datatype;
typedef struct MPI_ABI_Request* MPI_Request;
typedef struct MPI_ABI_Message* MPI_Message;
typedef struct MPI_ABI_Op* MPI_Op;
typedef struct MPI_ABI_Group* MPI_Group;
typedef struct MPI_ABI_Info* MPI_Info;
typedef struct MPI_ABI_Errhandler* MPI_Errhandler;
typedef struct MPI_ABI_Session* MPI_Session;
typedef struct MPI_ABI_Comm* MPI_Comm;
typedef struct MPI_ABI_Win* MPI_Win;
typedef struct MPI_ABI_File* MPI_File;
#define MPI_UNDEFINED -32766
#define MPI_ANY_SOURCE -1
#define MPI_ANY_TAG -2
#define MPI_PROC_NULL -3
#define MPI_ROOT -4
#define MPI_IDENT 201
#define MPI_CONGRUENT 202
#define MPI_SIMILAR 203
#define MPI_UNEQUAL 204
#define MPI_BOTTOM ((void*)0)
#define MPI_IN_PLACE ((void*)1)
#define MPI_KEYVAL_INVALID 0
#define MPI_MAX_OBJECT_NAME 128
#define MPI_DATATYPE_NULL ((MPI_Datatype)0x00000200)
#define MPI_PACKED ((MPI_Datatype)0x00000207)
#define MPI_BYTE ((MPI_Datatype)0x00000247)
#define MPI_AINT ((MPI_Datatype)0x00000201)
#define MPI_OFFSET ((MPI_Datatype)0x00000203)
#define MPI_COUNT ((MPI_Datatype)0x00000202)
#define MPI_CHAR ((MPI_Datatype)0x00000243)
#define MPI_WCHAR ((MPI_Datatype)0x0000023c)
#define MPI_SIGNED_CHAR ((MPI_Datatype)0x00000244)
#define MPI_SHORT ((MPI_Datatype)0x00000208)
#define MPI_INT ((MPI_Datatype)0x00000209)
#define MPI_LONG ((MPI_Datatype)0x0000020a)
#define MPI_LONG_LONG ((MPI_Datatype)0x0000020b)
#define MPI_LONG_LONG_INT ((MPI_Datatype)MPI_LONG_LONG)
#define MPI_UNSIGNED_CHAR ((MPI_Datatype)0x00000245)
#define MPI_UNSIGNED_SHORT ((MPI_Datatype)0x0000020c)
#define MPI_UNSIGNED ((MPI_Datatype)0x0000020d)
#define MPI_UNSIGNED_LONG ((MPI_Datatype)0x0000020e)
#define MPI_UNSIGNED_LONG_LONG ((MPI_Datatype)0x0000020f)
#define MPI_FLOAT ((MPI_Datatype)0x00000210)
#define MPI_DOUBLE ((MPI_Datatype)0x00000214)
#define MPI_LONG_DOUBLE ((MPI_Datatype)0x00000220)
#define MPI_C_BOOL ((MPI_Datatype)0x00000238)
#define MPI_INT8_T ((MPI_Datatype)0x00000240)
#define MPI_INT16_T ((MPI_Datatype)0x00000248)
#define MPI_INT32_T ((MPI_Datatype)0x00000250)
#define MPI_INT64_T ((MPI_Datatype)0x00000258)
#define MPI_UINT8_T ((MPI_Datatype)0x00000241)
#define MPI_UINT16_T ((MPI_Datatype)0x00000249)
#define MPI_UINT32_T ((MPI_Datatype)0x00000251)
#define MPI_UINT64_T ((MPI_Datatype)0x00000259)
#define MPI_C_COMPLEX ((MPI_Datatype)MPI_C_FLOAT_COMPLEX)
#define MPI_C_FLOAT_COMPLEX ((MPI_Datatype)0x00000212)
#define MPI_C_DOUBLE_COMPLEX ((MPI_Datatype)0x00000216)
#define MPI_C_LONG_DOUBLE_COMPLEX ((MPI_Datatype)0x00000224)
#define MPI_CXX_BOOL ((MPI_Datatype)0x00000239)
#define MPI_CXX_FLOAT_COMPLEX ((MPI_Datatype)0x00000213)
#define MPI_CXX_DOUBLE_COMPLEX ((MPI_Datatype)0x00000217)
#define MPI_CXX_LONG_DOUBLE_COMPLEX ((MPI_Datatype)0x00000225)
#define MPI_SHORT_INT ((MPI_Datatype)0x0000022c)
#define MPI_2INT ((MPI_Datatype)0x0000022b)
#define MPI_LONG_INT ((MPI_Datatype)0x0000022a)
#define MPI_FLOAT_INT ((MPI_Datatype)0x00000228)
#define MPI_DOUBLE_INT ((MPI_Datatype)0x00000229)
#define MPI_LONG_DOUBLE_INT ((MPI_Datatype)0x0000022d)
#define MPI_CHARACTER ((MPI_Datatype)0x0000021e)
#define MPI_LOGICAL ((MPI_Datatype)0x00000218)
#define MPI_INTEGER ((MPI_Datatype)0x00000219)
#define MPI_REAL ((MPI_Datatype)0x0000021a)
#define MPI_DOUBLE_PRECISION ((MPI_Datatype)0x0000021c)
#define MPI_COMPLEX ((MPI_Datatype)0x0000021b)
#define MPI_DOUBLE_COMPLEX ((MPI_Datatype)0x0000021d)
#define MPI_LOGICAL1 ((MPI_Datatype)0x000002c0)
#define MPI_LOGICAL2 ((MPI_Datatype)0x000002c8)
#define MPI_LOGICAL4 ((MPI_Datatype)0x000002d0)
#define MPI_LOGICAL8 ((MPI_Datatype)0x000002d8)
#define MPI_LOGICAL16 ((MPI_Datatype)0x000002e0)
#define MPI_INTEGER1 ((MPI_Datatype)0x000002c1)
#define MPI_INTEGER2 ((MPI_Datatype)0x000002c9)
#define MPI_INTEGER4 ((MPI_Datatype)0x000002d1)
#define MPI_INTEGER8 ((MPI_Datatype)0x000002d9)
#define MPI_INTEGER16 ((MPI_Datatype)0x000002e1)
#define MPI_REAL2 ((MPI_Datatype)0x000002ca)
#define MPI_REAL4 ((MPI_Datatype)0x000002d2)
#define MPI_REAL8 ((MPI_Datatype)0x000002da)
#define MPI_REAL16 ((MPI_Datatype)0x000002e2)
#define MPI_COMPLEX4 ((MPI_Datatype)0x000002d3)
#define MPI_COMPLEX8 ((MPI_Datatype)0x000002db)
#define MPI_COMPLEX16 ((MPI_Datatype)0x000002e3)
#define MPI_COMPLEX32 ((MPI_Datatype)0x000002eb)
int MPI_Get_address(void*, MPI_Aint*);
MPI_Aint MPI_Aint_add(MPI_Aint, MPI_Aint);
MPI_Aint MPI_Aint_diff(MPI_Aint, MPI_Aint);
int MPI_Type_dup(MPI_Datatype, MPI_Datatype*);
int MPI_Type_contiguous(int, MPI_Datatype, MPI_Datatype*);
int MPI_Type_vector(int, int, int, MPI_Datatype, MPI_Datatype*);
int MPI_Type_indexed(int, int[], int[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_indexed_block(int, int, int[], MPI_Datatype, MPI_Datatype*);
#define MPI_ORDER_C 12
#define MPI_ORDER_FORTRAN 15
int MPI_Type_create_subarray(int, int[], int[], int[], int, MPI_Datatype, MPI_Datatype*);
#define MPI_DISTRIBUTE_NONE 16
#define MPI_DISTRIBUTE_BLOCK 17
#define MPI_DISTRIBUTE_CYCLIC 18
#define MPI_DISTRIBUTE_DFLT_DARG 19
int MPI_Type_create_darray(int, int, int, int[], int[], int[], int[], int, MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_hvector(int, int, MPI_Aint, MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_hindexed(int, int[], MPI_Aint[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_hindexed_block(int, int, MPI_Aint[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_struct(int, int[], MPI_Aint[], MPI_Datatype[], MPI_Datatype*);
int MPI_Type_create_resized(MPI_Datatype, MPI_Aint, MPI_Aint, MPI_Datatype*);
int MPI_Type_size(MPI_Datatype, int*);
int MPI_Type_get_extent(MPI_Datatype, MPI_Aint*, MPI_Aint*);
int MPI_Type_get_true_extent(MPI_Datatype, MPI_Aint*, MPI_Aint*);
int MPI_Type_size_x(MPI_Datatype, MPI_Count*);
int MPI_Type_get_extent_x(MPI_Datatype, MPI_Count*, MPI_Count*);
int MPI_Type_get_true_extent_x(MPI_Datatype, MPI_Count*, MPI_Count*);
int MPI_Type_create_f90_integer(int, MPI_Datatype*);
int MPI_Type_create_f90_real(int, int, MPI_Datatype*);
int MPI_Type_create_f90_complex(int, int, MPI_Datatype*);
#define MPI_TYPECLASS_INTEGER 192
#define MPI_TYPECLASS_REAL 193
#define MPI_TYPECLASS_COMPLEX 194
int MPI_Type_match_size(int, int, MPI_Datatype*);
int MPI_Type_get_value_index(MPI_Datatype, MPI_Datatype, MPI_Datatype*);
int MPI_Type_commit(MPI_Datatype*);
int MPI_Type_free(MPI_Datatype*);
#define MPI_COMBINER_NAMED 101
#define MPI_COMBINER_DUP 102
#define MPI_COMBINER_CONTIGUOUS 103
#define MPI_COMBINER_VECTOR 104
#define MPI_COMBINER_HVECTOR 105
#define MPI_COMBINER_INDEXED 106
#define MPI_COMBINER_HINDEXED 107
#define MPI_COMBINER_INDEXED_BLOCK 108
#define MPI_COMBINER_HINDEXED_BLOCK 109
#define MPI_COMBINER_STRUCT 110
#define MPI_COMBINER_SUBARRAY 111
#define MPI_COMBINER_DARRAY 112
#define MPI_COMBINER_F90_REAL 113
#define MPI_COMBINER_F90_COMPLEX 114
#define MPI_COMBINER_F90_INTEGER 115
#define MPI_COMBINER_RESIZED 116
#define MPI_COMBINER_VALUE_INDEX 117
int MPI_Type_get_envelope(MPI_Datatype, int*, int*, int*, int*);
int MPI_Type_get_contents(MPI_Datatype, int, int, int, int[], MPI_Aint[], MPI_Datatype[]);
int MPI_Pack(void*, int, MPI_Datatype, void*, int, int*, MPI_Comm);
int MPI_Unpack(void*, int, int*, void*, int, MPI_Datatype, MPI_Comm);
int MPI_Pack_size(int, MPI_Datatype, MPI_Comm, int*);
int MPI_Pack_external(char[], void*, int, MPI_Datatype, void*, MPI_Aint, MPI_Aint*);
int MPI_Unpack_external(char[], void*, MPI_Aint, MPI_Aint*, void*, int, MPI_Datatype);
int MPI_Pack_external_size(char[], int, MPI_Datatype, MPI_Aint*);
int MPI_Type_get_name(MPI_Datatype, char[], int*);
int MPI_Type_set_name(MPI_Datatype, char[]);
int MPI_Type_get_attr(MPI_Datatype, int, void*, int*);
int MPI_Type_set_attr(MPI_Datatype, int, void*);
int MPI_Type_delete_attr(MPI_Datatype, int);
typedef int (MPI_Type_copy_attr_function)(MPI_Datatype,int,void*,void*,void*,int*);
typedef int (MPI_Type_delete_attr_function)(MPI_Datatype,int,void*,void*);
#define MPI_TYPE_NULL_COPY_FN ((MPI_Type_copy_attr_function*)0x0)
#define MPI_TYPE_DUP_FN ((MPI_Type_copy_attr_function*)0x1)
#define MPI_TYPE_NULL_DELETE_FN ((MPI_Type_delete_attr_function*)0x0)
int MPI_Type_create_keyval(MPI_Type_copy_attr_function*, MPI_Type_delete_attr_function*, int*, void*);
int MPI_Type_free_keyval(int*);
int MPI_Type_contiguous_c(MPI_Count, MPI_Datatype, MPI_Datatype*);
int MPI_Type_vector_c(MPI_Count, MPI_Count, MPI_Count, MPI_Datatype, MPI_Datatype*);
int MPI_Type_indexed_c(MPI_Count, MPI_Count[], MPI_Count[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_indexed_block_c(MPI_Count, MPI_Count, MPI_Count[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_subarray_c(int, MPI_Count[], MPI_Count[], MPI_Count[], int, MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_darray_c(int, int, int, MPI_Count[], int[], int[], int[], int, MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_hvector_c(MPI_Count, MPI_Count, MPI_Count, MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_hindexed_c(MPI_Count, MPI_Count[], MPI_Count[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_hindexed_block_c(MPI_Count, MPI_Count, MPI_Count[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_create_struct_c(MPI_Count, MPI_Count[], MPI_Count[], MPI_Datatype[], MPI_Datatype*);
int MPI_Type_create_resized_c(MPI_Datatype, MPI_Count, MPI_Count, MPI_Datatype*);
int MPI_Type_size_c(MPI_Datatype, MPI_Count*);
int MPI_Type_get_extent_c(MPI_Datatype, MPI_Count*, MPI_Count*);
int MPI_Type_get_true_extent_c(MPI_Datatype, MPI_Count*, MPI_Count*);
int MPI_Type_get_envelope_c(MPI_Datatype, MPI_Count*, MPI_Count*, MPI_Count*, MPI_Count*, int*);
int MPI_Type_get_contents_c(MPI_Datatype, MPI_Count, MPI_Count, MPI_Count, MPI_Count, int[], MPI_Aint[], MPI_Count[], MPI_Datatype[]);
int MPI_Pack_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Count*, MPI_Comm);
int MPI_Unpack_c(void*, MPI_Count, MPI_Count*, void*, MPI_Count, MPI_Datatype, MPI_Comm);
int MPI_Pack_size_c(MPI_Count, MPI_Datatype, MPI_Comm, MPI_Count*);
int MPI_Pack_external_c(char[], void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Count*);
int MPI_Unpack_external_c(char[], void*, MPI_Count, MPI_Count*, void*, MPI_Count, MPI_Datatype);
int MPI_Pack_external_size_c(char[], MPI_Count, MPI_Datatype, MPI_Count*);
#define MPI_STATUS_IGNORE ((MPI_Status*)0)
#define MPI_STATUSES_IGNORE ((MPI_Status*)0)
int MPI_Get_count(MPI_Status*, MPI_Datatype, int*);
int MPI_Get_elements(MPI_Status*, MPI_Datatype, int*);
int MPI_Status_set_elements(MPI_Status*, MPI_Datatype, int);
int MPI_Get_elements_x(MPI_Status*, MPI_Datatype, MPI_Count*);
int MPI_Status_set_elements_x(MPI_Status*, MPI_Datatype, MPI_Count);
int MPI_Test_cancelled(MPI_Status*, int*);
int MPI_Status_set_cancelled(MPI_Status*, int);
int MPI_Get_count_c(MPI_Status*, MPI_Datatype, MPI_Count*);
int MPI_Get_elements_c(MPI_Status*, MPI_Datatype, MPI_Count*);
int MPI_Status_set_elements_c(MPI_Status*, MPI_Datatype, MPI_Count);
int MPI_Status_get_source(MPI_Status*, int*);
int MPI_Status_set_source(MPI_Status*, int);
int MPI_Status_get_tag(MPI_Status*, int*);
int MPI_Status_set_tag(MPI_Status*, int);
int MPI_Status_get_error(MPI_Status*, int*);
int MPI_Status_set_error(MPI_Status*, int);
#define MPI_REQUEST_NULL ((MPI_Request)0x00000180)
int MPI_Wait(MPI_Request*, MPI_Status*);
int MPI_Test(MPI_Request*, int*, MPI_Status*);
int MPI_Request_get_status(MPI_Request, int*, MPI_Status*);
int MPI_Waitany(int, MPI_Request[], int*, MPI_Status*);
int MPI_Testany(int, MPI_Request[], int*, int*, MPI_Status*);
int MPI_Request_get_status_any(int, MPI_Request[], int*, int*, MPI_Status*);
int MPI_Waitall(int, MPI_Request[], MPI_Status[]);
int MPI_Testall(int, MPI_Request[], int*, MPI_Status[]);
int MPI_Request_get_status_all(int, MPI_Request [], int*, MPI_Status[]);
int MPI_Waitsome(int, MPI_Request[], int*, int[], MPI_Status[]);
int MPI_Testsome(int, MPI_Request[], int*, int[], MPI_Status[]);
int MPI_Request_get_status_some(int, MPI_Request[], int*, int[], MPI_Status[]);
int MPI_Cancel(MPI_Request*);
int MPI_Request_free(MPI_Request*);
int MPI_Start(MPI_Request*);
int MPI_Startall(int, MPI_Request*);
int MPI_Pready(int, MPI_Request);
int MPI_Pready_range(int, int, MPI_Request);
int MPI_Pready_list(int, int[], MPI_Request);
int MPI_Parrived(MPI_Request, int, int*);
typedef int (MPI_Grequest_cancel_function)(void*,int);
typedef int (MPI_Grequest_free_function)(void*);
typedef int (MPI_Grequest_query_function)(void*,MPI_Status*);
int MPI_Grequest_start(MPI_Grequest_query_function*, MPI_Grequest_free_function*, MPI_Grequest_cancel_function*, void*, MPI_Request*);
int MPI_Grequest_complete(MPI_Request);
#define MPI_OP_NULL ((MPI_Op)0x00000020)
#define MPI_MAX ((MPI_Op)0x00000023)
#define MPI_MIN ((MPI_Op)0x00000022)
#define MPI_SUM ((MPI_Op)0x00000021)
#define MPI_PROD ((MPI_Op)0x00000024)
#define MPI_LAND ((MPI_Op)0x00000030)
#define MPI_BAND ((MPI_Op)0x00000028)
#define MPI_LOR ((MPI_Op)0x00000031)
#define MPI_BOR ((MPI_Op)0x00000029)
#define MPI_LXOR ((MPI_Op)0x00000032)
#define MPI_BXOR ((MPI_Op)0x0000002a)
#define MPI_MAXLOC ((MPI_Op)0x00000039)
#define MPI_MINLOC ((MPI_Op)0x00000038)
#define MPI_REPLACE ((MPI_Op)0x0000003c)
#define MPI_NO_OP ((MPI_Op)0x0000003d)
int MPI_Op_free(MPI_Op*);
typedef void (MPI_User_function)(void*,void*,int*,MPI_Datatype*);
int MPI_Op_create(MPI_User_function*, int, MPI_Op*);
int MPI_Op_commutative(MPI_Op, int*);
typedef void (MPI_User_function_c)(void*,void*,MPI_Count*,MPI_Datatype*);
int MPI_Op_create_c(MPI_User_function_c*, int, MPI_Op*);
#define MPI_GROUP_NULL ((MPI_Group)0x00000108)
#define MPI_GROUP_EMPTY ((MPI_Group)0x00000109)
int MPI_Group_free(MPI_Group*);
int MPI_Group_size(MPI_Group, int*);
int MPI_Group_rank(MPI_Group, int*);
int MPI_Group_translate_ranks(MPI_Group, int, int[], MPI_Group, int[]);
int MPI_Group_compare(MPI_Group, MPI_Group, int*);
int MPI_Group_union(MPI_Group, MPI_Group, MPI_Group*);
int MPI_Group_intersection(MPI_Group, MPI_Group, MPI_Group*);
int MPI_Group_difference(MPI_Group, MPI_Group, MPI_Group*);
int MPI_Group_incl(MPI_Group, int, int[], MPI_Group*);
int MPI_Group_excl(MPI_Group, int, int[], MPI_Group*);
int MPI_Group_range_incl(MPI_Group, int, int[][3], MPI_Group*);
int MPI_Group_range_excl(MPI_Group, int, int[][3], MPI_Group*);
#define MPI_INFO_NULL ((MPI_Info)0x00000130)
#define MPI_INFO_ENV ((MPI_Info)0x00000131)
int MPI_Info_free(MPI_Info*);
int MPI_Info_create(MPI_Info*);
int MPI_Info_dup(MPI_Info, MPI_Info*);
int MPI_Info_create_env(int, char*[], MPI_Info*);
#define MPI_MAX_INFO_KEY 256
#define MPI_MAX_INFO_VAL 1024
int MPI_Info_get_string(MPI_Info, char[], int*, char[], int*);
int MPI_Info_set(MPI_Info, char[], char[]);
int MPI_Info_delete(MPI_Info, char[]);
int MPI_Info_get_nkeys(MPI_Info, int*);
int MPI_Info_get_nthkey(MPI_Info, int, char[]);
#define MPI_ERRHANDLER_NULL ((MPI_Errhandler)0x00000140)
#define MPI_ERRORS_RETURN ((MPI_Errhandler)0x00000143)
#define MPI_ERRORS_ABORT ((MPI_Errhandler)0x00000142)
#define MPI_ERRORS_ARE_FATAL ((MPI_Errhandler)0x00000141)
int MPI_Errhandler_free(MPI_Errhandler*);
#define MPI_SESSION_NULL ((MPI_Session)0x00000120)
#define MPI_MAX_PSET_NAME_LEN 1024
int MPI_Session_init(MPI_Info, MPI_Errhandler, MPI_Session*);
int MPI_Session_finalize(MPI_Session*);
int MPI_Session_get_num_psets(MPI_Session, MPI_Info, int*);
int MPI_Session_get_nth_pset(MPI_Session, MPI_Info, int, int*, char[]);
int MPI_Session_get_info(MPI_Session, MPI_Info*);
int MPI_Session_get_pset_info(MPI_Session, char[], MPI_Info*);
int MPI_Group_from_session_pset(MPI_Session, char[], MPI_Group*);
typedef void (MPI_Session_errhandler_function)(MPI_Session*,int*,...);
int MPI_Session_create_errhandler(MPI_Session_errhandler_function*, MPI_Errhandler*);
int MPI_Session_get_errhandler(MPI_Session, MPI_Errhandler*);
int MPI_Session_set_errhandler(MPI_Session, MPI_Errhandler);
int MPI_Session_call_errhandler(MPI_Session, int);
#define MPI_COMM_NULL ((MPI_Comm)0x00000100)
#define MPI_COMM_SELF ((MPI_Comm)0x00000102)
#define MPI_COMM_WORLD ((MPI_Comm)0x00000101)
int MPI_Comm_free(MPI_Comm*);
int MPI_Comm_group(MPI_Comm, MPI_Group*);
int MPI_Comm_size(MPI_Comm, int*);
int MPI_Comm_rank(MPI_Comm, int*);
int MPI_Comm_compare(MPI_Comm, MPI_Comm, int*);
int MPI_Topo_test(MPI_Comm, int*);
int MPI_Comm_test_inter(MPI_Comm, int*);
int MPI_Abort(MPI_Comm, int);
#define MPI_BSEND_OVERHEAD 512
#define MPI_BUFFER_AUTOMATIC ((void*)2)
int MPI_Buffer_attach(void*, int);
int MPI_Buffer_detach(void*, int*);
int MPI_Buffer_flush(void);
int MPI_Buffer_iflush(MPI_Request*);
int MPI_Comm_attach_buffer(MPI_Comm, void*, int);
int MPI_Comm_detach_buffer(MPI_Comm, void*, int*);
int MPI_Comm_flush_buffer(MPI_Comm);
int MPI_Comm_iflush_buffer(MPI_Comm,MPI_Request*);
int MPI_Session_attach_buffer(MPI_Session, void*, int);
int MPI_Session_detach_buffer(MPI_Session, void*, int*);
int MPI_Session_flush_buffer(MPI_Session);
int MPI_Session_iflush_buffer(MPI_Session,MPI_Request*);
int MPI_Send(void*, int, MPI_Datatype, int, int, MPI_Comm);
int MPI_Recv(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Status*);
int MPI_Sendrecv(void*, int, MPI_Datatype, int, int, void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Status*);
int MPI_Sendrecv_replace(void*, int, MPI_Datatype, int, int, int, int, MPI_Comm, MPI_Status*);
int MPI_Bsend(void*, int, MPI_Datatype, int, int, MPI_Comm);
int MPI_Ssend(void*, int, MPI_Datatype, int, int, MPI_Comm);
int MPI_Rsend(void*, int, MPI_Datatype, int, int, MPI_Comm);
int MPI_Isend(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Irecv(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Isendrecv(void*, int, MPI_Datatype, int, int, void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Isendrecv_replace(void*, int, MPI_Datatype, int, int, int, int, MPI_Comm, MPI_Request*);
int MPI_Ibsend(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Issend(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Irsend(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Send_init(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Bsend_init(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Ssend_init(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Rsend_init(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Recv_init(void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Psend_init(void*, int, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Precv_init(void*, int, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Probe(int, int, MPI_Comm, MPI_Status*);
int MPI_Iprobe(int, int, MPI_Comm, int*, MPI_Status*);
#define MPI_MESSAGE_NULL ((MPI_Message)0x00000128)
#define MPI_MESSAGE_NO_PROC ((MPI_Message)0x00000129)
int MPI_Mprobe(int, int, MPI_Comm, MPI_Message*, MPI_Status*);
int MPI_Improbe(int, int, MPI_Comm, int*, MPI_Message*, MPI_Status*);
int MPI_Mrecv(void*, int, MPI_Datatype, MPI_Message*, MPI_Status*);
int MPI_Imrecv(void*, int, MPI_Datatype, MPI_Message*, MPI_Request*);
int MPI_Barrier(MPI_Comm);
int MPI_Bcast(void*, int, MPI_Datatype, int, MPI_Comm);
int MPI_Gather(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm);
int MPI_Gatherv(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, int, MPI_Comm);
int MPI_Scatter(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm);
int MPI_Scatterv(void*, int[], int[], MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm);
int MPI_Allgather(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm);
int MPI_Allgatherv(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm);
int MPI_Alltoall(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm);
int MPI_Alltoallv(void*, int[], int[], MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm);
int MPI_Alltoallw(void*, int[], int[], MPI_Datatype[], void*, int[], int[], MPI_Datatype[], MPI_Comm);
int MPI_Reduce_local(void*, void*, int, MPI_Datatype, MPI_Op);
int MPI_Reduce(void*, void*, int, MPI_Datatype, MPI_Op, int, MPI_Comm);
int MPI_Allreduce(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Reduce_scatter_block(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Reduce_scatter(void*, void*, int[], MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Scan(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Exscan(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Neighbor_allgather(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm);
int MPI_Neighbor_allgatherv(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm);
int MPI_Neighbor_alltoall(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm);
int MPI_Neighbor_alltoallv(void*, int[], int[], MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm);
int MPI_Neighbor_alltoallw(void*, int[], MPI_Aint[], MPI_Datatype[], void*, int[], MPI_Aint[], MPI_Datatype[], MPI_Comm);
int MPI_Ibarrier(MPI_Comm, MPI_Request*);
int MPI_Ibcast(void*, int, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Igather(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Igatherv(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Iscatter(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Iscatterv(void*, int[], int[], MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Iallgather(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Iallgatherv(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ialltoall(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ialltoallv(void*, int[], int[], MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ialltoallw(void*, int[], int[], MPI_Datatype[], void*, int[], int[], MPI_Datatype[], MPI_Comm, MPI_Request*);
int MPI_Ireduce(void*, void*, int, MPI_Datatype, MPI_Op, int, MPI_Comm, MPI_Request*);
int MPI_Iallreduce(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Ireduce_scatter_block(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Ireduce_scatter(void*, void*, int[], MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Iscan(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Iexscan(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_allgather(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_allgatherv(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_alltoall(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_alltoallv(void*, int[], int[], MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_alltoallw(void*, int[], MPI_Aint[], MPI_Datatype[], void*, int[], MPI_Aint[], MPI_Datatype[], MPI_Comm, MPI_Request*);
int MPI_Barrier_init(MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Bcast_init(void*, int, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Gather_init(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Gatherv_init(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Scatter_init(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Scatterv_init(void*, int[], int[], MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Allgather_init(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Allgatherv_init(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Alltoall_init(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Alltoallv_init(void*, int[], int[], MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Alltoallw_init(void*, int[], int[], MPI_Datatype[], void*, int[], int[], MPI_Datatype[], MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Reduce_init(void*, void*, int, MPI_Datatype, MPI_Op, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Allreduce_init(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Reduce_scatter_block_init(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Reduce_scatter_init(void*, void*, int[], MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Scan_init(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Exscan_init(void*, void*, int, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_allgather_init(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_allgatherv_init(void*, int, MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_alltoall_init(void*, int, MPI_Datatype, void*, int, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_alltoallv_init(void*, int[], int[], MPI_Datatype, void*, int[], int[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_alltoallw_init(void*, int[], MPI_Aint[], MPI_Datatype[], void*, int[], MPI_Aint[], MPI_Datatype[], MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Comm_dup(MPI_Comm, MPI_Comm*);
int MPI_Comm_dup_with_info(MPI_Comm, MPI_Info, MPI_Comm*);
int MPI_Comm_idup(MPI_Comm, MPI_Comm*, MPI_Request*);
int MPI_Comm_idup_with_info(MPI_Comm, MPI_Info, MPI_Comm*, MPI_Request*);
int MPI_Comm_create(MPI_Comm, MPI_Group, MPI_Comm*);
int MPI_Comm_create_group(MPI_Comm, MPI_Group, int, MPI_Comm*);
#define MPI_MAX_STRINGTAG_LEN 1024
int MPI_Comm_create_from_group(MPI_Group, char[], MPI_Info, MPI_Errhandler, MPI_Comm*);
int MPI_Comm_split(MPI_Comm, int, int, MPI_Comm*);
#define MPI_COMM_TYPE_SHARED 221
#define MPI_COMM_TYPE_HW_GUIDED 223
#define MPI_COMM_TYPE_HW_UNGUIDED 222
#define MPI_COMM_TYPE_RESOURCE_GUIDED 224
int MPI_Comm_split_type(MPI_Comm, int, int, MPI_Info, MPI_Comm*);
int MPI_Comm_set_info(MPI_Comm, MPI_Info);
int MPI_Comm_get_info(MPI_Comm, MPI_Info*);
#define MPI_CART 211
int MPI_Cart_create(MPI_Comm, int, int[], int[], int, MPI_Comm*);
int MPI_Cartdim_get(MPI_Comm, int*);
int MPI_Cart_get(MPI_Comm, int, int[], int[], int[]);
int MPI_Cart_rank(MPI_Comm, int[], int*);
int MPI_Cart_coords(MPI_Comm, int, int, int[]);
int MPI_Cart_shift(MPI_Comm, int, int, int[], int[]);
int MPI_Cart_sub(MPI_Comm, int[], MPI_Comm*);
int MPI_Cart_map(MPI_Comm, int, int[], int[], int*);
int MPI_Dims_create(int, int, int[]);
#define MPI_GRAPH 212
int MPI_Graph_create(MPI_Comm, int, int[], int[], int, MPI_Comm*);
int MPI_Graphdims_get(MPI_Comm, int*, int*);
int MPI_Graph_get(MPI_Comm, int, int, int[], int[]);
int MPI_Graph_map(MPI_Comm, int, int[], int[], int*);
int MPI_Graph_neighbors_count(MPI_Comm, int, int*);
int MPI_Graph_neighbors(MPI_Comm, int, int, int[]);
#define MPI_DIST_GRAPH 213
#define MPI_UNWEIGHTED ((int*)10)
#define MPI_WEIGHTS_EMPTY ((int*)11)
int MPI_Dist_graph_create_adjacent(MPI_Comm, int, int[], int[], int, int[], int[], MPI_Info, int, MPI_Comm*);
int MPI_Dist_graph_create(MPI_Comm, int, int[], int[], int[], int[], MPI_Info, int, MPI_Comm*);
int MPI_Dist_graph_neighbors_count(MPI_Comm, int*, int*, int*);
int MPI_Dist_graph_neighbors(MPI_Comm, int, int[], int[], int, int[], int[]);
int MPI_Intercomm_create(MPI_Comm, int, MPI_Comm, int, int, MPI_Comm*);
int MPI_Intercomm_create_from_groups(MPI_Group, int, MPI_Group, int, char[], MPI_Info, MPI_Errhandler, MPI_Comm*);
int MPI_Comm_remote_group(MPI_Comm, MPI_Group*);
int MPI_Comm_remote_size(MPI_Comm, int*);
int MPI_Intercomm_merge(MPI_Comm, int, MPI_Comm*);
#define MPI_MAX_PORT_NAME 1024
int MPI_Open_port(MPI_Info, char[]);
int MPI_Close_port(char[]);
int MPI_Publish_name(char[], MPI_Info, char[]);
int MPI_Unpublish_name(char[], MPI_Info, char[]);
int MPI_Lookup_name(char[], MPI_Info, char[]);
int MPI_Comm_accept(char[], MPI_Info, int, MPI_Comm, MPI_Comm*);
int MPI_Comm_connect(char[], MPI_Info, int, MPI_Comm, MPI_Comm*);
int MPI_Comm_join(int, MPI_Comm*);
int MPI_Comm_disconnect(MPI_Comm*);
#define MPI_ARGV_NULL ((char**)0)
#define MPI_ARGVS_NULL ((char***)0)
#define MPI_ERRCODES_IGNORE ((int*)0)
int MPI_Comm_spawn(char[], char*[], int, MPI_Info, int, MPI_Comm, MPI_Comm*, int[]);
int MPI_Comm_spawn_multiple(int, char*[], char**[], int[], MPI_Info[], int, MPI_Comm, MPI_Comm*, int[]);
int MPI_Comm_get_parent(MPI_Comm*);
int MPI_Comm_get_name(MPI_Comm, char[], int*);
int MPI_Comm_set_name(MPI_Comm, char[]);
#define MPI_TAG_UB 501
#define MPI_IO 502
#define MPI_WTIME_IS_GLOBAL 504
#define MPI_UNIVERSE_SIZE 507
#define MPI_APPNUM 505
#define MPI_LASTUSEDCODE 506
int MPI_Comm_get_attr(MPI_Comm, int, void*, int*);
int MPI_Comm_set_attr(MPI_Comm, int, void*);
int MPI_Comm_delete_attr(MPI_Comm, int);
typedef int (MPI_Comm_copy_attr_function)(MPI_Comm,int,void*,void*,void*,int*);
typedef int (MPI_Comm_delete_attr_function)(MPI_Comm,int,void*,void*);
#define MPI_COMM_DUP_FN ((MPI_Comm_copy_attr_function*)0x1)
#define MPI_COMM_NULL_COPY_FN ((MPI_Comm_copy_attr_function*)0x0)
#define MPI_COMM_NULL_DELETE_FN ((MPI_Comm_delete_attr_function*)0x0)
int MPI_Comm_create_keyval(MPI_Comm_copy_attr_function*, MPI_Comm_delete_attr_function*, int*, void*);
int MPI_Comm_free_keyval(int*);
typedef void (MPI_Comm_errhandler_fn)(MPI_Comm*,int*,...);
typedef void (MPI_Comm_errhandler_function)(MPI_Comm*,int*,...);
int MPI_Comm_create_errhandler(MPI_Comm_errhandler_function*, MPI_Errhandler*);
int MPI_Comm_get_errhandler(MPI_Comm, MPI_Errhandler*);
int MPI_Comm_set_errhandler(MPI_Comm, MPI_Errhandler);
int MPI_Comm_call_errhandler(MPI_Comm, int);
int MPI_Buffer_attach_c(void*, MPI_Count);
int MPI_Buffer_detach_c(void*, MPI_Count*);
int MPI_Comm_attach_buffer_c(MPI_Comm, void*, MPI_Count);
int MPI_Comm_detach_buffer_c(MPI_Comm, void*, MPI_Count*);
int MPI_Session_attach_buffer_c(MPI_Session, void*, MPI_Count);
int MPI_Session_detach_buffer_c(MPI_Session, void*, MPI_Count*);
int MPI_Send_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm);
int MPI_Recv_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Status*);
int MPI_Sendrecv_c(void*, MPI_Count, MPI_Datatype, int, int, void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Status*);
int MPI_Sendrecv_replace_c(void*, MPI_Count, MPI_Datatype, int, int, int, int, MPI_Comm, MPI_Status*);
int MPI_Bsend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm);
int MPI_Ssend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm);
int MPI_Rsend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm);
int MPI_Isend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Irecv_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Isendrecv_c(void*, MPI_Count, MPI_Datatype, int, int, void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Isendrecv_replace_c(void*, MPI_Count, MPI_Datatype, int, int, int, int, MPI_Comm, MPI_Request*);
int MPI_Ibsend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Issend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Irsend_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Send_init_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Recv_init_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Bsend_init_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Ssend_init_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Rsend_init_c(void*, MPI_Count, MPI_Datatype, int, int, MPI_Comm, MPI_Request*);
int MPI_Mrecv_c(void*, MPI_Count, MPI_Datatype, MPI_Message*, MPI_Status*);
int MPI_Imrecv_c(void*, MPI_Count, MPI_Datatype, MPI_Message*, MPI_Request*);
int MPI_Bcast_c(void*, MPI_Count, MPI_Datatype, int, MPI_Comm);
int MPI_Gather_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm);
int MPI_Gatherv_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, int, MPI_Comm);
int MPI_Scatter_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm);
int MPI_Scatterv_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm);
int MPI_Allgather_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm);
int MPI_Allgatherv_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm);
int MPI_Alltoall_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm);
int MPI_Alltoallv_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm);
int MPI_Alltoallw_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], MPI_Comm);
int MPI_Reduce_local_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op);
int MPI_Reduce_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, int, MPI_Comm);
int MPI_Allreduce_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Reduce_scatter_block_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Reduce_scatter_c(void*, void*, MPI_Count[], MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Scan_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Exscan_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm);
int MPI_Neighbor_allgather_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm);
int MPI_Neighbor_allgatherv_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm);
int MPI_Neighbor_alltoall_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm);
int MPI_Neighbor_alltoallv_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm);
int MPI_Neighbor_alltoallw_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], MPI_Comm);
int MPI_Ibcast_c(void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Igather_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Igatherv_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Iscatter_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Iscatterv_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Request*);
int MPI_Iallgather_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Iallgatherv_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ialltoall_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ialltoallv_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ialltoallw_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], MPI_Comm, MPI_Request*);
int MPI_Ireduce_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, int, MPI_Comm, MPI_Request*);
int MPI_Iallreduce_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Ireduce_scatter_block_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Ireduce_scatter_c(void*, void*, MPI_Count[], MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Iscan_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Iexscan_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_allgather_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_allgatherv_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_alltoall_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_alltoallv_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Request*);
int MPI_Ineighbor_alltoallw_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], MPI_Comm, MPI_Request*);
int MPI_Bcast_init_c(void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Gather_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Gatherv_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Scatter_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Scatterv_init_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Allgather_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Allgatherv_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Alltoall_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Alltoallv_init_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Alltoallw_init_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Reduce_init_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, int, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Allreduce_init_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Reduce_scatter_block_init_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Reduce_scatter_init_c(void*, void*, MPI_Count[], MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Scan_init_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Exscan_init_c(void*, void*, MPI_Count, MPI_Datatype, MPI_Op, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_allgather_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_allgatherv_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_alltoall_init_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_alltoallv_init_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype, void*, MPI_Count[], MPI_Aint[], MPI_Datatype, MPI_Comm, MPI_Info, MPI_Request*);
int MPI_Neighbor_alltoallw_init_c(void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], void*, MPI_Count[], MPI_Aint[], MPI_Datatype[], MPI_Comm, MPI_Info, MPI_Request*);
#define MPI_WIN_NULL ((MPI_Win)0x00000110)
int MPI_Win_free(MPI_Win*);
int MPI_Win_create(void*, MPI_Aint, int, MPI_Info, MPI_Comm, MPI_Win*);
int MPI_Win_allocate(MPI_Aint, int, MPI_Info, MPI_Comm, void*, MPI_Win*);
int MPI_Win_allocate_shared(MPI_Aint, int, MPI_Info, MPI_Comm, void*, MPI_Win*);
int MPI_Win_shared_query(MPI_Win, int, MPI_Aint*, int*, void*);
int MPI_Win_create_dynamic(MPI_Info, MPI_Comm, MPI_Win*);
int MPI_Win_attach(MPI_Win, void*, MPI_Aint);
int MPI_Win_detach(MPI_Win, void*);
int MPI_Win_set_info(MPI_Win, MPI_Info);
int MPI_Win_get_info(MPI_Win, MPI_Info*);
int MPI_Win_get_group(MPI_Win, MPI_Group*);
int MPI_Get(void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Win);
int MPI_Put(void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Win);
int MPI_Accumulate(void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Op, MPI_Win);
int MPI_Get_accumulate(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Op, MPI_Win);
int MPI_Fetch_and_op(void*, void*, MPI_Datatype, int, MPI_Aint, MPI_Op, MPI_Win);
int MPI_Compare_and_swap(void*, void*, void*, MPI_Datatype, int, MPI_Aint, MPI_Win);
int MPI_Rget(void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Win, MPI_Request*);
int MPI_Rput(void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Win, MPI_Request*);
int MPI_Raccumulate(void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Op, MPI_Win, MPI_Request*);
int MPI_Rget_accumulate(void*, int, MPI_Datatype, void*, int, MPI_Datatype, int, MPI_Aint, int, MPI_Datatype, MPI_Op, MPI_Win, MPI_Request*);
#define MPI_MODE_NOCHECK 1024
#define MPI_MODE_NOSTORE 8192
#define MPI_MODE_NOPUT 4096
#define MPI_MODE_NOPRECEDE 2048
#define MPI_MODE_NOSUCCEED 16384
int MPI_Win_fence(int, MPI_Win);
int MPI_Win_post(MPI_Group, int, MPI_Win);
int MPI_Win_start(MPI_Group, int, MPI_Win);
int MPI_Win_complete(MPI_Win);
int MPI_Win_wait(MPI_Win);
int MPI_Win_test(MPI_Win, int*);
#define MPI_LOCK_EXCLUSIVE 301
#define MPI_LOCK_SHARED 302
int MPI_Win_lock(int, int, int, MPI_Win);
int MPI_Win_unlock(int, MPI_Win);
int MPI_Win_lock_all(int, MPI_Win);
int MPI_Win_unlock_all(MPI_Win);
int MPI_Win_flush(int, MPI_Win);
int MPI_Win_flush_all(MPI_Win);
int MPI_Win_flush_local(int, MPI_Win);
int MPI_Win_flush_local_all(MPI_Win);
int MPI_Win_sync(MPI_Win);
int MPI_Win_get_name(MPI_Win, char[], int*);
int MPI_Win_set_name(MPI_Win, char[]);
#define MPI_WIN_BASE 601
#define MPI_WIN_SIZE 603
#define MPI_WIN_DISP_UNIT 602
#define MPI_WIN_CREATE_FLAVOR 604
#define MPI_WIN_MODEL 605
#define MPI_WIN_FLAVOR_CREATE 311
#define MPI_WIN_FLAVOR_ALLOCATE 312
#define MPI_WIN_FLAVOR_DYNAMIC 313
#define MPI_WIN_FLAVOR_SHARED 314
#define MPI_WIN_SEPARATE 322
#define MPI_WIN_UNIFIED 321
int MPI_Win_get_attr(MPI_Win, int, void*, int*);
int MPI_Win_set_attr(MPI_Win, int, void*);
int MPI_Win_delete_attr(MPI_Win, int);
typedef int (MPI_Win_copy_attr_function)(MPI_Win,int,void*,void*,void*,int*);
typedef int (MPI_Win_delete_attr_function)(MPI_Win,int,void*,void*);
#define MPI_WIN_DUP_FN ((MPI_Win_copy_attr_function*)0x1)
#define MPI_WIN_NULL_COPY_FN ((MPI_Win_copy_attr_function*)0x0)
#define MPI_WIN_NULL_DELETE_FN ((MPI_Win_delete_attr_function*)0x0)
int MPI_Win_create_keyval(MPI_Win_copy_attr_function*, MPI_Win_delete_attr_function*, int*, void*);
int MPI_Win_free_keyval(int*);
typedef void (MPI_Win_errhandler_fn)(MPI_Win*,int*,...);
typedef void (MPI_Win_errhandler_function)(MPI_Win*,int*,...);
int MPI_Win_create_errhandler(MPI_Win_errhandler_function*, MPI_Errhandler*);
int MPI_Win_get_errhandler(MPI_Win, MPI_Errhandler*);
int MPI_Win_set_errhandler(MPI_Win, MPI_Errhandler);
int MPI_Win_call_errhandler(MPI_Win, int);
int MPI_Win_create_c(void*, MPI_Aint, MPI_Aint, MPI_Info, MPI_Comm, MPI_Win*);
int MPI_Win_allocate_c(MPI_Aint, MPI_Aint, MPI_Info, MPI_Comm, void*, MPI_Win*);
int MPI_Win_allocate_shared_c(MPI_Aint, MPI_Aint, MPI_Info, MPI_Comm, void*, MPI_Win*);
int MPI_Win_shared_query_c(MPI_Win, int, MPI_Aint*, MPI_Aint*, void*);
int MPI_Get_c(void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Win);
int MPI_Put_c(void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Win);
int MPI_Accumulate_c(void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Op, MPI_Win);
int MPI_Get_accumulate_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Op, MPI_Win);
int MPI_Rget_c(void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Win, MPI_Request*);
int MPI_Rput_c(void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Win, MPI_Request*);
int MPI_Raccumulate_c(void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Op, MPI_Win, MPI_Request*);
int MPI_Rget_accumulate_c(void*, MPI_Count, MPI_Datatype, void*, MPI_Count, MPI_Datatype, int, MPI_Aint, MPI_Count, MPI_Datatype, MPI_Op, MPI_Win, MPI_Request*);
#define MPI_FILE_NULL ((MPI_File)0x00000118)
#define MPI_MODE_RDONLY 16
#define MPI_MODE_RDWR 32
#define MPI_MODE_WRONLY 256
#define MPI_MODE_CREATE 2
#define MPI_MODE_EXCL 8
#define MPI_MODE_DELETE_ON_CLOSE 4
#define MPI_MODE_UNIQUE_OPEN 128
#define MPI_MODE_APPEND 1
#define MPI_MODE_SEQUENTIAL 64
int MPI_File_open(MPI_Comm, char[], int, MPI_Info, MPI_File*);
int MPI_File_close(MPI_File*);
int MPI_File_delete(char[], MPI_Info);
int MPI_File_set_size(MPI_File, MPI_Offset);
int MPI_File_preallocate(MPI_File, MPI_Offset);
int MPI_File_get_size(MPI_File, MPI_Offset*);
int MPI_File_get_group(MPI_File, MPI_Group*);
int MPI_File_get_amode(MPI_File, int*);
int MPI_File_set_info(MPI_File, MPI_Info);
int MPI_File_get_info(MPI_File, MPI_Info*);
int MPI_File_get_view(MPI_File, MPI_Offset*, MPI_Datatype*, MPI_Datatype*, char[]);
int MPI_File_set_view(MPI_File, MPI_Offset, MPI_Datatype, MPI_Datatype, char[], MPI_Info);
int MPI_File_read_at(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_read_at_all(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_write_at(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_write_at_all(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_iread_at(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iread_at_all(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_at(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_at_all(MPI_File, MPI_Offset, void*, int, MPI_Datatype, MPI_Request*);
#define MPI_SEEK_SET 403
#define MPI_SEEK_CUR 401
#define MPI_SEEK_END 402
#define MPI_DISPLACEMENT_CURRENT -1
int MPI_File_seek(MPI_File, MPI_Offset, int);
int MPI_File_get_position(MPI_File, MPI_Offset*);
int MPI_File_get_byte_offset(MPI_File, MPI_Offset, MPI_Offset*);
int MPI_File_read(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_read_all(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_write(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_write_all(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_iread(MPI_File, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iread_all(MPI_File, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite(MPI_File, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_all(MPI_File, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_read_shared(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_write_shared(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_iread_shared(MPI_File, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_shared(MPI_File, void*, int, MPI_Datatype, MPI_Request*);
int MPI_File_read_ordered(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_write_ordered(MPI_File, void*, int, MPI_Datatype, MPI_Status*);
int MPI_File_seek_shared(MPI_File, MPI_Offset, int);
int MPI_File_get_position_shared(MPI_File, MPI_Offset*);
int MPI_File_read_at_all_begin(MPI_File, MPI_Offset, void*, int, MPI_Datatype);
int MPI_File_read_at_all_end(MPI_File, void*, MPI_Status*);
int MPI_File_write_at_all_begin(MPI_File, MPI_Offset, void*, int, MPI_Datatype);
int MPI_File_write_at_all_end(MPI_File, void*, MPI_Status*);
int MPI_File_read_all_begin(MPI_File, void*, int, MPI_Datatype);
int MPI_File_read_all_end(MPI_File, void*, MPI_Status*);
int MPI_File_write_all_begin(MPI_File, void*, int, MPI_Datatype);
int MPI_File_write_all_end(MPI_File, void*, MPI_Status*);
int MPI_File_read_ordered_begin(MPI_File, void*, int, MPI_Datatype);
int MPI_File_read_ordered_end(MPI_File, void*, MPI_Status*);
int MPI_File_write_ordered_begin(MPI_File, void*, int, MPI_Datatype);
int MPI_File_write_ordered_end(MPI_File, void*, MPI_Status*);
int MPI_File_get_type_extent(MPI_File, MPI_Datatype, MPI_Aint*);
int MPI_File_set_atomicity(MPI_File, int);
int MPI_File_get_atomicity(MPI_File, int*);
int MPI_File_sync(MPI_File);
typedef void (MPI_File_errhandler_fn)(MPI_File*,int*,...);
typedef void (MPI_File_errhandler_function)(MPI_File*,int*,...);
int MPI_File_create_errhandler(MPI_File_errhandler_function*, MPI_Errhandler*);
int MPI_File_get_errhandler(MPI_File, MPI_Errhandler*);
int MPI_File_set_errhandler(MPI_File, MPI_Errhandler);
int MPI_File_call_errhandler(MPI_File, int);
typedef int (MPI_Datarep_conversion_function)(void*,MPI_Datatype,int,void*,MPI_Offset,void*);
typedef int (MPI_Datarep_extent_function)(MPI_Datatype,MPI_Aint*,void*);
#define MPI_CONVERSION_FN_NULL ((MPI_Datarep_conversion_function*)0x0)
#define MPI_MAX_DATAREP_STRING 128
int MPI_Register_datarep(char[], MPI_Datarep_conversion_function*, MPI_Datarep_conversion_function*, MPI_Datarep_extent_function*, void*);
int MPI_File_read_at_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_read_at_all_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_write_at_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_write_at_all_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_iread_at_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iread_at_all_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_at_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_at_all_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_read_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_read_all_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_write_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_write_all_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_iread_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iread_all_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_all_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_read_shared_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_write_shared_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_iread_shared_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_iwrite_shared_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Request*);
int MPI_File_read_ordered_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_write_ordered_c(MPI_File, void*, MPI_Count, MPI_Datatype, MPI_Status*);
int MPI_File_read_at_all_begin_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype);
int MPI_File_write_at_all_begin_c(MPI_File, MPI_Offset, void*, MPI_Count, MPI_Datatype);
int MPI_File_read_all_begin_c(MPI_File, void*, MPI_Count, MPI_Datatype);
int MPI_File_write_all_begin_c(MPI_File, void*, MPI_Count, MPI_Datatype);
int MPI_File_read_ordered_begin_c(MPI_File, void*, MPI_Count, MPI_Datatype);
int MPI_File_write_ordered_begin_c(MPI_File, void*, MPI_Count, MPI_Datatype);
int MPI_File_get_type_extent_c(MPI_File, MPI_Datatype, MPI_Count*);
typedef int (MPI_Datarep_conversion_function_c)(void*,MPI_Datatype,MPI_Count,void*,MPI_Offset,void*);
#define MPI_CONVERSION_FN_NULL_C ((MPI_Datarep_conversion_function_c*)0x0)
int MPI_Register_datarep_c(char[], MPI_Datarep_conversion_function_c*, MPI_Datarep_conversion_function_c*, MPI_Datarep_extent_function*, void*);
#define MPI_MAX_ERROR_STRING 512
int MPI_Error_class(int, int*);
int MPI_Error_string(int, char[], int*);
int MPI_Add_error_class(int*);
int MPI_Remove_error_class(int);
int MPI_Add_error_code(int,int*);
int MPI_Remove_error_code(int);
int MPI_Add_error_string(int,char[]);
int MPI_Remove_error_string(int);
#define MPI_SUCCESS 0
#define MPI_ERR_LASTCODE 16383
#define MPI_ERR_ABI 62
#define MPI_ERR_TYPE 3
#define MPI_ERR_REQUEST 7
#define MPI_ERR_OP 10
#define MPI_ERR_GROUP 9
#define MPI_ERR_INFO 34
#define MPI_ERR_ERRHANDLER 61
#define MPI_ERR_SESSION 60
#define MPI_ERR_COMM 5
#define MPI_ERR_WIN 56
#define MPI_ERR_FILE 30
#define MPI_ERR_BUFFER 1
#define MPI_ERR_COUNT 2
#define MPI_ERR_TAG 4
#define MPI_ERR_RANK 6
#define MPI_ERR_ROOT 8
#define MPI_ERR_TRUNCATE 15
#define MPI_ERR_IN_STATUS 19
#define MPI_ERR_PENDING 18
#define MPI_ERR_TOPOLOGY 11
#define MPI_ERR_DIMS 12
#define MPI_ERR_ARG 13
#define MPI_ERR_OTHER 16
#define MPI_ERR_UNKNOWN 14
#define MPI_ERR_INTERN 17
#define MPI_ERR_KEYVAL 36
#define MPI_ERR_NO_MEM 39
#define MPI_ERR_INFO_KEY 31
#define MPI_ERR_INFO_VALUE 33
#define MPI_ERR_INFO_NOKEY 32
#define MPI_ERR_SPAWN 53
#define MPI_ERR_PORT 43
#define MPI_ERR_SERVICE 51
#define MPI_ERR_NAME 38
#define MPI_ERR_PROC_ABORTED 58
#define MPI_ERR_BASE 24
#define MPI_ERR_SIZE 52
#define MPI_ERR_DISP 26
#define MPI_ERR_ASSERT 22
#define MPI_ERR_LOCKTYPE 37
#define MPI_ERR_RMA_CONFLICT 47
#define MPI_ERR_RMA_SYNC 50
#define MPI_ERR_RMA_RANGE 48
#define MPI_ERR_RMA_ATTACH 46
#define MPI_ERR_RMA_SHARED 49
#define MPI_ERR_RMA_FLAVOR 57
#define MPI_ERR_BAD_FILE 23
#define MPI_ERR_NO_SUCH_FILE 42
#define MPI_ERR_FILE_EXISTS 28
#define MPI_ERR_FILE_IN_USE 29
#define MPI_ERR_AMODE 21
#define MPI_ERR_ACCESS 20
#define MPI_ERR_READ_ONLY 45
#define MPI_ERR_NO_SPACE 41
#define MPI_ERR_QUOTA 44
#define MPI_ERR_UNSUPPORTED_OPERATION 55
#define MPI_ERR_NOT_SAME 40
#define MPI_ERR_IO 35
#define MPI_ERR_UNSUPPORTED_DATAREP 54
#define MPI_ERR_CONVERSION 25
#define MPI_ERR_DUP_DATAREP 27
#define MPI_ERR_VALUE_TOO_LARGE 59
int MPI_Alloc_mem(MPI_Aint, MPI_Info, void*);
int MPI_Free_mem(void*);
int MPI_Init(int*, char**[]);
int MPI_Finalize(void);
int MPI_Initialized(int*);
int MPI_Finalized(int*);
#define MPI_THREAD_SINGLE 0
#define MPI_THREAD_FUNNELED 1024
#define MPI_THREAD_SERIALIZED 2048
#define MPI_THREAD_MULTIPLE 4096
int MPI_Init_thread(int*, char**[], int, int*);
int MPI_Query_thread(int*);
int MPI_Is_thread_main(int*);
#define MPI_VERSION 5
#define MPI_SUBVERSION 0
int MPI_Get_version(int*, int*);
#define MPI_MAX_LIBRARY_VERSION_STRING 8192
int MPI_Get_library_version(char[], int*);
#define MPI_ABI_VERSION 1
#define MPI_ABI_SUBVERSION 0
int MPI_Abi_get_version(int*, int*);
int MPI_Abi_get_info(MPI_Info*);
int MPI_Abi_get_fortran_info(MPI_Info*);
#define MPI_MAX_PROCESSOR_NAME 256
int MPI_Get_processor_name(char[], int*);
int MPI_Get_hw_resource_info(MPI_Info*);
double MPI_Wtime(void);
double MPI_Wtick(void);
int MPI_Pcontrol(int, ...);
#define MPI_F_SOURCE 0
#define MPI_F_TAG 1
#define MPI_F_ERROR 2
#define MPI_F_STATUS_SIZE 8
int MPI_Comm_toint(MPI_Comm);
int MPI_Errhandler_toint(MPI_Errhandler);
int MPI_File_toint(MPI_File);
int MPI_Group_toint(MPI_Group);
int MPI_Info_toint(MPI_Info);
int MPI_Message_toint(MPI_Message);
int MPI_Op_toint(MPI_Op);
int MPI_Request_toint(MPI_Request);
int MPI_Session_toint(MPI_Session);
int MPI_Type_toint(MPI_Datatype);
int MPI_Win_toint(MPI_Win);
MPI_Comm MPI_Comm_fromint(int);
MPI_Errhandler MPI_Errhandler_fromint(int);
MPI_File MPI_File_fromint(int);
MPI_Group MPI_Group_fromint(int);
MPI_Info MPI_Info_fromint(int);
MPI_Message MPI_Message_fromint(int);
MPI_Op MPI_Op_fromint(int);
MPI_Request MPI_Request_fromint(int);
MPI_Session MPI_Session_fromint(int);
MPI_Datatype MPI_Type_fromint(int);
MPI_Win MPI_Win_fromint(int);
#define MPI_HOST 503
int MPI_Info_get(MPI_Info, char[], int, char[], int*);
int MPI_Info_get_valuelen(MPI_Info, char[], int*, int*);
int MPI_Attr_get(MPI_Comm, int, void*, int*);
int MPI_Attr_put(MPI_Comm, int, void*);
int MPI_Attr_delete(MPI_Comm, int);
typedef int (MPI_Copy_function)(MPI_Comm,int,void*,void*,void*,int*);
typedef int (MPI_Delete_function)(MPI_Comm,int,void*,void*);
#define MPI_DUP_FN ((MPI_Copy_function*)0x1)
#define MPI_NULL_COPY_FN ((MPI_Copy_function*)0x0)
#define MPI_NULL_DELETE_FN ((MPI_Delete_function*)0x0)
int MPI_Keyval_create(MPI_Copy_function*, MPI_Delete_function*, int*, void*);
int MPI_Keyval_free(int*);
int MPI_Errhandler_get(MPI_Comm, MPI_Errhandler*);
int MPI_Errhandler_set(MPI_Comm, MPI_Errhandler);
typedef void (MPI_Handler_function)(MPI_Comm*,int*,...);
int MPI_Errhandler_create(MPI_Handler_function*, MPI_Errhandler*);
int MPI_Address(void*, MPI_Aint*);
int MPI_Type_lb(MPI_Datatype, MPI_Aint*);
int MPI_Type_ub(MPI_Datatype, MPI_Aint*);
int MPI_Type_extent(MPI_Datatype, MPI_Aint*);
int MPI_Type_hvector(int, int, MPI_Aint, MPI_Datatype, MPI_Datatype*);
int MPI_Type_hindexed(int, int[], MPI_Aint[], MPI_Datatype, MPI_Datatype*);
int MPI_Type_struct(int, int[], MPI_Aint[], MPI_Datatype[], MPI_Datatype*);
#if defined(__cplusplus)
}
#endif
#endif /* MPI_H_ABI */
