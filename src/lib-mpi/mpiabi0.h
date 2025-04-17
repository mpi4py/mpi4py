/* Generated with `python conf/mpiapigen.py` */

#define _pympi_CALL(fn, ...) \
PyMPI_WEAK_CALL(fn, __VA_ARGS__); \
return _pympi__##fn(__VA_ARGS__)

#ifdef OPEN_MPI
#include <mpi-ext.h>
PyMPI_WEAK_LOAD(ompi_mpi_datatype_null)
PyMPI_WEAK_LOAD(ompi_mpi_packed)
PyMPI_WEAK_LOAD(ompi_mpi_byte)
PyMPI_WEAK_LOAD(ompi_mpi_aint)
PyMPI_WEAK_LOAD(ompi_mpi_offset)
PyMPI_WEAK_LOAD(ompi_mpi_count)
PyMPI_WEAK_LOAD(ompi_mpi_char)
PyMPI_WEAK_LOAD(ompi_mpi_wchar)
PyMPI_WEAK_LOAD(ompi_mpi_signed_char)
PyMPI_WEAK_LOAD(ompi_mpi_short)
PyMPI_WEAK_LOAD(ompi_mpi_int)
PyMPI_WEAK_LOAD(ompi_mpi_long)
PyMPI_WEAK_LOAD(ompi_mpi_long_long_int)
PyMPI_WEAK_LOAD(ompi_mpi_unsigned_char)
PyMPI_WEAK_LOAD(ompi_mpi_unsigned_short)
PyMPI_WEAK_LOAD(ompi_mpi_unsigned)
PyMPI_WEAK_LOAD(ompi_mpi_unsigned_long)
PyMPI_WEAK_LOAD(ompi_mpi_unsigned_long_long)
PyMPI_WEAK_LOAD(ompi_mpi_float)
PyMPI_WEAK_LOAD(ompi_mpi_double)
PyMPI_WEAK_LOAD(ompi_mpi_long_double)
PyMPI_WEAK_LOAD(ompi_mpi_c_bool)
PyMPI_WEAK_LOAD(ompi_mpi_int8_t)
PyMPI_WEAK_LOAD(ompi_mpi_int16_t)
PyMPI_WEAK_LOAD(ompi_mpi_int32_t)
PyMPI_WEAK_LOAD(ompi_mpi_int64_t)
PyMPI_WEAK_LOAD(ompi_mpi_uint8_t)
PyMPI_WEAK_LOAD(ompi_mpi_uint16_t)
PyMPI_WEAK_LOAD(ompi_mpi_uint32_t)
PyMPI_WEAK_LOAD(ompi_mpi_uint64_t)
PyMPI_WEAK_LOAD(ompi_mpi_short_float)
PyMPI_WEAK_LOAD(ompi_mpi_c_float_complex)
PyMPI_WEAK_LOAD(ompi_mpi_c_double_complex)
PyMPI_WEAK_LOAD(ompi_mpi_c_long_double_complex)
PyMPI_WEAK_LOAD(ompi_mpi_cxx_bool)
PyMPI_WEAK_LOAD(ompi_mpi_cxx_cplex)
PyMPI_WEAK_LOAD(ompi_mpi_cxx_dblcplex)
PyMPI_WEAK_LOAD(ompi_mpi_cxx_ldblcplex)
PyMPI_WEAK_LOAD(ompi_mpi_short_int)
PyMPI_WEAK_LOAD(ompi_mpi_2int)
PyMPI_WEAK_LOAD(ompi_mpi_long_int)
PyMPI_WEAK_LOAD(ompi_mpi_float_int)
PyMPI_WEAK_LOAD(ompi_mpi_double_int)
PyMPI_WEAK_LOAD(ompi_mpi_longdbl_int)
PyMPI_WEAK_LOAD(ompi_mpi_character)
PyMPI_WEAK_LOAD(ompi_mpi_logical)
PyMPI_WEAK_LOAD(ompi_mpi_integer)
PyMPI_WEAK_LOAD(ompi_mpi_real)
PyMPI_WEAK_LOAD(ompi_mpi_dblprec)
PyMPI_WEAK_LOAD(ompi_mpi_cplex)
PyMPI_WEAK_LOAD(ompi_mpi_dblcplex)
PyMPI_WEAK_LOAD(ompi_mpi_logical1)
PyMPI_WEAK_LOAD(ompi_mpi_logical2)
PyMPI_WEAK_LOAD(ompi_mpi_logical4)
PyMPI_WEAK_LOAD(ompi_mpi_logical8)
PyMPI_WEAK_LOAD(ompi_mpi_logical16)
PyMPI_WEAK_LOAD(ompi_mpi_integer1)
PyMPI_WEAK_LOAD(ompi_mpi_integer2)
PyMPI_WEAK_LOAD(ompi_mpi_integer4)
PyMPI_WEAK_LOAD(ompi_mpi_integer8)
PyMPI_WEAK_LOAD(ompi_mpi_integer16)
PyMPI_WEAK_LOAD(ompi_mpi_real2)
PyMPI_WEAK_LOAD(ompi_mpi_real4)
PyMPI_WEAK_LOAD(ompi_mpi_real8)
PyMPI_WEAK_LOAD(ompi_mpi_real16)
PyMPI_WEAK_LOAD(ompi_mpi_complex4)
PyMPI_WEAK_LOAD(ompi_mpi_complex8)
PyMPI_WEAK_LOAD(ompi_mpi_complex16)
PyMPI_WEAK_LOAD(ompi_mpi_complex32)
PyMPI_WEAK_LOAD(ompi_request_null)
PyMPI_WEAK_LOAD(ompi_mpi_op_null)
PyMPI_WEAK_LOAD(ompi_mpi_op_max)
PyMPI_WEAK_LOAD(ompi_mpi_op_min)
PyMPI_WEAK_LOAD(ompi_mpi_op_sum)
PyMPI_WEAK_LOAD(ompi_mpi_op_prod)
PyMPI_WEAK_LOAD(ompi_mpi_op_land)
PyMPI_WEAK_LOAD(ompi_mpi_op_band)
PyMPI_WEAK_LOAD(ompi_mpi_op_lor)
PyMPI_WEAK_LOAD(ompi_mpi_op_bor)
PyMPI_WEAK_LOAD(ompi_mpi_op_lxor)
PyMPI_WEAK_LOAD(ompi_mpi_op_bxor)
PyMPI_WEAK_LOAD(ompi_mpi_op_maxloc)
PyMPI_WEAK_LOAD(ompi_mpi_op_minloc)
PyMPI_WEAK_LOAD(ompi_mpi_op_replace)
PyMPI_WEAK_LOAD(ompi_mpi_op_no_op)
PyMPI_WEAK_LOAD(ompi_mpi_group_null)
PyMPI_WEAK_LOAD(ompi_mpi_group_empty)
PyMPI_WEAK_LOAD(ompi_mpi_info_null)
PyMPI_WEAK_LOAD(ompi_mpi_info_env)
PyMPI_WEAK_LOAD(ompi_mpi_errhandler_null)
PyMPI_WEAK_LOAD(ompi_mpi_errors_return)
PyMPI_WEAK_LOAD(ompi_mpi_errors_abort)
PyMPI_WEAK_LOAD(ompi_mpi_errors_are_fatal)
PyMPI_WEAK_LOAD(ompi_mpi_instance_null)
PyMPI_WEAK_LOAD(ompi_mpi_comm_null)
PyMPI_WEAK_LOAD(ompi_mpi_comm_self)
PyMPI_WEAK_LOAD(ompi_mpi_comm_world)
PyMPI_WEAK_LOAD(ompi_message_null)
PyMPI_WEAK_LOAD(ompi_message_no_proc)
PyMPI_WEAK_LOAD(ompi_mpi_win_null)
PyMPI_WEAK_LOAD(ompi_mpi_file_null)
#endif /* OPEN_MPI */

#ifdef MPICH

#undef MPI_Type_create_f90_integer
#ifndef PyMPI_HAVE_MPI_Type_create_f90_integer
PyMPI_EXTERN int MPI_Type_create_f90_integer(int a0,MPI_Datatype* a1);
#endif
#define _pympi__MPI_Type_create_f90_integer(...) PyMPI_UNAVAILABLE("MPI_Type_create_f90_integer")
PyMPI_LOCAL int _pympi_MPI_Type_create_f90_integer(int a0,MPI_Datatype* a1) { _pympi_CALL(MPI_Type_create_f90_integer,a0,a1); }
#define MPI_Type_create_f90_integer _pympi_MPI_Type_create_f90_integer

#undef MPI_Type_create_f90_real
#ifndef PyMPI_HAVE_MPI_Type_create_f90_real
PyMPI_EXTERN int MPI_Type_create_f90_real(int a0,int a1,MPI_Datatype* a2);
#endif
#define _pympi__MPI_Type_create_f90_real(...) PyMPI_UNAVAILABLE("MPI_Type_create_f90_real")
PyMPI_LOCAL int _pympi_MPI_Type_create_f90_real(int a0,int a1,MPI_Datatype* a2) { _pympi_CALL(MPI_Type_create_f90_real,a0,a1,a2); }
#define MPI_Type_create_f90_real _pympi_MPI_Type_create_f90_real

#undef MPI_Type_create_f90_complex
#ifndef PyMPI_HAVE_MPI_Type_create_f90_complex
PyMPI_EXTERN int MPI_Type_create_f90_complex(int a0,int a1,MPI_Datatype* a2);
#endif
#define _pympi__MPI_Type_create_f90_complex(...) PyMPI_UNAVAILABLE("MPI_Type_create_f90_complex")
PyMPI_LOCAL int _pympi_MPI_Type_create_f90_complex(int a0,int a1,MPI_Datatype* a2) { _pympi_CALL(MPI_Type_create_f90_complex,a0,a1,a2); }
#define MPI_Type_create_f90_complex _pympi_MPI_Type_create_f90_complex

#endif /* MPICH */

#undef MPI_Status_c2f
PyMPI_EXTERN int MPI_Status_c2f(const MPI_Status* a0,MPI_Fint* a1);
static int _pympi__MPI_Status_c2f(const MPI_Status *c, MPI_Fint *f) { return (c && f) ? (*(MPI_Status *)(char *)f = *c), MPI_SUCCESS : MPI_ERR_ARG; }
PyMPI_LOCAL int _pympi_MPI_Status_c2f(const MPI_Status* a0,MPI_Fint* a1) { _pympi_CALL(MPI_Status_c2f,a0,a1); }
#define MPI_Status_c2f _pympi_MPI_Status_c2f

#undef MPI_Status_f2c
PyMPI_EXTERN int MPI_Status_f2c(const MPI_Fint* a0,MPI_Status* a1);
static int _pympi__MPI_Status_f2c(const MPI_Fint *f, MPI_Status *c) { return (c && f) ? (*c = *(MPI_Status *)(char *)f), MPI_SUCCESS : MPI_ERR_ARG; }
PyMPI_LOCAL int _pympi_MPI_Status_f2c(const MPI_Fint* a0,MPI_Status* a1) { _pympi_CALL(MPI_Status_f2c,a0,a1); }
#define MPI_Status_f2c _pympi_MPI_Status_f2c

#undef MPI_Type_c2f
PyMPI_EXTERN MPI_Fint MPI_Type_c2f(MPI_Datatype a0);
#ifdef MPICH
#define _pympi__MPI_Type_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Type_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Type_c2f(MPI_Datatype a0) { _pympi_CALL(MPI_Type_c2f,a0); }
#define MPI_Type_c2f _pympi_MPI_Type_c2f

#undef MPI_Request_c2f
PyMPI_EXTERN MPI_Fint MPI_Request_c2f(MPI_Request a0);
#ifdef MPICH
#define _pympi__MPI_Request_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Request_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Request_c2f(MPI_Request a0) { _pympi_CALL(MPI_Request_c2f,a0); }
#define MPI_Request_c2f _pympi_MPI_Request_c2f

#undef MPI_Message_c2f
PyMPI_EXTERN MPI_Fint MPI_Message_c2f(MPI_Message a0);
#ifdef MPICH
#define _pympi__MPI_Message_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Message_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Message_c2f(MPI_Message a0) { _pympi_CALL(MPI_Message_c2f,a0); }
#define MPI_Message_c2f _pympi_MPI_Message_c2f

#undef MPI_Op_c2f
PyMPI_EXTERN MPI_Fint MPI_Op_c2f(MPI_Op a0);
#ifdef MPICH
#define _pympi__MPI_Op_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Op_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Op_c2f(MPI_Op a0) { _pympi_CALL(MPI_Op_c2f,a0); }
#define MPI_Op_c2f _pympi_MPI_Op_c2f

#undef MPI_Group_c2f
PyMPI_EXTERN MPI_Fint MPI_Group_c2f(MPI_Group a0);
#ifdef MPICH
#define _pympi__MPI_Group_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Group_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Group_c2f(MPI_Group a0) { _pympi_CALL(MPI_Group_c2f,a0); }
#define MPI_Group_c2f _pympi_MPI_Group_c2f

