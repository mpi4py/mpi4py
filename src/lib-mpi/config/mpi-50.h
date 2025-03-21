#if defined(MPI_VERSION)
#if (MPI_VERSION >= 5)

#define PyMPI_HAVE_MPI_LOGICAL1 1
#define PyMPI_HAVE_MPI_LOGICAL2 1
#define PyMPI_HAVE_MPI_LOGICAL4 1
#define PyMPI_HAVE_MPI_LOGICAL8 1
#define PyMPI_HAVE_MPI_LOGICAL16 1

#define PyMPI_HAVE_MPI_Comm_toint 1
#define PyMPI_HAVE_MPI_Errhandler_toint 1
#define PyMPI_HAVE_MPI_File_toint 1
#define PyMPI_HAVE_MPI_Group_toint 1
#define PyMPI_HAVE_MPI_Info_toint 1
#define PyMPI_HAVE_MPI_Message_toint 1
#define PyMPI_HAVE_MPI_Op_toint 1
#define PyMPI_HAVE_MPI_Request_toint 1
#define PyMPI_HAVE_MPI_Session_toint 1
#define PyMPI_HAVE_MPI_Type_toint 1
#define PyMPI_HAVE_MPI_Win_toint 1

#define PyMPI_HAVE_MPI_Comm_fromint 1
#define PyMPI_HAVE_MPI_Errhandler_fromint 1
#define PyMPI_HAVE_MPI_File_fromint 1
#define PyMPI_HAVE_MPI_Group_fromint 1
#define PyMPI_HAVE_MPI_Info_fromint 1
#define PyMPI_HAVE_MPI_Message_fromint 1
#define PyMPI_HAVE_MPI_Op_fromint 1
#define PyMPI_HAVE_MPI_Request_fromint 1
#define PyMPI_HAVE_MPI_Session_fromint 1
#define PyMPI_HAVE_MPI_Type_fromint 1
#define PyMPI_HAVE_MPI_Win_fromint 1

#endif
#endif
