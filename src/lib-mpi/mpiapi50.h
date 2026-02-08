#if !defined(PyMPI_HAVE_MPI_Abi_get_version) || PyMPI_LEGACY_ABI
#undef MPI_Abi_get_version
static int PyMPI_Abi_get_version(int *version, int *subversion)
{
  PyMPI_WEAK_CALL(MPI_Abi_get_version, version, subversion);
  if (!version || !subversion) return MPI_ERR_ARG;
  *version = -1; *subversion = -1;
  return MPI_SUCCESS;
}
#define MPI_Abi_get_version PyMPI_Abi_get_version
#endif

#if !defined(PyMPI_HAVE_MPI_Abi_get_info) || PyMPI_LEGACY_ABI
#undef MPI_Abi_get_info
static int PyMPI_Abi_get_info(MPI_Info *info)
{
  MPI_Info abi_info = MPI_INFO_NULL;
  PyMPI_WEAK_CALL(MPI_Abi_get_info, info);
  if (!info) return MPI_ERR_ARG;
#define PyMPI_ABI_SET_TYPE_SIZE(name, type) do { \
  int n = (int) sizeof(type); int ierr; \
  char buf[4], *str = &buf[sizeof(buf)-1]; *str = 0; \
  do { *--str = (char) ('0' + n % 10); n /= 10; } while (n > 0); \
  if (abi_info == MPI_INFO_NULL) \
  { ierr = MPI_Info_create(&abi_info); if (ierr) return ierr; } \
  ierr = MPI_Info_set(abi_info, (char *) name "_size", str); \
  if (ierr) { (void) MPI_Info_free(&abi_info); return ierr; } \
  } while (0)
  PyMPI_ABI_SET_TYPE_SIZE("mpi_aint", MPI_Aint);
  PyMPI_ABI_SET_TYPE_SIZE("mpi_count", MPI_Count);
  PyMPI_ABI_SET_TYPE_SIZE("mpi_offset", MPI_Offset);
#undef PyMPI_ABI_SET_TYPE_SIZE
  *info = abi_info;
  return MPI_SUCCESS;
}
#define MPI_Abi_get_info PyMPI_Abi_get_info
#endif

#if !defined(PyMPI_HAVE_MPI_Abi_get_fortran_info) || PyMPI_LEGACY_ABI
#undef MPI_Abi_get_fortran_info
static int PyMPI_Abi_get_fortran_info(MPI_Info *info)
{
  MPI_Info abi_info = MPI_INFO_NULL;
  PyMPI_WEAK_CALL(MPI_Abi_get_fortran_info, info);
  if (!info) {
    (void) MPI_Comm_call_errhandler(MPI_COMM_SELF, MPI_ERR_ARG);
    return MPI_ERR_ARG;
  }
#if defined(MPICH_NAME) && PyMPI_LEGACY_ABI
#define PyMPI_ABI_HAS_TYPE(type) \
  ((pympi_numversion() < 50 &&   \
    ((type) == MPI_LOGICAL1  ||  \
     (type) == MPI_LOGICAL2  ||  \
     (type) == MPI_LOGICAL4  ||  \
     (type) == MPI_LOGICAL8  ||  \
     (type) == MPI_LOGICAL16 ||  \
     (type) == MPI_INTEGER16 ||  \
     (type) == MPI_REAL2     ||  \
     (type) == MPI_COMPLEX4      \
     )) ? 0 : 1)
#else
#define PyMPI_ABI_HAS_TYPE(type) (1)
#endif
#define PyMPI_ABI_GET_TYPE_SIZE(type, typesize) do { \
    if ((type) != MPI_DATATYPE_NULL && PyMPI_ABI_HAS_TYPE(type)) { \
      MPI_Count size = MPI_UNDEFINED; \
      ierr = MPI_Type_size_c((type), &size); \
      if (!ierr && size > 0) (typesize) = (int) size; \
    } \
  } while (0)
#define PyMPI_ABI_SET_TYPE_SIZE(name, typesize) do { \
    int n = (typesize); char buf[4], *str; \
    str = &buf[sizeof(buf)-1]; *str = 0; \
    do { *--str = (char) ('0' + n % 10); n /= 10; } while (n > 0); \
    ierr = MPI_Info_set(abi_info, (char *) name "_size", str); \
    if (ierr) { (void) MPI_Info_free(&abi_info); return ierr; } \
  } while (0)
#define PyMPI_ABI_SET_TYPE_SUPP(name, type) do { \
    int typesize = 0; char *str; \
    PyMPI_ABI_GET_TYPE_SIZE(type, typesize); \
    str = (char *) (typesize > 0 ? "true" : "false"); \
    ierr = MPI_Info_set(abi_info, (char *) name "_supported", str); \
    if (ierr) { (void) MPI_Info_free(&abi_info); return ierr; } \
  } while (0)
  {
    int l_size = 0, i_size = 0, r_size = 0, d_size = 0, ierr;
    PyMPI_ABI_GET_TYPE_SIZE(MPI_LOGICAL,          l_size);
    PyMPI_ABI_GET_TYPE_SIZE(MPI_INTEGER,          i_size);
    PyMPI_ABI_GET_TYPE_SIZE(MPI_REAL,             r_size);
    PyMPI_ABI_GET_TYPE_SIZE(MPI_DOUBLE_PRECISION, d_size);
    if (!l_size && !i_size && !r_size && !d_size) goto finally;
    ierr = MPI_Info_create(&abi_info); if (ierr) return ierr;
    PyMPI_ABI_SET_TYPE_SIZE("mpi_logical",          l_size);
    PyMPI_ABI_SET_TYPE_SIZE("mpi_integer",          i_size);
    PyMPI_ABI_SET_TYPE_SIZE("mpi_real",             r_size);
    PyMPI_ABI_SET_TYPE_SIZE("mpi_double_precision", d_size);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_logical1",         MPI_LOGICAL1);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_logical2",         MPI_LOGICAL2);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_logical4",         MPI_LOGICAL4);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_logical8",         MPI_LOGICAL8);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_logical16",        MPI_LOGICAL16);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_integer1",         MPI_INTEGER1);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_integer2",         MPI_INTEGER2);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_integer4",         MPI_INTEGER4);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_integer8",         MPI_INTEGER8);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_integer16",        MPI_INTEGER16);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_real2",            MPI_REAL2);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_real4",            MPI_REAL4);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_real8",            MPI_REAL8);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_real16",           MPI_REAL16);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_complex4",         MPI_COMPLEX4);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_complex8",         MPI_COMPLEX8);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_complex16",        MPI_COMPLEX16);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_complex32",        MPI_COMPLEX32);
    PyMPI_ABI_SET_TYPE_SUPP("mpi_double_complex",   MPI_DOUBLE_COMPLEX);
  }
#undef PyMPI_ABI_HAS_TYPE
#undef PyMPI_ABI_GET_TYPE_SIZE
#undef PyMPI_ABI_SET_TYPE_SIZE
#undef PyMPI_ABI_SET_TYPE_SUPP
 finally:
  *info = abi_info;
  return MPI_SUCCESS;
}
#define MPI_Abi_get_fortran_info PyMPI_Abi_get_fortran_info
#endif