#undef MPI_Info_c2f
PyMPI_EXTERN MPI_Fint MPI_Info_c2f(MPI_Info a0);
#ifdef MPICH
#define _pympi__MPI_Info_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Info_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Info_c2f(MPI_Info a0) { _pympi_CALL(MPI_Info_c2f,a0); }
#define MPI_Info_c2f _pympi_MPI_Info_c2f

#undef MPI_Session_c2f
PyMPI_EXTERN MPI_Fint MPI_Session_c2f(MPI_Session a0);
#ifdef MPICH
#define _pympi__MPI_Session_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Session_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Session_c2f(MPI_Session a0) { _pympi_CALL(MPI_Session_c2f,a0); }
#define MPI_Session_c2f _pympi_MPI_Session_c2f

#undef MPI_Comm_c2f
PyMPI_EXTERN MPI_Fint MPI_Comm_c2f(MPI_Comm a0);
#ifdef MPICH
#define _pympi__MPI_Comm_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Comm_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Comm_c2f(MPI_Comm a0) { _pympi_CALL(MPI_Comm_c2f,a0); }
#define MPI_Comm_c2f _pympi_MPI_Comm_c2f

#undef MPI_Win_c2f
PyMPI_EXTERN MPI_Fint MPI_Win_c2f(MPI_Win a0);
#ifdef MPICH
#define _pympi__MPI_Win_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Win_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Win_c2f(MPI_Win a0) { _pympi_CALL(MPI_Win_c2f,a0); }
#define MPI_Win_c2f _pympi_MPI_Win_c2f

#undef MPI_File_c2f
PyMPI_EXTERN MPI_Fint MPI_File_c2f(MPI_File a0);
#ifdef MPICH
#define _pympi__MPI_File_c2f(arg) ((MPI_Fint)-1)
#else
#define _pympi__MPI_File_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_File_c2f(MPI_File a0) { _pympi_CALL(MPI_File_c2f,a0); }
#define MPI_File_c2f _pympi_MPI_File_c2f

#undef MPI_Errhandler_c2f
PyMPI_EXTERN MPI_Fint MPI_Errhandler_c2f(MPI_Errhandler a0);
#ifdef MPICH
#define _pympi__MPI_Errhandler_c2f(arg) ((MPI_Fint)arg)
#else
#define _pympi__MPI_Errhandler_c2f(arg) ((MPI_Fint)-1)
#endif
PyMPI_LOCAL MPI_Fint _pympi_MPI_Errhandler_c2f(MPI_Errhandler a0) { _pympi_CALL(MPI_Errhandler_c2f,a0); }
#define MPI_Errhandler_c2f _pympi_MPI_Errhandler_c2f

#undef MPI_Type_f2c
PyMPI_EXTERN MPI_Datatype MPI_Type_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Type_f2c(arg) ((MPI_Datatype)arg)
#else
#define _pympi__MPI_Type_f2c(arg) ((MPI_Datatype)0)
#endif
PyMPI_LOCAL MPI_Datatype _pympi_MPI_Type_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Type_f2c,a0); }
#define MPI_Type_f2c _pympi_MPI_Type_f2c

#undef MPI_Request_f2c
PyMPI_EXTERN MPI_Request MPI_Request_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Request_f2c(arg) ((MPI_Request)arg)
#else
#define _pympi__MPI_Request_f2c(arg) ((MPI_Request)0)
#endif
PyMPI_LOCAL MPI_Request _pympi_MPI_Request_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Request_f2c,a0); }
#define MPI_Request_f2c _pympi_MPI_Request_f2c

#undef MPI_Message_f2c
PyMPI_EXTERN MPI_Message MPI_Message_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Message_f2c(arg) ((MPI_Message)arg)
#else
#define _pympi__MPI_Message_f2c(arg) ((MPI_Message)0)
#endif
PyMPI_LOCAL MPI_Message _pympi_MPI_Message_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Message_f2c,a0); }
#define MPI_Message_f2c _pympi_MPI_Message_f2c

#undef MPI_Op_f2c
PyMPI_EXTERN MPI_Op MPI_Op_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Op_f2c(arg) ((MPI_Op)arg)
#else
#define _pympi__MPI_Op_f2c(arg) ((MPI_Op)0)
#endif
PyMPI_LOCAL MPI_Op _pympi_MPI_Op_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Op_f2c,a0); }
#define MPI_Op_f2c _pympi_MPI_Op_f2c

#undef MPI_Group_f2c
PyMPI_EXTERN MPI_Group MPI_Group_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Group_f2c(arg) ((MPI_Group)arg)
#else
#define _pympi__MPI_Group_f2c(arg) ((MPI_Group)0)
#endif
PyMPI_LOCAL MPI_Group _pympi_MPI_Group_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Group_f2c,a0); }
#define MPI_Group_f2c _pympi_MPI_Group_f2c

#undef MPI_Info_f2c
PyMPI_EXTERN MPI_Info MPI_Info_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Info_f2c(arg) ((MPI_Info)arg)
#else
#define _pympi__MPI_Info_f2c(arg) ((MPI_Info)0)
#endif
PyMPI_LOCAL MPI_Info _pympi_MPI_Info_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Info_f2c,a0); }
#define MPI_Info_f2c _pympi_MPI_Info_f2c

#undef MPI_Session_f2c
PyMPI_EXTERN MPI_Session MPI_Session_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Session_f2c(arg) ((MPI_Session)arg)
#else
#define _pympi__MPI_Session_f2c(arg) ((MPI_Session)0)
#endif
PyMPI_LOCAL MPI_Session _pympi_MPI_Session_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Session_f2c,a0); }
#define MPI_Session_f2c _pympi_MPI_Session_f2c

#undef MPI_Comm_f2c
PyMPI_EXTERN MPI_Comm MPI_Comm_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Comm_f2c(arg) ((MPI_Comm)arg)
#else
#define _pympi__MPI_Comm_f2c(arg) ((MPI_Comm)0)
#endif
PyMPI_LOCAL MPI_Comm _pympi_MPI_Comm_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Comm_f2c,a0); }
#define MPI_Comm_f2c _pympi_MPI_Comm_f2c

#undef MPI_Win_f2c
PyMPI_EXTERN MPI_Win MPI_Win_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Win_f2c(arg) ((MPI_Win)arg)
#else
#define _pympi__MPI_Win_f2c(arg) ((MPI_Win)0)
#endif
PyMPI_LOCAL MPI_Win _pympi_MPI_Win_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Win_f2c,a0); }
#define MPI_Win_f2c _pympi_MPI_Win_f2c

#undef MPI_File_f2c
PyMPI_EXTERN MPI_File MPI_File_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_File_f2c(arg) ((MPI_File)0)
#else
#define _pympi__MPI_File_f2c(arg) ((MPI_File)0)
#endif
PyMPI_LOCAL MPI_File _pympi_MPI_File_f2c(MPI_Fint a0) { _pympi_CALL(MPI_File_f2c,a0); }
#define MPI_File_f2c _pympi_MPI_File_f2c

#undef MPI_Errhandler_f2c
PyMPI_EXTERN MPI_Errhandler MPI_Errhandler_f2c(MPI_Fint a0);
#ifdef MPICH
#define _pympi__MPI_Errhandler_f2c(arg) ((MPI_Errhandler)arg)
#else
#define _pympi__MPI_Errhandler_f2c(arg) ((MPI_Errhandler)0)
#endif
PyMPI_LOCAL MPI_Errhandler _pympi_MPI_Errhandler_f2c(MPI_Fint a0) { _pympi_CALL(MPI_Errhandler_f2c,a0); }
#define MPI_Errhandler_f2c _pympi_MPI_Errhandler_f2c

#undef MPI_Comm_toint
#ifndef PyMPI_HAVE_MPI_Comm_toint
PyMPI_EXTERN int MPI_Comm_toint(MPI_Comm a0);
#endif
#define _pympi__MPI_Comm_toint(arg) (int)MPI_Comm_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Comm_toint(MPI_Comm a0) { _pympi_CALL(MPI_Comm_toint,a0); }
#define MPI_Comm_toint _pympi_MPI_Comm_toint

#undef MPI_Errhandler_toint
#ifndef PyMPI_HAVE_MPI_Errhandler_toint
PyMPI_EXTERN int MPI_Errhandler_toint(MPI_Errhandler a0);
#endif
#define _pympi__MPI_Errhandler_toint(arg) (int)MPI_Errhandler_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Errhandler_toint(MPI_Errhandler a0) { _pympi_CALL(MPI_Errhandler_toint,a0); }
#define MPI_Errhandler_toint _pympi_MPI_Errhandler_toint

#undef MPI_File_toint
#ifndef PyMPI_HAVE_MPI_File_toint
PyMPI_EXTERN int MPI_File_toint(MPI_File a0);
#endif
#define _pympi__MPI_File_toint(arg) (int)MPI_File_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_File_toint(MPI_File a0) { _pympi_CALL(MPI_File_toint,a0); }
#define MPI_File_toint _pympi_MPI_File_toint

#undef MPI_Group_toint
#ifndef PyMPI_HAVE_MPI_Group_toint
PyMPI_EXTERN int MPI_Group_toint(MPI_Group a0);
#endif
#define _pympi__MPI_Group_toint(arg) (int)MPI_Group_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Group_toint(MPI_Group a0) { _pympi_CALL(MPI_Group_toint,a0); }
#define MPI_Group_toint _pympi_MPI_Group_toint

#undef MPI_Info_toint
#ifndef PyMPI_HAVE_MPI_Info_toint
PyMPI_EXTERN int MPI_Info_toint(MPI_Info a0);
#endif
#define _pympi__MPI_Info_toint(arg) (int)MPI_Info_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Info_toint(MPI_Info a0) { _pympi_CALL(MPI_Info_toint,a0); }
#define MPI_Info_toint _pympi_MPI_Info_toint

#undef MPI_Message_toint
#ifndef PyMPI_HAVE_MPI_Message_toint
PyMPI_EXTERN int MPI_Message_toint(MPI_Message a0);
#endif
#define _pympi__MPI_Message_toint(arg) (int)MPI_Message_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Message_toint(MPI_Message a0) { _pympi_CALL(MPI_Message_toint,a0); }
#define MPI_Message_toint _pympi_MPI_Message_toint

#undef MPI_Op_toint
#ifndef PyMPI_HAVE_MPI_Op_toint
PyMPI_EXTERN int MPI_Op_toint(MPI_Op a0);
#endif
#define _pympi__MPI_Op_toint(arg) (int)MPI_Op_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Op_toint(MPI_Op a0) { _pympi_CALL(MPI_Op_toint,a0); }
#define MPI_Op_toint _pympi_MPI_Op_toint

#undef MPI_Request_toint
#ifndef PyMPI_HAVE_MPI_Request_toint
PyMPI_EXTERN int MPI_Request_toint(MPI_Request a0);
#endif
#define _pympi__MPI_Request_toint(arg) (int)MPI_Request_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Request_toint(MPI_Request a0) { _pympi_CALL(MPI_Request_toint,a0); }
#define MPI_Request_toint _pympi_MPI_Request_toint

#undef MPI_Session_toint
#ifndef PyMPI_HAVE_MPI_Session_toint
PyMPI_EXTERN int MPI_Session_toint(MPI_Session a0);
#endif
#define _pympi__MPI_Session_toint(arg) (int)MPI_Session_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Session_toint(MPI_Session a0) { _pympi_CALL(MPI_Session_toint,a0); }
#define MPI_Session_toint _pympi_MPI_Session_toint

#undef MPI_Type_toint
#ifndef PyMPI_HAVE_MPI_Type_toint
PyMPI_EXTERN int MPI_Type_toint(MPI_Datatype a0);
#endif
#define _pympi__MPI_Type_toint(arg) (int)MPI_Type_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Type_toint(MPI_Datatype a0) { _pympi_CALL(MPI_Type_toint,a0); }
#define MPI_Type_toint _pympi_MPI_Type_toint

#undef MPI_Win_toint
#ifndef PyMPI_HAVE_MPI_Win_toint
PyMPI_EXTERN int MPI_Win_toint(MPI_Win a0);
#endif
#define _pympi__MPI_Win_toint(arg) (int)MPI_Win_c2f(arg)
PyMPI_LOCAL int _pympi_MPI_Win_toint(MPI_Win a0) { _pympi_CALL(MPI_Win_toint,a0); }
#define MPI_Win_toint _pympi_MPI_Win_toint

#undef MPI_Comm_fromint
#ifndef PyMPI_HAVE_MPI_Comm_fromint
PyMPI_EXTERN MPI_Comm MPI_Comm_fromint(int a0);
#endif
#define _pympi__MPI_Comm_fromint(arg) MPI_Comm_f2c((int)arg)
PyMPI_LOCAL MPI_Comm _pympi_MPI_Comm_fromint(int a0) { _pympi_CALL(MPI_Comm_fromint,a0); }
#define MPI_Comm_fromint _pympi_MPI_Comm_fromint

