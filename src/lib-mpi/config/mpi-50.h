#if defined(MPI_VERSION)
#if (MPI_VERSION >= 5) || defined(MPI_ABI_VERSION)

#define PyMPI_HAVE_MPI_Comm_toint
#define PyMPI_HAVE_MPI_Errhandler_toint
#define PyMPI_HAVE_MPI_File_toint
#define PyMPI_HAVE_MPI_Group_toint
#define PyMPI_HAVE_MPI_Info_toint
#define PyMPI_HAVE_MPI_Message_toint
#define PyMPI_HAVE_MPI_Op_toint
#define PyMPI_HAVE_MPI_Request_toint
#define PyMPI_HAVE_MPI_Session_toint
#define PyMPI_HAVE_MPI_Type_toint
#define PyMPI_HAVE_MPI_Win_toint

#define PyMPI_HAVE_MPI_Comm_fromint
#define PyMPI_HAVE_MPI_Errhandler_fromint
#define PyMPI_HAVE_MPI_File_fromint
#define PyMPI_HAVE_MPI_Group_fromint
#define PyMPI_HAVE_MPI_Info_fromint
#define PyMPI_HAVE_MPI_Message_fromint
#define PyMPI_HAVE_MPI_Op_fromint
#define PyMPI_HAVE_MPI_Request_fromint
#define PyMPI_HAVE_MPI_Session_fromint
#define PyMPI_HAVE_MPI_Type_fromint
#define PyMPI_HAVE_MPI_Win_fromint

#endif
#endif
