#if PyMPI_NUMVERSION < 41 || PyMPI_LEGACY_ABI

#if PyMPI_LEGACY_ABI
# define pympi_numversion_lt_41 (pympi_numversion() < 41)
#else
# define pympi_numversion_lt_41 (1)
#endif

#define PyMPI_GET_NAME_NULLOBJ(MPI_HANDLE_NULL) \
  if (pympi_numversion_lt_41) \
  do { if (obj == MPI_HANDLE_NULL && name && rlen) { \
  (void) strncpy(name, #MPI_HANDLE_NULL, MPI_MAX_OBJECT_NAME); \
  name[MPI_MAX_OBJECT_NAME] = 0; *rlen = (int) strlen(name); \
  return MPI_SUCCESS; \
  } } while(0)

static int PyMPI_41_MPI_Type_get_name(MPI_Datatype obj, char *name, int *rlen)
{
  PyMPI_GET_NAME_NULLOBJ(MPI_DATATYPE_NULL);
  return MPI_Type_get_name(obj, name, rlen);
}
#undef  MPI_Type_get_name
#define MPI_Type_get_name PyMPI_41_MPI_Type_get_name

static int PyMPI_41_MPI_Comm_get_name(MPI_Comm obj, char *name, int *rlen)
{
  PyMPI_GET_NAME_NULLOBJ(MPI_COMM_NULL);
  return MPI_Comm_get_name(obj, name, rlen);
}
#undef  MPI_Comm_get_name
#define MPI_Comm_get_name PyMPI_41_MPI_Comm_get_name

static int PyMPI_41_MPI_Win_get_name(MPI_Win obj, char *name, int *rlen)
{
  PyMPI_GET_NAME_NULLOBJ(MPI_WIN_NULL);
  return MPI_Win_get_name(obj, name, rlen);
}
#undef  MPI_Win_get_name
#define MPI_Win_get_name PyMPI_41_MPI_Win_get_name

#undef PyMPI_GET_NAME_NULLOBJ
#undef pympi_numversion_lt_41

#endif /* MPI < 4.1 || PyMPI_LEGACY_ABI */