#undef MPI_Errhandler_fromint
#ifndef PyMPI_HAVE_MPI_Errhandler_fromint
PyMPI_EXTERN MPI_Errhandler MPI_Errhandler_fromint(int a0);
#endif
#define _pympi__MPI_Errhandler_fromint(arg) MPI_Errhandler_f2c((int)arg)
PyMPI_LOCAL MPI_Errhandler _pympi_MPI_Errhandler_fromint(int a0) { _pympi_CALL(MPI_Errhandler_fromint,a0); }
#define MPI_Errhandler_fromint _pympi_MPI_Errhandler_fromint

#undef MPI_File_fromint
#ifndef PyMPI_HAVE_MPI_File_fromint
PyMPI_EXTERN MPI_File MPI_File_fromint(int a0);
#endif
#define _pympi__MPI_File_fromint(arg) MPI_File_f2c((int)arg)
PyMPI_LOCAL MPI_File _pympi_MPI_File_fromint(int a0) { _pympi_CALL(MPI_File_fromint,a0); }
#define MPI_File_fromint _pympi_MPI_File_fromint

#undef MPI_Group_fromint
#ifndef PyMPI_HAVE_MPI_Group_fromint
PyMPI_EXTERN MPI_Group MPI_Group_fromint(int a0);
#endif
#define _pympi__MPI_Group_fromint(arg) MPI_Group_f2c((int)arg)
PyMPI_LOCAL MPI_Group _pympi_MPI_Group_fromint(int a0) { _pympi_CALL(MPI_Group_fromint,a0); }
#define MPI_Group_fromint _pympi_MPI_Group_fromint

#undef MPI_Info_fromint
#ifndef PyMPI_HAVE_MPI_Info_fromint
PyMPI_EXTERN MPI_Info MPI_Info_fromint(int a0);
#endif
#define _pympi__MPI_Info_fromint(arg) MPI_Info_f2c((int)arg)
PyMPI_LOCAL MPI_Info _pympi_MPI_Info_fromint(int a0) { _pympi_CALL(MPI_Info_fromint,a0); }
#define MPI_Info_fromint _pympi_MPI_Info_fromint

#undef MPI_Message_fromint
#ifndef PyMPI_HAVE_MPI_Message_fromint
PyMPI_EXTERN MPI_Message MPI_Message_fromint(int a0);
#endif
#define _pympi__MPI_Message_fromint(arg) MPI_Message_f2c((int)arg)
PyMPI_LOCAL MPI_Message _pympi_MPI_Message_fromint(int a0) { _pympi_CALL(MPI_Message_fromint,a0); }
#define MPI_Message_fromint _pympi_MPI_Message_fromint

#undef MPI_Op_fromint
#ifndef PyMPI_HAVE_MPI_Op_fromint
PyMPI_EXTERN MPI_Op MPI_Op_fromint(int a0);
#endif
#define _pympi__MPI_Op_fromint(arg) MPI_Op_f2c((int)arg)
PyMPI_LOCAL MPI_Op _pympi_MPI_Op_fromint(int a0) { _pympi_CALL(MPI_Op_fromint,a0); }
#define MPI_Op_fromint _pympi_MPI_Op_fromint

#undef MPI_Request_fromint
#ifndef PyMPI_HAVE_MPI_Request_fromint
PyMPI_EXTERN MPI_Request MPI_Request_fromint(int a0);
#endif
#define _pympi__MPI_Request_fromint(arg) MPI_Request_f2c((int)arg)
PyMPI_LOCAL MPI_Request _pympi_MPI_Request_fromint(int a0) { _pympi_CALL(MPI_Request_fromint,a0); }
#define MPI_Request_fromint _pympi_MPI_Request_fromint

#undef MPI_Session_fromint
#ifndef PyMPI_HAVE_MPI_Session_fromint
PyMPI_EXTERN MPI_Session MPI_Session_fromint(int a0);
#endif
#define _pympi__MPI_Session_fromint(arg) MPI_Session_f2c((int)arg)
PyMPI_LOCAL MPI_Session _pympi_MPI_Session_fromint(int a0) { _pympi_CALL(MPI_Session_fromint,a0); }
#define MPI_Session_fromint _pympi_MPI_Session_fromint

#undef MPI_Type_fromint
#ifndef PyMPI_HAVE_MPI_Type_fromint
PyMPI_EXTERN MPI_Datatype MPI_Type_fromint(int a0);
#endif
#define _pympi__MPI_Type_fromint(arg) MPI_Type_f2c((int)arg)
PyMPI_LOCAL MPI_Datatype _pympi_MPI_Type_fromint(int a0) { _pympi_CALL(MPI_Type_fromint,a0); }
#define MPI_Type_fromint _pympi_MPI_Type_fromint

#undef MPI_Win_fromint
#ifndef PyMPI_HAVE_MPI_Win_fromint
PyMPI_EXTERN MPI_Win MPI_Win_fromint(int a0);
#endif
#define _pympi__MPI_Win_fromint(arg) MPI_Win_f2c((int)arg)
PyMPI_LOCAL MPI_Win _pympi_MPI_Win_fromint(int a0) { _pympi_CALL(MPI_Win_fromint,a0); }
#define MPI_Win_fromint _pympi_MPI_Win_fromint

#ifdef MPI_Aint_add
static MPI_Aint _pympi__MPI_Aint_add(MPI_Aint a0,MPI_Aint a1) { return MPI_Aint_add(a0,a1); }
#else
static MPI_Aint _pympi__MPI_Aint_add(MPI_Aint a0,MPI_Aint a1) { return ((MPI_Aint)((char*)(a0)+(a1))); }
#endif
#undef MPI_Aint_add
PyMPI_EXTERN MPI_Aint MPI_Aint_add(MPI_Aint a0,MPI_Aint a1);
PyMPI_LOCAL MPI_Aint _pympi_MPI_Aint_add(MPI_Aint a0,MPI_Aint a1) { _pympi_CALL(MPI_Aint_add,a0,a1); }
#define MPI_Aint_add _pympi_MPI_Aint_add

#ifdef MPI_Aint_diff
static MPI_Aint _pympi__MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1) { return MPI_Aint_diff(a0,a1); }
#else
static MPI_Aint _pympi__MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1) { return ((MPI_Aint)((char*)(a0)-(char*)(a1))); }
#endif
#undef MPI_Aint_diff
PyMPI_EXTERN MPI_Aint MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1);
PyMPI_LOCAL MPI_Aint _pympi_MPI_Aint_diff(MPI_Aint a0,MPI_Aint a1) { _pympi_CALL(MPI_Aint_diff,a0,a1); }
#define MPI_Aint_diff _pympi_MPI_Aint_diff

#undef MPI_Type_get_value_index
#ifndef PyMPI_HAVE_MPI_Type_get_value_index
PyMPI_EXTERN int MPI_Type_get_value_index(MPI_Datatype a0,MPI_Datatype a1,MPI_Datatype* a2);
#endif

#undef MPI_Type_contiguous_c
#ifndef PyMPI_HAVE_MPI_Type_contiguous_c
PyMPI_EXTERN int MPI_Type_contiguous_c(MPI_Count a0,MPI_Datatype a1,MPI_Datatype* a2);
#endif

#undef MPI_Type_vector_c
#ifndef PyMPI_HAVE_MPI_Type_vector_c
PyMPI_EXTERN int MPI_Type_vector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4);
#endif

#undef MPI_Type_indexed_c
#ifndef PyMPI_HAVE_MPI_Type_indexed_c
PyMPI_EXTERN int MPI_Type_indexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif

#undef MPI_Type_create_indexed_block_c
#ifndef PyMPI_HAVE_MPI_Type_create_indexed_block_c
PyMPI_EXTERN int MPI_Type_create_indexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif

#undef MPI_Type_create_subarray_c
#ifndef PyMPI_HAVE_MPI_Type_create_subarray_c
PyMPI_EXTERN int MPI_Type_create_subarray_c(int a0,MPI_Count a1[],MPI_Count a2[],MPI_Count a3[],int a4,MPI_Datatype a5,MPI_Datatype* a6);
#endif

#undef MPI_Type_create_darray_c
#ifndef PyMPI_HAVE_MPI_Type_create_darray_c
PyMPI_EXTERN int MPI_Type_create_darray_c(int a0,int a1,int a2,MPI_Count a3[],int a4[],int a5[],int a6[],int a7,MPI_Datatype a8,MPI_Datatype* a9);
#endif

#undef MPI_Type_create_hvector_c
#ifndef PyMPI_HAVE_MPI_Type_create_hvector_c
PyMPI_EXTERN int MPI_Type_create_hvector_c(MPI_Count a0,MPI_Count a1,MPI_Count a2,MPI_Datatype a3,MPI_Datatype* a4);
#endif

#undef MPI_Type_create_hindexed_c
#ifndef PyMPI_HAVE_MPI_Type_create_hindexed_c
PyMPI_EXTERN int MPI_Type_create_hindexed_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif

#undef MPI_Type_create_hindexed_block_c
#ifndef PyMPI_HAVE_MPI_Type_create_hindexed_block_c
PyMPI_EXTERN int MPI_Type_create_hindexed_block_c(MPI_Count a0,MPI_Count a1,MPI_Count a2[],MPI_Datatype a3,MPI_Datatype* a4);
#endif

#undef MPI_Type_create_struct_c
#ifndef PyMPI_HAVE_MPI_Type_create_struct_c
PyMPI_EXTERN int MPI_Type_create_struct_c(MPI_Count a0,MPI_Count a1[],MPI_Count a2[],MPI_Datatype a3[],MPI_Datatype* a4);
#endif

#undef MPI_Type_create_resized_c
#ifndef PyMPI_HAVE_MPI_Type_create_resized_c
PyMPI_EXTERN int MPI_Type_create_resized_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Datatype* a3);
#endif

#undef MPI_Type_size_c
#ifndef PyMPI_HAVE_MPI_Type_size_c
PyMPI_EXTERN int MPI_Type_size_c(MPI_Datatype a0,MPI_Count* a1);
#endif

#undef MPI_Type_get_extent_c
#ifndef PyMPI_HAVE_MPI_Type_get_extent_c
PyMPI_EXTERN int MPI_Type_get_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2);
#endif

#undef MPI_Type_get_true_extent_c
#ifndef PyMPI_HAVE_MPI_Type_get_true_extent_c
PyMPI_EXTERN int MPI_Type_get_true_extent_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2);
#endif

#undef MPI_Type_get_envelope_c
#ifndef PyMPI_HAVE_MPI_Type_get_envelope_c
PyMPI_EXTERN int MPI_Type_get_envelope_c(MPI_Datatype a0,MPI_Count* a1,MPI_Count* a2,MPI_Count* a3,MPI_Count* a4,int* a5);
#endif

#undef MPI_Type_get_contents_c
#ifndef PyMPI_HAVE_MPI_Type_get_contents_c
PyMPI_EXTERN int MPI_Type_get_contents_c(MPI_Datatype a0,MPI_Count a1,MPI_Count a2,MPI_Count a3,MPI_Count a4,int a5[],MPI_Aint a6[],MPI_Count a7[],MPI_Datatype a8[]);
#endif

#undef MPI_Pack_c
#ifndef PyMPI_HAVE_MPI_Pack_c
PyMPI_EXTERN int MPI_Pack_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Count* a5,MPI_Comm a6);
#endif

#undef MPI_Unpack_c
#ifndef PyMPI_HAVE_MPI_Unpack_c
PyMPI_EXTERN int MPI_Unpack_c(void* a0,MPI_Count a1,MPI_Count* a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif

#undef MPI_Pack_size_c
#ifndef PyMPI_HAVE_MPI_Pack_size_c
PyMPI_EXTERN int MPI_Pack_size_c(MPI_Count a0,MPI_Datatype a1,MPI_Comm a2,MPI_Count* a3);
#endif

#undef MPI_Pack_external_c
#ifndef PyMPI_HAVE_MPI_Pack_external_c
PyMPI_EXTERN int MPI_Pack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Count* a6);
#endif

#undef MPI_Unpack_external_c
#ifndef PyMPI_HAVE_MPI_Unpack_external_c
PyMPI_EXTERN int MPI_Unpack_external_c(char a0[],void* a1,MPI_Count a2,MPI_Count* a3,void* a4,MPI_Count a5,MPI_Datatype a6);
#endif

#undef MPI_Pack_external_size_c
#ifndef PyMPI_HAVE_MPI_Pack_external_size_c
PyMPI_EXTERN int MPI_Pack_external_size_c(char a0[],MPI_Count a1,MPI_Datatype a2,MPI_Count* a3);
#endif

#undef MPI_Get_count_c
#ifndef PyMPI_HAVE_MPI_Get_count_c
PyMPI_EXTERN int MPI_Get_count_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2);
#endif

#undef MPI_Get_elements_c
#ifndef PyMPI_HAVE_MPI_Get_elements_c
PyMPI_EXTERN int MPI_Get_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count* a2);
#endif

#undef MPI_Status_set_elements_c
#ifndef PyMPI_HAVE_MPI_Status_set_elements_c
PyMPI_EXTERN int MPI_Status_set_elements_c(MPI_Status* a0,MPI_Datatype a1,MPI_Count a2);
#endif

#undef MPI_Status_get_source
#ifndef PyMPI_HAVE_MPI_Status_get_source
PyMPI_EXTERN int MPI_Status_get_source(MPI_Status* a0,int* a1);
#endif

