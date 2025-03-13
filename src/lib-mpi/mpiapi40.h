#if !defined(PyMPI_HAVE_MPI_F_SOURCE)
#define PyMPI_F_SOURCE ((int)(offsetof(MPI_Status,MPI_SOURCE)/sizeof(int)))
#undef  MPI_F_SOURCE
#define MPI_F_SOURCE PyMPI_F_SOURCE
#endif

#if !defined(PyMPI_HAVE_MPI_F_TAG)
#define PyMPI_F_TAG ((int)(offsetof(MPI_Status,MPI_TAG)/sizeof(int)))
#undef  MPI_F_TAG
#define MPI_F_TAG PyMPI_F_TAG
#endif

#if !defined(PyMPI_HAVE_MPI_F_ERROR)
#define PyMPI_F_ERROR ((int)(offsetof(MPI_Status,MPI_ERROR)/sizeof(int)))
#undef  MPI_F_ERROR
#define MPI_F_ERROR PyMPI_F_ERROR
#endif

#if !defined(PyMPI_HAVE_MPI_F_STATUS_SIZE)
#define PyMPI_F_STATUS_SIZE ((int)(sizeof(MPI_Status)/sizeof(int)))
#undef  MPI_F_STATUS_SIZE
#define MPI_F_STATUS_SIZE PyMPI_F_STATUS_SIZE
#endif

