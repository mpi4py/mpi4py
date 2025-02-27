#ifndef PyMPI_HAVE_MPI_F_SOURCE
#define PyMPI_F_SOURCE ((int)(offsetof(MPI_Status,MPI_SOURCE)/sizeof(int)))
#undef  MPI_F_SOURCE
#define MPI_F_SOURCE PyMPI_F_SOURCE
#endif

#ifndef PyMPI_HAVE_MPI_F_TAG
#define PyMPI_F_TAG ((int)(offsetof(MPI_Status,MPI_TAG)/sizeof(int)))
#undef  MPI_F_TAG
#define MPI_F_TAG PyMPI_F_TAG
#endif

#ifndef PyMPI_HAVE_MPI_F_ERROR
#define PyMPI_F_ERROR ((int)(offsetof(MPI_Status,MPI_ERROR)/sizeof(int)))
#undef  MPI_F_ERROR
#define MPI_F_ERROR PyMPI_F_ERROR
#endif

#ifndef PyMPI_HAVE_MPI_F_STATUS_SIZE
#define PyMPI_F_STATUS_SIZE ((int)(sizeof(MPI_Status)/sizeof(int)))
#undef  MPI_F_STATUS_SIZE
#define MPI_F_STATUS_SIZE PyMPI_F_STATUS_SIZE
#endif

#if !defined(PyMPI_HAVE_MPI_Info_get_string) || PyMPI_WITH_LEGACY_ABI
static int PyMPI_Info_get_string(MPI_Info info,
                                 char key[],
                                 int *buflen,
                                 char value[],
                                 int *flag)
{
  int ierr, valuelen = buflen ? *buflen : 0;
  if (valuelen) {
    ierr = MPI_Info_get(info, key, valuelen-1, value, flag);
    if (ierr != MPI_SUCCESS) return ierr;
    if (value && flag && *flag) value[valuelen] = 0;
  }
  ierr = MPI_Info_get_valuelen(info, key, &valuelen, flag);
  if (ierr != MPI_SUCCESS) return ierr;
  if (buflen && flag && *flag) *buflen = valuelen + 1;
  return MPI_SUCCESS;
}
#undef  MPI_Info_get_string
#define MPI_Info_get_string PyMPI_Info_get_string
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_idup_with_info) || PyMPI_WITH_LEGACY_ABI
static int PyMPI_Comm_idup_with_info(MPI_Comm comm, MPI_Info info,
                                     MPI_Comm *newcomm, MPI_Request *request)
{
  int dummy, ierr;
  if (info != MPI_INFO_NULL) {
    ierr = MPI_Info_get_nkeys(info, &dummy);
    if (ierr != MPI_SUCCESS) return ierr;
  }
  return MPI_Comm_idup(comm, newcomm, request);
}
#undef  MPI_Comm_idup_with_info
#define MPI_Comm_idup_with_info PyMPI_Comm_idup_with_info
#endif