#undef MPI_Status_set_source
#ifndef PyMPI_HAVE_MPI_Status_set_source
PyMPI_EXTERN int MPI_Status_set_source(MPI_Status* a0,int a1);
#endif

#undef MPI_Status_get_tag
#ifndef PyMPI_HAVE_MPI_Status_get_tag
PyMPI_EXTERN int MPI_Status_get_tag(MPI_Status* a0,int* a1);
#endif

#undef MPI_Status_set_tag
#ifndef PyMPI_HAVE_MPI_Status_set_tag
PyMPI_EXTERN int MPI_Status_set_tag(MPI_Status* a0,int a1);
#endif

#undef MPI_Status_get_error
#ifndef PyMPI_HAVE_MPI_Status_get_error
PyMPI_EXTERN int MPI_Status_get_error(MPI_Status* a0,int* a1);
#endif

#undef MPI_Status_set_error
#ifndef PyMPI_HAVE_MPI_Status_set_error
PyMPI_EXTERN int MPI_Status_set_error(MPI_Status* a0,int a1);
#endif

#undef MPI_Request_get_status_any
#ifndef PyMPI_HAVE_MPI_Request_get_status_any
PyMPI_EXTERN int MPI_Request_get_status_any(int a0,MPI_Request a1[],int* a2,int* a3,MPI_Status* a4);
#endif
#define _pympi__MPI_Request_get_status_any(...) PyMPI_UNAVAILABLE("MPI_Request_get_status_any")
PyMPI_LOCAL int _pympi_MPI_Request_get_status_any(int a0,MPI_Request a1[],int* a2,int* a3,MPI_Status* a4) { _pympi_CALL(MPI_Request_get_status_any,a0,a1,a2,a3,a4); }
#define MPI_Request_get_status_any _pympi_MPI_Request_get_status_any

#undef MPI_Request_get_status_all
#ifndef PyMPI_HAVE_MPI_Request_get_status_all
PyMPI_EXTERN int MPI_Request_get_status_all(int a0,MPI_Request  a1[],int* a2,MPI_Status a3[]);
#endif
#define _pympi__MPI_Request_get_status_all(...) PyMPI_UNAVAILABLE("MPI_Request_get_status_all")
PyMPI_LOCAL int _pympi_MPI_Request_get_status_all(int a0,MPI_Request  a1[],int* a2,MPI_Status a3[]) { _pympi_CALL(MPI_Request_get_status_all,a0,a1,a2,a3); }
#define MPI_Request_get_status_all _pympi_MPI_Request_get_status_all

#undef MPI_Request_get_status_some
#ifndef PyMPI_HAVE_MPI_Request_get_status_some
PyMPI_EXTERN int MPI_Request_get_status_some(int a0,MPI_Request a1[],int* a2,int a3[],MPI_Status a4[]);
#endif
#define _pympi__MPI_Request_get_status_some(...) PyMPI_UNAVAILABLE("MPI_Request_get_status_some")
PyMPI_LOCAL int _pympi_MPI_Request_get_status_some(int a0,MPI_Request a1[],int* a2,int a3[],MPI_Status a4[]) { _pympi_CALL(MPI_Request_get_status_some,a0,a1,a2,a3,a4); }
#define MPI_Request_get_status_some _pympi_MPI_Request_get_status_some

#undef MPI_Pready
#ifndef PyMPI_HAVE_MPI_Pready
PyMPI_EXTERN int MPI_Pready(int a0,MPI_Request a1);
#endif
#define _pympi__MPI_Pready(...) PyMPI_UNAVAILABLE("MPI_Pready")
PyMPI_LOCAL int _pympi_MPI_Pready(int a0,MPI_Request a1) { _pympi_CALL(MPI_Pready,a0,a1); }
#define MPI_Pready _pympi_MPI_Pready

#undef MPI_Pready_range
#ifndef PyMPI_HAVE_MPI_Pready_range
PyMPI_EXTERN int MPI_Pready_range(int a0,int a1,MPI_Request a2);
#endif
#define _pympi__MPI_Pready_range(...) PyMPI_UNAVAILABLE("MPI_Pready_range")
PyMPI_LOCAL int _pympi_MPI_Pready_range(int a0,int a1,MPI_Request a2) { _pympi_CALL(MPI_Pready_range,a0,a1,a2); }
#define MPI_Pready_range _pympi_MPI_Pready_range

#undef MPI_Pready_list
#ifndef PyMPI_HAVE_MPI_Pready_list
PyMPI_EXTERN int MPI_Pready_list(int a0,int a1[],MPI_Request a2);
#endif
#define _pympi__MPI_Pready_list(...) PyMPI_UNAVAILABLE("MPI_Pready_list")
PyMPI_LOCAL int _pympi_MPI_Pready_list(int a0,int a1[],MPI_Request a2) { _pympi_CALL(MPI_Pready_list,a0,a1,a2); }
#define MPI_Pready_list _pympi_MPI_Pready_list

#undef MPI_Parrived
#ifndef PyMPI_HAVE_MPI_Parrived
PyMPI_EXTERN int MPI_Parrived(MPI_Request a0,int a1,int* a2);
#endif
#define _pympi__MPI_Parrived(...) PyMPI_UNAVAILABLE("MPI_Parrived")
PyMPI_LOCAL int _pympi_MPI_Parrived(MPI_Request a0,int a1,int* a2) { _pympi_CALL(MPI_Parrived,a0,a1,a2); }
#define MPI_Parrived _pympi_MPI_Parrived

#undef MPI_Op_create_c
#ifndef PyMPI_HAVE_MPI_Op_create_c
PyMPI_EXTERN int MPI_Op_create_c(MPI_User_function_c* a0,int a1,MPI_Op* a2);
#endif
#define _pympi__MPI_Op_create_c(...) PyMPI_UNAVAILABLE("MPI_Op_create_c")
PyMPI_LOCAL int _pympi_MPI_Op_create_c(MPI_User_function_c* a0,int a1,MPI_Op* a2) { _pympi_CALL(MPI_Op_create_c,a0,a1,a2); }
#define MPI_Op_create_c _pympi_MPI_Op_create_c

#undef MPI_Info_create_env
#ifndef PyMPI_HAVE_MPI_Info_create_env
PyMPI_EXTERN int MPI_Info_create_env(int a0,char* a1[],MPI_Info* a2);
#endif
#define _pympi__MPI_Info_create_env(...) PyMPI_UNAVAILABLE("MPI_Info_create_env")
PyMPI_LOCAL int _pympi_MPI_Info_create_env(int a0,char* a1[],MPI_Info* a2) { _pympi_CALL(MPI_Info_create_env,a0,a1,a2); }
#define MPI_Info_create_env _pympi_MPI_Info_create_env

#undef MPI_Info_get_string
#ifndef PyMPI_HAVE_MPI_Info_get_string
PyMPI_EXTERN int MPI_Info_get_string(MPI_Info a0,char a1[],int* a2,char a3[],int* a4);
#endif

#undef MPI_Session_init
#ifndef PyMPI_HAVE_MPI_Session_init
PyMPI_EXTERN int MPI_Session_init(MPI_Info a0,MPI_Errhandler a1,MPI_Session* a2);
#endif
#define _pympi__MPI_Session_init(...) PyMPI_UNAVAILABLE("MPI_Session_init")
PyMPI_LOCAL int _pympi_MPI_Session_init(MPI_Info a0,MPI_Errhandler a1,MPI_Session* a2) { _pympi_CALL(MPI_Session_init,a0,a1,a2); }
#define MPI_Session_init _pympi_MPI_Session_init

#undef MPI_Session_finalize
#ifndef PyMPI_HAVE_MPI_Session_finalize
PyMPI_EXTERN int MPI_Session_finalize(MPI_Session* a0);
#endif
#define _pympi__MPI_Session_finalize(...) PyMPI_UNAVAILABLE("MPI_Session_finalize")
PyMPI_LOCAL int _pympi_MPI_Session_finalize(MPI_Session* a0) { _pympi_CALL(MPI_Session_finalize,a0); }
#define MPI_Session_finalize _pympi_MPI_Session_finalize

#undef MPI_Session_get_num_psets
#ifndef PyMPI_HAVE_MPI_Session_get_num_psets
PyMPI_EXTERN int MPI_Session_get_num_psets(MPI_Session a0,MPI_Info a1,int* a2);
#endif
#define _pympi__MPI_Session_get_num_psets(...) PyMPI_UNAVAILABLE("MPI_Session_get_num_psets")
PyMPI_LOCAL int _pympi_MPI_Session_get_num_psets(MPI_Session a0,MPI_Info a1,int* a2) { _pympi_CALL(MPI_Session_get_num_psets,a0,a1,a2); }
#define MPI_Session_get_num_psets _pympi_MPI_Session_get_num_psets

#undef MPI_Session_get_nth_pset
#ifndef PyMPI_HAVE_MPI_Session_get_nth_pset
PyMPI_EXTERN int MPI_Session_get_nth_pset(MPI_Session a0,MPI_Info a1,int a2,int* a3,char a4[]);
#endif
#define _pympi__MPI_Session_get_nth_pset(...) PyMPI_UNAVAILABLE("MPI_Session_get_nth_pset")
PyMPI_LOCAL int _pympi_MPI_Session_get_nth_pset(MPI_Session a0,MPI_Info a1,int a2,int* a3,char a4[]) { _pympi_CALL(MPI_Session_get_nth_pset,a0,a1,a2,a3,a4); }
#define MPI_Session_get_nth_pset _pympi_MPI_Session_get_nth_pset

#undef MPI_Session_get_info
#ifndef PyMPI_HAVE_MPI_Session_get_info
PyMPI_EXTERN int MPI_Session_get_info(MPI_Session a0,MPI_Info* a1);
#endif
#define _pympi__MPI_Session_get_info(...) PyMPI_UNAVAILABLE("MPI_Session_get_info")
PyMPI_LOCAL int _pympi_MPI_Session_get_info(MPI_Session a0,MPI_Info* a1) { _pympi_CALL(MPI_Session_get_info,a0,a1); }
#define MPI_Session_get_info _pympi_MPI_Session_get_info

#undef MPI_Session_get_pset_info
#ifndef PyMPI_HAVE_MPI_Session_get_pset_info
PyMPI_EXTERN int MPI_Session_get_pset_info(MPI_Session a0,char a1[],MPI_Info* a2);
#endif
#define _pympi__MPI_Session_get_pset_info(...) PyMPI_UNAVAILABLE("MPI_Session_get_pset_info")
PyMPI_LOCAL int _pympi_MPI_Session_get_pset_info(MPI_Session a0,char a1[],MPI_Info* a2) { _pympi_CALL(MPI_Session_get_pset_info,a0,a1,a2); }
#define MPI_Session_get_pset_info _pympi_MPI_Session_get_pset_info

#undef MPI_Group_from_session_pset
#ifndef PyMPI_HAVE_MPI_Group_from_session_pset
PyMPI_EXTERN int MPI_Group_from_session_pset(MPI_Session a0,char a1[],MPI_Group* a2);
#endif
#define _pympi__MPI_Group_from_session_pset(...) PyMPI_UNAVAILABLE("MPI_Group_from_session_pset")
PyMPI_LOCAL int _pympi_MPI_Group_from_session_pset(MPI_Session a0,char a1[],MPI_Group* a2) { _pympi_CALL(MPI_Group_from_session_pset,a0,a1,a2); }
#define MPI_Group_from_session_pset _pympi_MPI_Group_from_session_pset

#undef MPI_Session_create_errhandler
#ifndef PyMPI_HAVE_MPI_Session_create_errhandler
PyMPI_EXTERN int MPI_Session_create_errhandler(MPI_Session_errhandler_function* a0,MPI_Errhandler* a1);
#endif
#define _pympi__MPI_Session_create_errhandler(...) PyMPI_UNAVAILABLE("MPI_Session_create_errhandler")
PyMPI_LOCAL int _pympi_MPI_Session_create_errhandler(MPI_Session_errhandler_function* a0,MPI_Errhandler* a1) { _pympi_CALL(MPI_Session_create_errhandler,a0,a1); }
#define MPI_Session_create_errhandler _pympi_MPI_Session_create_errhandler

#undef MPI_Session_get_errhandler
#ifndef PyMPI_HAVE_MPI_Session_get_errhandler
PyMPI_EXTERN int MPI_Session_get_errhandler(MPI_Session a0,MPI_Errhandler* a1);
#endif
#define _pympi__MPI_Session_get_errhandler(...) PyMPI_UNAVAILABLE("MPI_Session_get_errhandler")
PyMPI_LOCAL int _pympi_MPI_Session_get_errhandler(MPI_Session a0,MPI_Errhandler* a1) { _pympi_CALL(MPI_Session_get_errhandler,a0,a1); }
#define MPI_Session_get_errhandler _pympi_MPI_Session_get_errhandler