#if !defined(PyMPI_HAVE_MPI_Type_get_envelope_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_get_envelope_c
static int PyMPI_Type_get_envelope_c(
  MPI_Datatype datatype,
  MPI_Count *num_integers,
  MPI_Count *num_addresses,
  MPI_Count *num_large_counts,
  MPI_Count *num_datatypes,
  int *combiner)
{
  PyMPI_WEAK_CALL(
  MPI_Type_get_envelope_c,
  datatype,
  num_integers,
  num_addresses,
  num_large_counts,
  num_datatypes,
  combiner);
  {
  int ierr; int ni = 0, na = 0, nd = 0;
  ierr = MPI_Type_get_envelope(datatype, &ni, &na, &nd, combiner);
  if (ierr != MPI_SUCCESS) return ierr;
  if (num_integers) *num_integers     = ni;
  if (num_addresses) *num_addresses    = na;
  if (num_large_counts) *num_large_counts = 0;
  if (num_datatypes) *num_datatypes    = nd;
  return ierr;
  }
}
#undef  MPI_Type_get_envelope_c
#define MPI_Type_get_envelope_c PyMPI_Type_get_envelope_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_get_contents_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_get_contents_c
static int PyMPI_Type_get_contents_c(
  MPI_Datatype datatype,
  MPI_Count max_integers,
  MPI_Count max_addresses,
  MPI_Count max_large_counts,
  MPI_Count max_datatypes,
  int integers[],
  MPI_Aint addresses[],
  MPI_Count large_counts[],
  MPI_Datatype datatypes[])
{
  PyMPI_WEAK_CALL(
  MPI_Type_get_contents_c,
  datatype,
  max_integers,
  max_addresses,
  max_large_counts,
  max_datatypes,
  integers,
  addresses,
  large_counts,
  datatypes);
  {
  int ierr; int ni, na, nd;
  PyMPICastValue(int, ni, MPI_Count, max_integers);
  PyMPICastValue(int, na, MPI_Count, max_addresses);
  PyMPICastValue(int, nd, MPI_Count, max_datatypes);
  ierr = MPI_Type_get_contents(datatype,
                               ni, na, nd,
                               integers,
                               addresses,
                               datatypes);
  (void)max_large_counts;
  (void)large_counts;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_get_contents_c
#define MPI_Type_get_contents_c PyMPI_Type_get_contents_c
#endif

#if !defined(PyMPI_HAVE_MPI_Info_get_string) || PyMPI_LEGACY_ABI
#undef MPI_Info_get_string
static int PyMPI_Info_get_string(MPI_Info info,
                                 char key[],
                                 int *buflen,
                                 char value[],
                                 int *flag)
{
  PyMPI_WEAK_CALL(MPI_Info_get_string, info, key, buflen, value, flag);
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
}
#define MPI_Info_get_string PyMPI_Info_get_string
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_idup_with_info) || PyMPI_LEGACY_ABI
#undef MPI_Comm_idup_with_info
static int PyMPI_Comm_idup_with_info(MPI_Comm comm,
                                     MPI_Info info,
                                     MPI_Comm *newcomm,
                                     MPI_Request *request)
{
  PyMPI_WEAK_CALL(MPI_Comm_idup_with_info, comm, info, newcomm, request);
  {
  int ierr, dummy;
  if (info != MPI_INFO_NULL) {
    ierr = MPI_Info_get_nkeys(info, &dummy);
    if (ierr != MPI_SUCCESS) return ierr;
  }
  return MPI_Comm_idup(comm, newcomm, request);
  }
}
#define MPI_Comm_idup_with_info PyMPI_Comm_idup_with_info
#endif

#if !defined(PyMPI_HAVE_MPI_Register_datarep_c) || PyMPI_LEGACY_ABI
#undef MPI_Register_datarep_c
typedef struct PyMPI_datarep_s {
  MPI_Datarep_conversion_function_c *read_fn;
  MPI_Datarep_conversion_function_c *write_fn;
  MPI_Datarep_extent_function *extent_fn;
  void *extra_state;
} PyMPI_datarep_t;

static int MPIAPI
  PyMPI_datarep_read_fn(
  void *userbuf,
  MPI_Datatype datatype,
  int count,
  void *filebuf,
  MPI_Offset position,
  void *extra_state)
{
  PyMPI_datarep_t *drep = (PyMPI_datarep_t *) extra_state;
  return drep->read_fn(userbuf, datatype, count,
                       filebuf, position,
                       drep->extra_state);
}

static int MPIAPI
PyMPI_datarep_write_fn(
  void *userbuf,
  MPI_Datatype datatype,
  int count,
  void *filebuf,
  MPI_Offset position,
  void *extra_state)
{
  PyMPI_datarep_t *drep = (PyMPI_datarep_t *) extra_state;
  return drep->write_fn(userbuf, datatype, count,
                        filebuf, position,
                        drep->extra_state);
}

static int PyMPI_Register_datarep_c(
  char *datarep,
  MPI_Datarep_conversion_function_c *read_conversion_fn,
  MPI_Datarep_conversion_function_c *write_conversion_fn,
  MPI_Datarep_extent_function *dtype_file_extent_fn,
  void *extra_state)
{
  PyMPI_WEAK_CALL(
  MPI_Register_datarep_c,
  datarep,
  read_conversion_fn,
  write_conversion_fn,
  dtype_file_extent_fn,
  extra_state);
  {
  static int n = 0; enum {N=64};
  static PyMPI_datarep_t registry[N];
  PyMPI_datarep_t *drep = (n < N) ? &registry[n++] :
    (PyMPI_datarep_t *) PyMPI_MALLOC(sizeof(PyMPI_datarep_t));

  MPI_Datarep_conversion_function *r_fn = MPI_CONVERSION_FN_NULL;
  MPI_Datarep_conversion_function *w_fn = MPI_CONVERSION_FN_NULL;
  MPI_Datarep_extent_function *e_fn = dtype_file_extent_fn;

  drep->read_fn = read_conversion_fn;
  drep->write_fn = write_conversion_fn;
  drep->extent_fn = dtype_file_extent_fn;
  drep->extra_state = extra_state;

  if (read_conversion_fn != MPI_CONVERSION_FN_NULL_C)
    r_fn = PyMPI_datarep_read_fn;
  if (write_conversion_fn != MPI_CONVERSION_FN_NULL_C)
    w_fn = PyMPI_datarep_write_fn;

  return MPI_Register_datarep(datarep, r_fn, w_fn, e_fn, drep);
  }
}
#undef  MPI_Register_datarep_c
#define MPI_Register_datarep_c PyMPI_Register_datarep_c
#endif