#undef MPI_Session_set_errhandler
#ifndef PyMPI_HAVE_MPI_Session_set_errhandler
PyMPI_EXTERN int MPI_Session_set_errhandler(MPI_Session a0,MPI_Errhandler a1);
#endif
#define _pympi__MPI_Session_set_errhandler(...) PyMPI_UNAVAILABLE("MPI_Session_set_errhandler")
PyMPI_LOCAL int _pympi_MPI_Session_set_errhandler(MPI_Session a0,MPI_Errhandler a1) { _pympi_CALL(MPI_Session_set_errhandler,a0,a1); }
#define MPI_Session_set_errhandler _pympi_MPI_Session_set_errhandler

#undef MPI_Session_call_errhandler
#ifndef PyMPI_HAVE_MPI_Session_call_errhandler
PyMPI_EXTERN int MPI_Session_call_errhandler(MPI_Session a0,int a1);
#endif
#define _pympi__MPI_Session_call_errhandler(...) PyMPI_UNAVAILABLE("MPI_Session_call_errhandler")
PyMPI_LOCAL int _pympi_MPI_Session_call_errhandler(MPI_Session a0,int a1) { _pympi_CALL(MPI_Session_call_errhandler,a0,a1); }
#define MPI_Session_call_errhandler _pympi_MPI_Session_call_errhandler

#undef MPI_Buffer_flush
#ifndef PyMPI_HAVE_MPI_Buffer_flush
PyMPI_EXTERN int MPI_Buffer_flush(void);
#endif
#define _pympi__MPI_Buffer_flush(...) PyMPI_UNAVAILABLE("MPI_Buffer_flush")
PyMPI_LOCAL int _pympi_MPI_Buffer_flush(void) { _pympi_CALL(MPI_Buffer_flush,); }
#define MPI_Buffer_flush _pympi_MPI_Buffer_flush

#undef MPI_Buffer_iflush
#ifndef PyMPI_HAVE_MPI_Buffer_iflush
PyMPI_EXTERN int MPI_Buffer_iflush(MPI_Request* a0);
#endif
#define _pympi__MPI_Buffer_iflush(...) PyMPI_UNAVAILABLE("MPI_Buffer_iflush")
PyMPI_LOCAL int _pympi_MPI_Buffer_iflush(MPI_Request* a0) { _pympi_CALL(MPI_Buffer_iflush,a0); }
#define MPI_Buffer_iflush _pympi_MPI_Buffer_iflush

#undef MPI_Comm_attach_buffer
#ifndef PyMPI_HAVE_MPI_Comm_attach_buffer
PyMPI_EXTERN int MPI_Comm_attach_buffer(MPI_Comm a0,void* a1,int a2);
#endif
#define _pympi__MPI_Comm_attach_buffer(...) PyMPI_UNAVAILABLE("MPI_Comm_attach_buffer")
PyMPI_LOCAL int _pympi_MPI_Comm_attach_buffer(MPI_Comm a0,void* a1,int a2) { _pympi_CALL(MPI_Comm_attach_buffer,a0,a1,a2); }
#define MPI_Comm_attach_buffer _pympi_MPI_Comm_attach_buffer

#undef MPI_Comm_detach_buffer
#ifndef PyMPI_HAVE_MPI_Comm_detach_buffer
PyMPI_EXTERN int MPI_Comm_detach_buffer(MPI_Comm a0,void* a1,int* a2);
#endif
#define _pympi__MPI_Comm_detach_buffer(...) PyMPI_UNAVAILABLE("MPI_Comm_detach_buffer")
PyMPI_LOCAL int _pympi_MPI_Comm_detach_buffer(MPI_Comm a0,void* a1,int* a2) { _pympi_CALL(MPI_Comm_detach_buffer,a0,a1,a2); }
#define MPI_Comm_detach_buffer _pympi_MPI_Comm_detach_buffer

#undef MPI_Comm_flush_buffer
#ifndef PyMPI_HAVE_MPI_Comm_flush_buffer
PyMPI_EXTERN int MPI_Comm_flush_buffer(MPI_Comm a0);
#endif
#define _pympi__MPI_Comm_flush_buffer(...) PyMPI_UNAVAILABLE("MPI_Comm_flush_buffer")
PyMPI_LOCAL int _pympi_MPI_Comm_flush_buffer(MPI_Comm a0) { _pympi_CALL(MPI_Comm_flush_buffer,a0); }
#define MPI_Comm_flush_buffer _pympi_MPI_Comm_flush_buffer

#undef MPI_Comm_iflush_buffer
#ifndef PyMPI_HAVE_MPI_Comm_iflush_buffer
PyMPI_EXTERN int MPI_Comm_iflush_buffer(MPI_Comm a0,MPI_Request* a1);
#endif
#define _pympi__MPI_Comm_iflush_buffer(...) PyMPI_UNAVAILABLE("MPI_Comm_iflush_buffer")
PyMPI_LOCAL int _pympi_MPI_Comm_iflush_buffer(MPI_Comm a0,MPI_Request* a1) { _pympi_CALL(MPI_Comm_iflush_buffer,a0,a1); }
#define MPI_Comm_iflush_buffer _pympi_MPI_Comm_iflush_buffer

#undef MPI_Session_attach_buffer
#ifndef PyMPI_HAVE_MPI_Session_attach_buffer
PyMPI_EXTERN int MPI_Session_attach_buffer(MPI_Session a0,void* a1,int a2);
#endif
#define _pympi__MPI_Session_attach_buffer(...) PyMPI_UNAVAILABLE("MPI_Session_attach_buffer")
PyMPI_LOCAL int _pympi_MPI_Session_attach_buffer(MPI_Session a0,void* a1,int a2) { _pympi_CALL(MPI_Session_attach_buffer,a0,a1,a2); }
#define MPI_Session_attach_buffer _pympi_MPI_Session_attach_buffer

#undef MPI_Session_detach_buffer
#ifndef PyMPI_HAVE_MPI_Session_detach_buffer
PyMPI_EXTERN int MPI_Session_detach_buffer(MPI_Session a0,void* a1,int* a2);
#endif
#define _pympi__MPI_Session_detach_buffer(...) PyMPI_UNAVAILABLE("MPI_Session_detach_buffer")
PyMPI_LOCAL int _pympi_MPI_Session_detach_buffer(MPI_Session a0,void* a1,int* a2) { _pympi_CALL(MPI_Session_detach_buffer,a0,a1,a2); }
#define MPI_Session_detach_buffer _pympi_MPI_Session_detach_buffer

#undef MPI_Session_flush_buffer
#ifndef PyMPI_HAVE_MPI_Session_flush_buffer
PyMPI_EXTERN int MPI_Session_flush_buffer(MPI_Session a0);
#endif
#define _pympi__MPI_Session_flush_buffer(...) PyMPI_UNAVAILABLE("MPI_Session_flush_buffer")
PyMPI_LOCAL int _pympi_MPI_Session_flush_buffer(MPI_Session a0) { _pympi_CALL(MPI_Session_flush_buffer,a0); }
#define MPI_Session_flush_buffer _pympi_MPI_Session_flush_buffer

#undef MPI_Session_iflush_buffer
#ifndef PyMPI_HAVE_MPI_Session_iflush_buffer
PyMPI_EXTERN int MPI_Session_iflush_buffer(MPI_Session a0,MPI_Request* a1);
#endif
#define _pympi__MPI_Session_iflush_buffer(...) PyMPI_UNAVAILABLE("MPI_Session_iflush_buffer")
PyMPI_LOCAL int _pympi_MPI_Session_iflush_buffer(MPI_Session a0,MPI_Request* a1) { _pympi_CALL(MPI_Session_iflush_buffer,a0,a1); }
#define MPI_Session_iflush_buffer _pympi_MPI_Session_iflush_buffer

#undef MPI_Isendrecv
#ifndef PyMPI_HAVE_MPI_Isendrecv
PyMPI_EXTERN int MPI_Isendrecv(void* a0,int a1,MPI_Datatype a2,int a3,int a4,void* a5,int a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11);
#endif
#define _pympi__MPI_Isendrecv(...) PyMPI_UNAVAILABLE("MPI_Isendrecv")
PyMPI_LOCAL int _pympi_MPI_Isendrecv(void* a0,int a1,MPI_Datatype a2,int a3,int a4,void* a5,int a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11) { _pympi_CALL(MPI_Isendrecv,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11); }
#define MPI_Isendrecv _pympi_MPI_Isendrecv

#undef MPI_Isendrecv_replace
#ifndef PyMPI_HAVE_MPI_Isendrecv_replace
PyMPI_EXTERN int MPI_Isendrecv_replace(void* a0,int a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Isendrecv_replace(...) PyMPI_UNAVAILABLE("MPI_Isendrecv_replace")
PyMPI_LOCAL int _pympi_MPI_Isendrecv_replace(void* a0,int a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8) { _pympi_CALL(MPI_Isendrecv_replace,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Isendrecv_replace _pympi_MPI_Isendrecv_replace

#undef MPI_Psend_init
#ifndef PyMPI_HAVE_MPI_Psend_init
PyMPI_EXTERN int MPI_Psend_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Psend_init(...) PyMPI_UNAVAILABLE("MPI_Psend_init")
PyMPI_LOCAL int _pympi_MPI_Psend_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Psend_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Psend_init _pympi_MPI_Psend_init

#undef MPI_Precv_init
#ifndef PyMPI_HAVE_MPI_Precv_init
PyMPI_EXTERN int MPI_Precv_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Precv_init(...) PyMPI_UNAVAILABLE("MPI_Precv_init")
PyMPI_LOCAL int _pympi_MPI_Precv_init(void* a0,int a1,MPI_Count a2,MPI_Datatype a3,int a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Precv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Precv_init _pympi_MPI_Precv_init

#undef MPI_Barrier_init
#ifndef PyMPI_HAVE_MPI_Barrier_init
PyMPI_EXTERN int MPI_Barrier_init(MPI_Comm a0,MPI_Info a1,MPI_Request* a2);
#endif
#define _pympi__MPI_Barrier_init(...) PyMPI_UNAVAILABLE("MPI_Barrier_init")
PyMPI_LOCAL int _pympi_MPI_Barrier_init(MPI_Comm a0,MPI_Info a1,MPI_Request* a2) { _pympi_CALL(MPI_Barrier_init,a0,a1,a2); }
#define MPI_Barrier_init _pympi_MPI_Barrier_init

#undef MPI_Bcast_init
#ifndef PyMPI_HAVE_MPI_Bcast_init
PyMPI_EXTERN int MPI_Bcast_init(void* a0,int a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6);
#endif
#define _pympi__MPI_Bcast_init(...) PyMPI_UNAVAILABLE("MPI_Bcast_init")
PyMPI_LOCAL int _pympi_MPI_Bcast_init(void* a0,int a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6) { _pympi_CALL(MPI_Bcast_init,a0,a1,a2,a3,a4,a5,a6); }
#define MPI_Bcast_init _pympi_MPI_Bcast_init

#undef MPI_Gather_init
#ifndef PyMPI_HAVE_MPI_Gather_init
PyMPI_EXTERN int MPI_Gather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
#define _pympi__MPI_Gather_init(...) PyMPI_UNAVAILABLE("MPI_Gather_init")
PyMPI_LOCAL int _pympi_MPI_Gather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { _pympi_CALL(MPI_Gather_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Gather_init _pympi_MPI_Gather_init

#undef MPI_Gatherv_init
#ifndef PyMPI_HAVE_MPI_Gatherv_init
PyMPI_EXTERN int MPI_Gatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
#define _pympi__MPI_Gatherv_init(...) PyMPI_UNAVAILABLE("MPI_Gatherv_init")
PyMPI_LOCAL int _pympi_MPI_Gatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { _pympi_CALL(MPI_Gatherv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Gatherv_init _pympi_MPI_Gatherv_init

#undef MPI_Scatter_init
#ifndef PyMPI_HAVE_MPI_Scatter_init
PyMPI_EXTERN int MPI_Scatter_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
#define _pympi__MPI_Scatter_init(...) PyMPI_UNAVAILABLE("MPI_Scatter_init")
PyMPI_LOCAL int _pympi_MPI_Scatter_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { _pympi_CALL(MPI_Scatter_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Scatter_init _pympi_MPI_Scatter_init

#undef MPI_Scatterv_init
#ifndef PyMPI_HAVE_MPI_Scatterv_init
PyMPI_EXTERN int MPI_Scatterv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
#define _pympi__MPI_Scatterv_init(...) PyMPI_UNAVAILABLE("MPI_Scatterv_init")
PyMPI_LOCAL int _pympi_MPI_Scatterv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { _pympi_CALL(MPI_Scatterv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Scatterv_init _pympi_MPI_Scatterv_init

#undef MPI_Allgather_init
#ifndef PyMPI_HAVE_MPI_Allgather_init
PyMPI_EXTERN int MPI_Allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Allgather_init(...) PyMPI_UNAVAILABLE("MPI_Allgather_init")
PyMPI_LOCAL int _pympi_MPI_Allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Allgather_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Allgather_init _pympi_MPI_Allgather_init

#undef MPI_Allgatherv_init
#ifndef PyMPI_HAVE_MPI_Allgatherv_init
PyMPI_EXTERN int MPI_Allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
#define _pympi__MPI_Allgatherv_init(...) PyMPI_UNAVAILABLE("MPI_Allgatherv_init")
PyMPI_LOCAL int _pympi_MPI_Allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { _pympi_CALL(MPI_Allgatherv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Allgatherv_init _pympi_MPI_Allgatherv_init

#undef MPI_Alltoall_init
#ifndef PyMPI_HAVE_MPI_Alltoall_init
PyMPI_EXTERN int MPI_Alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Alltoall_init(...) PyMPI_UNAVAILABLE("MPI_Alltoall_init")
PyMPI_LOCAL int _pympi_MPI_Alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Alltoall_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Alltoall_init _pympi_MPI_Alltoall_init

#undef MPI_Alltoallv_init
#ifndef PyMPI_HAVE_MPI_Alltoallv_init
PyMPI_EXTERN int MPI_Alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
#define _pympi__MPI_Alltoallv_init(...) PyMPI_UNAVAILABLE("MPI_Alltoallv_init")
PyMPI_LOCAL int _pympi_MPI_Alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { _pympi_CALL(MPI_Alltoallv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Alltoallv_init _pympi_MPI_Alltoallv_init

#undef MPI_Alltoallw_init
#ifndef PyMPI_HAVE_MPI_Alltoallw_init
PyMPI_EXTERN int MPI_Alltoallw_init(void* a0,int a1[],int a2[],MPI_Datatype a3[],void* a4,int a5[],int a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
#define _pympi__MPI_Alltoallw_init(...) PyMPI_UNAVAILABLE("MPI_Alltoallw_init")
PyMPI_LOCAL int _pympi_MPI_Alltoallw_init(void* a0,int a1[],int a2[],MPI_Datatype a3[],void* a4,int a5[],int a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { _pympi_CALL(MPI_Alltoallw_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Alltoallw_init _pympi_MPI_Alltoallw_init

#undef MPI_Reduce_init
#ifndef PyMPI_HAVE_MPI_Reduce_init
PyMPI_EXTERN int MPI_Reduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Reduce_init(...) PyMPI_UNAVAILABLE("MPI_Reduce_init")
PyMPI_LOCAL int _pympi_MPI_Reduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Reduce_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Reduce_init _pympi_MPI_Reduce_init

#undef MPI_Allreduce_init
#ifndef PyMPI_HAVE_MPI_Allreduce_init
PyMPI_EXTERN int MPI_Allreduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
#define _pympi__MPI_Allreduce_init(...) PyMPI_UNAVAILABLE("MPI_Allreduce_init")
PyMPI_LOCAL int _pympi_MPI_Allreduce_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { _pympi_CALL(MPI_Allreduce_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Allreduce_init _pympi_MPI_Allreduce_init

#undef MPI_Reduce_scatter_block_init
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_block_init
PyMPI_EXTERN int MPI_Reduce_scatter_block_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
#define _pympi__MPI_Reduce_scatter_block_init(...) PyMPI_UNAVAILABLE("MPI_Reduce_scatter_block_init")
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_block_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { _pympi_CALL(MPI_Reduce_scatter_block_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Reduce_scatter_block_init _pympi_MPI_Reduce_scatter_block_init

#undef MPI_Reduce_scatter_init
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_init
PyMPI_EXTERN int MPI_Reduce_scatter_init(void* a0,void* a1,int a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
#define _pympi__MPI_Reduce_scatter_init(...) PyMPI_UNAVAILABLE("MPI_Reduce_scatter_init")
PyMPI_LOCAL int _pympi_MPI_Reduce_scatter_init(void* a0,void* a1,int a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { _pympi_CALL(MPI_Reduce_scatter_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Reduce_scatter_init _pympi_MPI_Reduce_scatter_init

#undef MPI_Scan_init
#ifndef PyMPI_HAVE_MPI_Scan_init
PyMPI_EXTERN int MPI_Scan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
#define _pympi__MPI_Scan_init(...) PyMPI_UNAVAILABLE("MPI_Scan_init")
PyMPI_LOCAL int _pympi_MPI_Scan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { _pympi_CALL(MPI_Scan_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Scan_init _pympi_MPI_Scan_init

#undef MPI_Exscan_init
#ifndef PyMPI_HAVE_MPI_Exscan_init
PyMPI_EXTERN int MPI_Exscan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif
#define _pympi__MPI_Exscan_init(...) PyMPI_UNAVAILABLE("MPI_Exscan_init")
PyMPI_LOCAL int _pympi_MPI_Exscan_init(void* a0,void* a1,int a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7) { _pympi_CALL(MPI_Exscan_init,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Exscan_init _pympi_MPI_Exscan_init

#undef MPI_Neighbor_allgather_init
#ifndef PyMPI_HAVE_MPI_Neighbor_allgather_init
PyMPI_EXTERN int MPI_Neighbor_allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Neighbor_allgather_init(...) PyMPI_UNAVAILABLE("MPI_Neighbor_allgather_init")
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgather_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Neighbor_allgather_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_allgather_init _pympi_MPI_Neighbor_allgather_init

#undef MPI_Neighbor_allgatherv_init
#ifndef PyMPI_HAVE_MPI_Neighbor_allgatherv_init
PyMPI_EXTERN int MPI_Neighbor_allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif
#define _pympi__MPI_Neighbor_allgatherv_init(...) PyMPI_UNAVAILABLE("MPI_Neighbor_allgatherv_init")
PyMPI_LOCAL int _pympi_MPI_Neighbor_allgatherv_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4[],int a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9) { _pympi_CALL(MPI_Neighbor_allgatherv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9); }
#define MPI_Neighbor_allgatherv_init _pympi_MPI_Neighbor_allgatherv_init

#undef MPI_Neighbor_alltoall_init
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoall_init
PyMPI_EXTERN int MPI_Neighbor_alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif
#define _pympi__MPI_Neighbor_alltoall_init(...) PyMPI_UNAVAILABLE("MPI_Neighbor_alltoall_init")
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoall_init(void* a0,int a1,MPI_Datatype a2,void* a3,int a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8) { _pympi_CALL(MPI_Neighbor_alltoall_init,a0,a1,a2,a3,a4,a5,a6,a7,a8); }
#define MPI_Neighbor_alltoall_init _pympi_MPI_Neighbor_alltoall_init

#undef MPI_Neighbor_alltoallv_init
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallv_init
PyMPI_EXTERN int MPI_Neighbor_alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
#define _pympi__MPI_Neighbor_alltoallv_init(...) PyMPI_UNAVAILABLE("MPI_Neighbor_alltoallv_init")
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallv_init(void* a0,int a1[],int a2[],MPI_Datatype a3,void* a4,int a5[],int a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { _pympi_CALL(MPI_Neighbor_alltoallv_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Neighbor_alltoallv_init _pympi_MPI_Neighbor_alltoallv_init

#undef MPI_Neighbor_alltoallw_init
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallw_init
PyMPI_EXTERN int MPI_Neighbor_alltoallw_init(void* a0,int a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,int a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif
#define _pympi__MPI_Neighbor_alltoallw_init(...) PyMPI_UNAVAILABLE("MPI_Neighbor_alltoallw_init")
PyMPI_LOCAL int _pympi_MPI_Neighbor_alltoallw_init(void* a0,int a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,int a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10) { _pympi_CALL(MPI_Neighbor_alltoallw_init,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10); }
#define MPI_Neighbor_alltoallw_init _pympi_MPI_Neighbor_alltoallw_init

#undef MPI_Comm_idup_with_info
#ifndef PyMPI_HAVE_MPI_Comm_idup_with_info
PyMPI_EXTERN int MPI_Comm_idup_with_info(MPI_Comm a0,MPI_Info a1,MPI_Comm* a2,MPI_Request* a3);
#endif

#undef MPI_Comm_create_from_group
#ifndef PyMPI_HAVE_MPI_Comm_create_from_group
PyMPI_EXTERN int MPI_Comm_create_from_group(MPI_Group a0,char a1[],MPI_Info a2,MPI_Errhandler a3,MPI_Comm* a4);
#endif
#define _pympi__MPI_Comm_create_from_group(...) PyMPI_UNAVAILABLE("MPI_Comm_create_from_group")
PyMPI_LOCAL int _pympi_MPI_Comm_create_from_group(MPI_Group a0,char a1[],MPI_Info a2,MPI_Errhandler a3,MPI_Comm* a4) { _pympi_CALL(MPI_Comm_create_from_group,a0,a1,a2,a3,a4); }
#define MPI_Comm_create_from_group _pympi_MPI_Comm_create_from_group

#undef MPI_Intercomm_create_from_groups
#ifndef PyMPI_HAVE_MPI_Intercomm_create_from_groups
PyMPI_EXTERN int MPI_Intercomm_create_from_groups(MPI_Group a0,int a1,MPI_Group a2,int a3,char a4[],MPI_Info a5,MPI_Errhandler a6,MPI_Comm* a7);
#endif
#define _pympi__MPI_Intercomm_create_from_groups(...) PyMPI_UNAVAILABLE("MPI_Intercomm_create_from_groups")
PyMPI_LOCAL int _pympi_MPI_Intercomm_create_from_groups(MPI_Group a0,int a1,MPI_Group a2,int a3,char a4[],MPI_Info a5,MPI_Errhandler a6,MPI_Comm* a7) { _pympi_CALL(MPI_Intercomm_create_from_groups,a0,a1,a2,a3,a4,a5,a6,a7); }
#define MPI_Intercomm_create_from_groups _pympi_MPI_Intercomm_create_from_groups

#undef MPI_Buffer_attach_c
#ifndef PyMPI_HAVE_MPI_Buffer_attach_c
PyMPI_EXTERN int MPI_Buffer_attach_c(void* a0,MPI_Count a1);
#endif

#undef MPI_Buffer_detach_c
#ifndef PyMPI_HAVE_MPI_Buffer_detach_c
PyMPI_EXTERN int MPI_Buffer_detach_c(void* a0,MPI_Count* a1);
#endif

#undef MPI_Comm_attach_buffer_c
#ifndef PyMPI_HAVE_MPI_Comm_attach_buffer_c
PyMPI_EXTERN int MPI_Comm_attach_buffer_c(MPI_Comm a0,void* a1,MPI_Count a2);
#endif

#undef MPI_Comm_detach_buffer_c
#ifndef PyMPI_HAVE_MPI_Comm_detach_buffer_c
PyMPI_EXTERN int MPI_Comm_detach_buffer_c(MPI_Comm a0,void* a1,MPI_Count* a2);
#endif

#undef MPI_Session_attach_buffer_c
#ifndef PyMPI_HAVE_MPI_Session_attach_buffer_c
PyMPI_EXTERN int MPI_Session_attach_buffer_c(MPI_Session a0,void* a1,MPI_Count a2);
#endif

#undef MPI_Session_detach_buffer_c
#ifndef PyMPI_HAVE_MPI_Session_detach_buffer_c
PyMPI_EXTERN int MPI_Session_detach_buffer_c(MPI_Session a0,void* a1,MPI_Count* a2);
#endif

#undef MPI_Send_c
#ifndef PyMPI_HAVE_MPI_Send_c
PyMPI_EXTERN int MPI_Send_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif

#undef MPI_Recv_c
#ifndef PyMPI_HAVE_MPI_Recv_c
PyMPI_EXTERN int MPI_Recv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Status* a6);
#endif

#undef MPI_Sendrecv_c
#ifndef PyMPI_HAVE_MPI_Sendrecv_c
PyMPI_EXTERN int MPI_Sendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Status* a11);
#endif

#undef MPI_Sendrecv_replace_c
#ifndef PyMPI_HAVE_MPI_Sendrecv_replace_c
PyMPI_EXTERN int MPI_Sendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Status* a8);
#endif

#undef MPI_Bsend_c
#ifndef PyMPI_HAVE_MPI_Bsend_c
PyMPI_EXTERN int MPI_Bsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif

#undef MPI_Ssend_c
#ifndef PyMPI_HAVE_MPI_Ssend_c
PyMPI_EXTERN int MPI_Ssend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif

#undef MPI_Rsend_c
#ifndef PyMPI_HAVE_MPI_Rsend_c
PyMPI_EXTERN int MPI_Rsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5);
#endif

#undef MPI_Isend_c
#ifndef PyMPI_HAVE_MPI_Isend_c
PyMPI_EXTERN int MPI_Isend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Irecv_c
#ifndef PyMPI_HAVE_MPI_Irecv_c
PyMPI_EXTERN int MPI_Irecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Isendrecv_c
#ifndef PyMPI_HAVE_MPI_Isendrecv_c
PyMPI_EXTERN int MPI_Isendrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,void* a5,MPI_Count a6,MPI_Datatype a7,int a8,int a9,MPI_Comm a10,MPI_Request* a11);
#endif

#undef MPI_Isendrecv_replace_c
#ifndef PyMPI_HAVE_MPI_Isendrecv_replace_c
PyMPI_EXTERN int MPI_Isendrecv_replace_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,int a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif

#undef MPI_Ibsend_c
#ifndef PyMPI_HAVE_MPI_Ibsend_c
PyMPI_EXTERN int MPI_Ibsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Issend_c
#ifndef PyMPI_HAVE_MPI_Issend_c
PyMPI_EXTERN int MPI_Issend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Irsend_c
#ifndef PyMPI_HAVE_MPI_Irsend_c
PyMPI_EXTERN int MPI_Irsend_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Send_init_c
#ifndef PyMPI_HAVE_MPI_Send_init_c
PyMPI_EXTERN int MPI_Send_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Recv_init_c
#ifndef PyMPI_HAVE_MPI_Recv_init_c
PyMPI_EXTERN int MPI_Recv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Bsend_init_c
#ifndef PyMPI_HAVE_MPI_Bsend_init_c
PyMPI_EXTERN int MPI_Bsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Ssend_init_c
#ifndef PyMPI_HAVE_MPI_Ssend_init_c
PyMPI_EXTERN int MPI_Ssend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Rsend_init_c
#ifndef PyMPI_HAVE_MPI_Rsend_init_c
PyMPI_EXTERN int MPI_Rsend_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,int a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Mrecv_c
#ifndef PyMPI_HAVE_MPI_Mrecv_c
PyMPI_EXTERN int MPI_Mrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Status* a4);
#endif

#undef MPI_Imrecv_c
#ifndef PyMPI_HAVE_MPI_Imrecv_c
PyMPI_EXTERN int MPI_Imrecv_c(void* a0,MPI_Count a1,MPI_Datatype a2,MPI_Message* a3,MPI_Request* a4);
#endif

#undef MPI_Bcast_c
#ifndef PyMPI_HAVE_MPI_Bcast_c
PyMPI_EXTERN int MPI_Bcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4);
#endif

#undef MPI_Gather_c
#ifndef PyMPI_HAVE_MPI_Gather_c
PyMPI_EXTERN int MPI_Gather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7);
#endif

#undef MPI_Gatherv_c
#ifndef PyMPI_HAVE_MPI_Gatherv_c
PyMPI_EXTERN int MPI_Gatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8);
#endif

#undef MPI_Scatter_c
#ifndef PyMPI_HAVE_MPI_Scatter_c
PyMPI_EXTERN int MPI_Scatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7);
#endif

#undef MPI_Scatterv_c
#ifndef PyMPI_HAVE_MPI_Scatterv_c
PyMPI_EXTERN int MPI_Scatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8);
#endif

#undef MPI_Allgather_c
#ifndef PyMPI_HAVE_MPI_Allgather_c
PyMPI_EXTERN int MPI_Allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif

#undef MPI_Allgatherv_c
#ifndef PyMPI_HAVE_MPI_Allgatherv_c
PyMPI_EXTERN int MPI_Allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7);
#endif

#undef MPI_Alltoall_c
#ifndef PyMPI_HAVE_MPI_Alltoall_c
PyMPI_EXTERN int MPI_Alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif

#undef MPI_Alltoallv_c
#ifndef PyMPI_HAVE_MPI_Alltoallv_c
PyMPI_EXTERN int MPI_Alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8);
#endif

#undef MPI_Alltoallw_c
#ifndef PyMPI_HAVE_MPI_Alltoallw_c
PyMPI_EXTERN int MPI_Alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8);
#endif

#undef MPI_Reduce_local_c
#ifndef PyMPI_HAVE_MPI_Reduce_local_c
PyMPI_EXTERN int MPI_Reduce_local_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4);
#endif

#undef MPI_Reduce_c
#ifndef PyMPI_HAVE_MPI_Reduce_c
PyMPI_EXTERN int MPI_Reduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6);
#endif

#undef MPI_Allreduce_c
#ifndef PyMPI_HAVE_MPI_Allreduce_c
PyMPI_EXTERN int MPI_Allreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif

#undef MPI_Reduce_scatter_block_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_block_c
PyMPI_EXTERN int MPI_Reduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif

#undef MPI_Reduce_scatter_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_c
PyMPI_EXTERN int MPI_Reduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif

#undef MPI_Scan_c
#ifndef PyMPI_HAVE_MPI_Scan_c
PyMPI_EXTERN int MPI_Scan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif

#undef MPI_Exscan_c
#ifndef PyMPI_HAVE_MPI_Exscan_c
PyMPI_EXTERN int MPI_Exscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5);
#endif

#undef MPI_Neighbor_allgather_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgather_c
PyMPI_EXTERN int MPI_Neighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif

#undef MPI_Neighbor_allgatherv_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgatherv_c
PyMPI_EXTERN int MPI_Neighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7);
#endif

#undef MPI_Neighbor_alltoall_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoall_c
PyMPI_EXTERN int MPI_Neighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6);
#endif

#undef MPI_Neighbor_alltoallv_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallv_c
PyMPI_EXTERN int MPI_Neighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8);
#endif

#undef MPI_Neighbor_alltoallw_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallw_c
PyMPI_EXTERN int MPI_Neighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8);
#endif

#undef MPI_Ibcast_c
#ifndef PyMPI_HAVE_MPI_Ibcast_c
PyMPI_EXTERN int MPI_Ibcast_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Request* a5);
#endif

#undef MPI_Igather_c
#ifndef PyMPI_HAVE_MPI_Igather_c
PyMPI_EXTERN int MPI_Igather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif

#undef MPI_Igatherv_c
#ifndef PyMPI_HAVE_MPI_Igatherv_c
PyMPI_EXTERN int MPI_Igatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9);
#endif

#undef MPI_Iscatter_c
#ifndef PyMPI_HAVE_MPI_Iscatter_c
PyMPI_EXTERN int MPI_Iscatter_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Request* a8);
#endif

#undef MPI_Iscatterv_c
#ifndef PyMPI_HAVE_MPI_Iscatterv_c
PyMPI_EXTERN int MPI_Iscatterv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Request* a9);
#endif

#undef MPI_Iallgather_c
#ifndef PyMPI_HAVE_MPI_Iallgather_c
PyMPI_EXTERN int MPI_Iallgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif

#undef MPI_Iallgatherv_c
#ifndef PyMPI_HAVE_MPI_Iallgatherv_c
PyMPI_EXTERN int MPI_Iallgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8);
#endif

#undef MPI_Ialltoall_c
#ifndef PyMPI_HAVE_MPI_Ialltoall_c
PyMPI_EXTERN int MPI_Ialltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif

#undef MPI_Ialltoallv_c
#ifndef PyMPI_HAVE_MPI_Ialltoallv_c
PyMPI_EXTERN int MPI_Ialltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9);
#endif

#undef MPI_Ialltoallw_c
#ifndef PyMPI_HAVE_MPI_Ialltoallw_c
PyMPI_EXTERN int MPI_Ialltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9);
#endif

#undef MPI_Ireduce_c
#ifndef PyMPI_HAVE_MPI_Ireduce_c
PyMPI_EXTERN int MPI_Ireduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Request* a7);
#endif

#undef MPI_Iallreduce_c
#ifndef PyMPI_HAVE_MPI_Iallreduce_c
PyMPI_EXTERN int MPI_Iallreduce_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Ireduce_scatter_block_c
#ifndef PyMPI_HAVE_MPI_Ireduce_scatter_block_c
PyMPI_EXTERN int MPI_Ireduce_scatter_block_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Ireduce_scatter_c
#ifndef PyMPI_HAVE_MPI_Ireduce_scatter_c
PyMPI_EXTERN int MPI_Ireduce_scatter_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Iscan_c
#ifndef PyMPI_HAVE_MPI_Iscan_c
PyMPI_EXTERN int MPI_Iscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Iexscan_c
#ifndef PyMPI_HAVE_MPI_Iexscan_c
PyMPI_EXTERN int MPI_Iexscan_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Request* a6);
#endif

#undef MPI_Ineighbor_allgather_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_allgather_c
PyMPI_EXTERN int MPI_Ineighbor_allgather_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif

#undef MPI_Ineighbor_allgatherv_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_allgatherv_c
PyMPI_EXTERN int MPI_Ineighbor_allgatherv_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Request* a8);
#endif

#undef MPI_Ineighbor_alltoall_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_alltoall_c
PyMPI_EXTERN int MPI_Ineighbor_alltoall_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Request* a7);
#endif

#undef MPI_Ineighbor_alltoallv_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_alltoallv_c
PyMPI_EXTERN int MPI_Ineighbor_alltoallv_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Request* a9);
#endif

#undef MPI_Ineighbor_alltoallw_c
#ifndef PyMPI_HAVE_MPI_Ineighbor_alltoallw_c
PyMPI_EXTERN int MPI_Ineighbor_alltoallw_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Request* a9);
#endif

#undef MPI_Bcast_init_c
#ifndef PyMPI_HAVE_MPI_Bcast_init_c
PyMPI_EXTERN int MPI_Bcast_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Comm a4,MPI_Info a5,MPI_Request* a6);
#endif

#undef MPI_Gather_init_c
#ifndef PyMPI_HAVE_MPI_Gather_init_c
PyMPI_EXTERN int MPI_Gather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif

#undef MPI_Gatherv_init_c
#ifndef PyMPI_HAVE_MPI_Gatherv_init_c
PyMPI_EXTERN int MPI_Gatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif

#undef MPI_Scatter_init_c
#ifndef PyMPI_HAVE_MPI_Scatter_init_c
PyMPI_EXTERN int MPI_Scatter_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif

#undef MPI_Scatterv_init_c
#ifndef PyMPI_HAVE_MPI_Scatterv_init_c
PyMPI_EXTERN int MPI_Scatterv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5,MPI_Datatype a6,int a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif

#undef MPI_Allgather_init_c
#ifndef PyMPI_HAVE_MPI_Allgather_init_c
PyMPI_EXTERN int MPI_Allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif

#undef MPI_Allgatherv_init_c
#ifndef PyMPI_HAVE_MPI_Allgatherv_init_c
PyMPI_EXTERN int MPI_Allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif

#undef MPI_Alltoall_init_c
#ifndef PyMPI_HAVE_MPI_Alltoall_init_c
PyMPI_EXTERN int MPI_Alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif

#undef MPI_Alltoallv_init_c
#ifndef PyMPI_HAVE_MPI_Alltoallv_init_c
PyMPI_EXTERN int MPI_Alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif

#undef MPI_Alltoallw_init_c
#ifndef PyMPI_HAVE_MPI_Alltoallw_init_c
PyMPI_EXTERN int MPI_Alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif

#undef MPI_Reduce_init_c
#ifndef PyMPI_HAVE_MPI_Reduce_init_c
PyMPI_EXTERN int MPI_Reduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,int a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif

#undef MPI_Allreduce_init_c
#ifndef PyMPI_HAVE_MPI_Allreduce_init_c
PyMPI_EXTERN int MPI_Allreduce_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif

#undef MPI_Reduce_scatter_block_init_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_block_init_c
PyMPI_EXTERN int MPI_Reduce_scatter_block_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif

#undef MPI_Reduce_scatter_init_c
#ifndef PyMPI_HAVE_MPI_Reduce_scatter_init_c
PyMPI_EXTERN int MPI_Reduce_scatter_init_c(void* a0,void* a1,MPI_Count a2[],MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif

#undef MPI_Scan_init_c
#ifndef PyMPI_HAVE_MPI_Scan_init_c
PyMPI_EXTERN int MPI_Scan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif

#undef MPI_Exscan_init_c
#ifndef PyMPI_HAVE_MPI_Exscan_init_c
PyMPI_EXTERN int MPI_Exscan_init_c(void* a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Op a4,MPI_Comm a5,MPI_Info a6,MPI_Request* a7);
#endif

#undef MPI_Neighbor_allgather_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgather_init_c
PyMPI_EXTERN int MPI_Neighbor_allgather_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif

#undef MPI_Neighbor_allgatherv_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_allgatherv_init_c
PyMPI_EXTERN int MPI_Neighbor_allgatherv_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4[],MPI_Aint a5[],MPI_Datatype a6,MPI_Comm a7,MPI_Info a8,MPI_Request* a9);
#endif

#undef MPI_Neighbor_alltoall_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoall_init_c
PyMPI_EXTERN int MPI_Neighbor_alltoall_init_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,MPI_Comm a6,MPI_Info a7,MPI_Request* a8);
#endif

#undef MPI_Neighbor_alltoallv_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallv_init_c
PyMPI_EXTERN int MPI_Neighbor_alltoallv_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3,void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7,MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif

#undef MPI_Neighbor_alltoallw_init_c
#ifndef PyMPI_HAVE_MPI_Neighbor_alltoallw_init_c
PyMPI_EXTERN int MPI_Neighbor_alltoallw_init_c(void* a0,MPI_Count a1[],MPI_Aint a2[],MPI_Datatype a3[],void* a4,MPI_Count a5[],MPI_Aint a6[],MPI_Datatype a7[],MPI_Comm a8,MPI_Info a9,MPI_Request* a10);
#endif

#undef MPI_Win_create_c
#ifndef PyMPI_HAVE_MPI_Win_create_c
PyMPI_EXTERN int MPI_Win_create_c(void* a0,MPI_Aint a1,MPI_Aint a2,MPI_Info a3,MPI_Comm a4,MPI_Win* a5);
#endif

#undef MPI_Win_allocate_c
#ifndef PyMPI_HAVE_MPI_Win_allocate_c
PyMPI_EXTERN int MPI_Win_allocate_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5);
#endif

#undef MPI_Win_allocate_shared_c
#ifndef PyMPI_HAVE_MPI_Win_allocate_shared_c
PyMPI_EXTERN int MPI_Win_allocate_shared_c(MPI_Aint a0,MPI_Aint a1,MPI_Info a2,MPI_Comm a3,void* a4,MPI_Win* a5);
#endif

#undef MPI_Win_shared_query_c
#ifndef PyMPI_HAVE_MPI_Win_shared_query_c
PyMPI_EXTERN int MPI_Win_shared_query_c(MPI_Win a0,int a1,MPI_Aint* a2,MPI_Aint* a3,void* a4);
#endif

#undef MPI_Get_c
#ifndef PyMPI_HAVE_MPI_Get_c
PyMPI_EXTERN int MPI_Get_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7);
#endif

#undef MPI_Put_c
#ifndef PyMPI_HAVE_MPI_Put_c
PyMPI_EXTERN int MPI_Put_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7);
#endif

#undef MPI_Accumulate_c
#ifndef PyMPI_HAVE_MPI_Accumulate_c
PyMPI_EXTERN int MPI_Accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8);
#endif

#undef MPI_Get_accumulate_c
#ifndef PyMPI_HAVE_MPI_Get_accumulate_c
PyMPI_EXTERN int MPI_Get_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11);
#endif

#undef MPI_Rget_c
#ifndef PyMPI_HAVE_MPI_Rget_c
PyMPI_EXTERN int MPI_Rget_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8);
#endif

#undef MPI_Rput_c
#ifndef PyMPI_HAVE_MPI_Rput_c
PyMPI_EXTERN int MPI_Rput_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Win a7,MPI_Request* a8);
#endif

#undef MPI_Raccumulate_c
#ifndef PyMPI_HAVE_MPI_Raccumulate_c
PyMPI_EXTERN int MPI_Raccumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,int a3,MPI_Aint a4,MPI_Count a5,MPI_Datatype a6,MPI_Op a7,MPI_Win a8,MPI_Request* a9);
#endif

#undef MPI_Rget_accumulate_c
#ifndef PyMPI_HAVE_MPI_Rget_accumulate_c
PyMPI_EXTERN int MPI_Rget_accumulate_c(void* a0,MPI_Count a1,MPI_Datatype a2,void* a3,MPI_Count a4,MPI_Datatype a5,int a6,MPI_Aint a7,MPI_Count a8,MPI_Datatype a9,MPI_Op a10,MPI_Win a11,MPI_Request* a12);
#endif

#undef MPI_File_iread_at_all
#ifndef PyMPI_HAVE_MPI_File_iread_at_all
PyMPI_EXTERN int MPI_File_iread_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5);
#endif
#define _pympi__MPI_File_iread_at_all(...) PyMPI_UNAVAILABLE("MPI_File_iread_at_all")
PyMPI_LOCAL int _pympi_MPI_File_iread_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5) { _pympi_CALL(MPI_File_iread_at_all,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iread_at_all _pympi_MPI_File_iread_at_all

#undef MPI_File_iwrite_at_all
#ifndef PyMPI_HAVE_MPI_File_iwrite_at_all
PyMPI_EXTERN int MPI_File_iwrite_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5);
#endif
#define _pympi__MPI_File_iwrite_at_all(...) PyMPI_UNAVAILABLE("MPI_File_iwrite_at_all")
PyMPI_LOCAL int _pympi_MPI_File_iwrite_at_all(MPI_File a0,MPI_Offset a1,void* a2,int a3,MPI_Datatype a4,MPI_Request* a5) { _pympi_CALL(MPI_File_iwrite_at_all,a0,a1,a2,a3,a4,a5); }
#define MPI_File_iwrite_at_all _pympi_MPI_File_iwrite_at_all

#undef MPI_File_iread_all
#ifndef PyMPI_HAVE_MPI_File_iread_all
PyMPI_EXTERN int MPI_File_iread_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4);
#endif
#define _pympi__MPI_File_iread_all(...) PyMPI_UNAVAILABLE("MPI_File_iread_all")
PyMPI_LOCAL int _pympi_MPI_File_iread_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4) { _pympi_CALL(MPI_File_iread_all,a0,a1,a2,a3,a4); }
#define MPI_File_iread_all _pympi_MPI_File_iread_all

#undef MPI_File_iwrite_all
#ifndef PyMPI_HAVE_MPI_File_iwrite_all
PyMPI_EXTERN int MPI_File_iwrite_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4);
#endif
#define _pympi__MPI_File_iwrite_all(...) PyMPI_UNAVAILABLE("MPI_File_iwrite_all")
PyMPI_LOCAL int _pympi_MPI_File_iwrite_all(MPI_File a0,void* a1,int a2,MPI_Datatype a3,MPI_Request* a4) { _pympi_CALL(MPI_File_iwrite_all,a0,a1,a2,a3,a4); }
#define MPI_File_iwrite_all _pympi_MPI_File_iwrite_all

#undef MPI_File_read_at_c
#ifndef PyMPI_HAVE_MPI_File_read_at_c
PyMPI_EXTERN int MPI_File_read_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif

#undef MPI_File_read_at_all_c
#ifndef PyMPI_HAVE_MPI_File_read_at_all_c
PyMPI_EXTERN int MPI_File_read_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif

#undef MPI_File_write_at_c
#ifndef PyMPI_HAVE_MPI_File_write_at_c
PyMPI_EXTERN int MPI_File_write_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif

#undef MPI_File_write_at_all_c
#ifndef PyMPI_HAVE_MPI_File_write_at_all_c
PyMPI_EXTERN int MPI_File_write_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Status* a5);
#endif

#undef MPI_File_iread_at_c
#ifndef PyMPI_HAVE_MPI_File_iread_at_c
PyMPI_EXTERN int MPI_File_iread_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif

#undef MPI_File_iread_at_all_c
#ifndef PyMPI_HAVE_MPI_File_iread_at_all_c
PyMPI_EXTERN int MPI_File_iread_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif

#undef MPI_File_iwrite_at_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_at_c
PyMPI_EXTERN int MPI_File_iwrite_at_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif

#undef MPI_File_iwrite_at_all_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_at_all_c
PyMPI_EXTERN int MPI_File_iwrite_at_all_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4,MPI_Request* a5);
#endif

#undef MPI_File_read_c
#ifndef PyMPI_HAVE_MPI_File_read_c
PyMPI_EXTERN int MPI_File_read_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_read_all_c
#ifndef PyMPI_HAVE_MPI_File_read_all_c
PyMPI_EXTERN int MPI_File_read_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_write_c
#ifndef PyMPI_HAVE_MPI_File_write_c
PyMPI_EXTERN int MPI_File_write_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_write_all_c
#ifndef PyMPI_HAVE_MPI_File_write_all_c
PyMPI_EXTERN int MPI_File_write_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_iread_c
#ifndef PyMPI_HAVE_MPI_File_iread_c
PyMPI_EXTERN int MPI_File_iread_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif

#undef MPI_File_iread_all_c
#ifndef PyMPI_HAVE_MPI_File_iread_all_c
PyMPI_EXTERN int MPI_File_iread_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif

#undef MPI_File_iwrite_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_c
PyMPI_EXTERN int MPI_File_iwrite_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif

#undef MPI_File_iwrite_all_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_all_c
PyMPI_EXTERN int MPI_File_iwrite_all_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif

#undef MPI_File_read_shared_c
#ifndef PyMPI_HAVE_MPI_File_read_shared_c
PyMPI_EXTERN int MPI_File_read_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_write_shared_c
#ifndef PyMPI_HAVE_MPI_File_write_shared_c
PyMPI_EXTERN int MPI_File_write_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_iread_shared_c
#ifndef PyMPI_HAVE_MPI_File_iread_shared_c
PyMPI_EXTERN int MPI_File_iread_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif

#undef MPI_File_iwrite_shared_c
#ifndef PyMPI_HAVE_MPI_File_iwrite_shared_c
PyMPI_EXTERN int MPI_File_iwrite_shared_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Request* a4);
#endif

#undef MPI_File_read_ordered_c
#ifndef PyMPI_HAVE_MPI_File_read_ordered_c
PyMPI_EXTERN int MPI_File_read_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_write_ordered_c
#ifndef PyMPI_HAVE_MPI_File_write_ordered_c
PyMPI_EXTERN int MPI_File_write_ordered_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3,MPI_Status* a4);
#endif

#undef MPI_File_read_at_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_read_at_all_begin_c
PyMPI_EXTERN int MPI_File_read_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4);
#endif

#undef MPI_File_write_at_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_write_at_all_begin_c
PyMPI_EXTERN int MPI_File_write_at_all_begin_c(MPI_File a0,MPI_Offset a1,void* a2,MPI_Count a3,MPI_Datatype a4);
#endif

#undef MPI_File_read_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_read_all_begin_c
PyMPI_EXTERN int MPI_File_read_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif

#undef MPI_File_write_all_begin_c
#ifndef PyMPI_HAVE_MPI_File_write_all_begin_c
PyMPI_EXTERN int MPI_File_write_all_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif

#undef MPI_File_read_ordered_begin_c
#ifndef PyMPI_HAVE_MPI_File_read_ordered_begin_c
PyMPI_EXTERN int MPI_File_read_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif

#undef MPI_File_write_ordered_begin_c
#ifndef PyMPI_HAVE_MPI_File_write_ordered_begin_c
PyMPI_EXTERN int MPI_File_write_ordered_begin_c(MPI_File a0,void* a1,MPI_Count a2,MPI_Datatype a3);
#endif

#undef MPI_File_get_type_extent_c
#ifndef PyMPI_HAVE_MPI_File_get_type_extent_c
PyMPI_EXTERN int MPI_File_get_type_extent_c(MPI_File a0,MPI_Datatype a1,MPI_Count* a2);
#endif

#undef MPI_Register_datarep_c
#ifndef PyMPI_HAVE_MPI_Register_datarep_c
PyMPI_EXTERN int MPI_Register_datarep_c(char a0[],MPI_Datarep_conversion_function_c* a1,MPI_Datarep_conversion_function_c* a2,MPI_Datarep_extent_function* a3,void* a4);
#endif

#undef MPI_Remove_error_class
#ifndef PyMPI_HAVE_MPI_Remove_error_class
PyMPI_EXTERN int MPI_Remove_error_class(int a0);
#endif
#define _pympi__MPI_Remove_error_class(...) PyMPI_UNAVAILABLE("MPI_Remove_error_class")
PyMPI_LOCAL int _pympi_MPI_Remove_error_class(int a0) { _pympi_CALL(MPI_Remove_error_class,a0); }
#define MPI_Remove_error_class _pympi_MPI_Remove_error_class

#undef MPI_Remove_error_code
#ifndef PyMPI_HAVE_MPI_Remove_error_code
PyMPI_EXTERN int MPI_Remove_error_code(int a0);
#endif
#define _pympi__MPI_Remove_error_code(...) PyMPI_UNAVAILABLE("MPI_Remove_error_code")
PyMPI_LOCAL int _pympi_MPI_Remove_error_code(int a0) { _pympi_CALL(MPI_Remove_error_code,a0); }
#define MPI_Remove_error_code _pympi_MPI_Remove_error_code

#undef MPI_Remove_error_string
#ifndef PyMPI_HAVE_MPI_Remove_error_string
PyMPI_EXTERN int MPI_Remove_error_string(int a0);
#endif
#define _pympi__MPI_Remove_error_string(...) PyMPI_UNAVAILABLE("MPI_Remove_error_string")
PyMPI_LOCAL int _pympi_MPI_Remove_error_string(int a0) { _pympi_CALL(MPI_Remove_error_string,a0); }
#define MPI_Remove_error_string _pympi_MPI_Remove_error_string

#undef MPI_Abi_get_version
#ifndef PyMPI_HAVE_MPI_Abi_get_version
PyMPI_EXTERN int MPI_Abi_get_version(int* a0,int* a1);
#endif

#undef MPI_Abi_get_info
#ifndef PyMPI_HAVE_MPI_Abi_get_info
PyMPI_EXTERN int MPI_Abi_get_info(MPI_Info* a0);
#endif

#undef MPI_Abi_get_fortran_info
#ifndef PyMPI_HAVE_MPI_Abi_get_fortran_info
PyMPI_EXTERN int MPI_Abi_get_fortran_info(MPI_Info* a0);
#endif

#undef MPI_Get_hw_resource_info
#ifndef PyMPI_HAVE_MPI_Get_hw_resource_info
PyMPI_EXTERN int MPI_Get_hw_resource_info(MPI_Info* a0);
#endif
#define _pympi__MPI_Get_hw_resource_info(...) PyMPI_UNAVAILABLE("MPI_Get_hw_resource_info")
PyMPI_LOCAL int _pympi_MPI_Get_hw_resource_info(MPI_Info* a0) { _pympi_CALL(MPI_Get_hw_resource_info,a0); }
#define MPI_Get_hw_resource_info _pympi_MPI_Get_hw_resource_info

#undef _pympi_CALL
/* */
