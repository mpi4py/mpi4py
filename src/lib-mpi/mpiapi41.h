#define PyMPI_STATUS_GETATTR(name, NAME) \
static int PyMPI_Status_get_##name(MPI_Status *s, int *i) \
{ PyMPI_WEAK_CALL(MPI_Status_get_##name, s, i); \
  if (s && i) { *i = s->MPI_##NAME; } return MPI_SUCCESS; }

#define PyMPI_STATUS_SETATTR(name, NAME) \
static int PyMPI_Status_set_##name(MPI_Status *s, int i) \
{ PyMPI_WEAK_CALL(MPI_Status_set_##name, s, i); \
  if (s) { s->MPI_##NAME = i; } return MPI_SUCCESS; }

#if !defined(PyMPI_HAVE_MPI_Status_get_source) || PyMPI_LEGACY_ABI
#undef MPI_Status_get_source
#if defined(MPIX_HAVE_MPI_STATUS_GETSET)
#define PyMPI_Status_get_source MPIX_Status_get_source
#else
#define PyMPI_Status_get_source PyMPI_Status_get_source
PyMPI_STATUS_GETATTR(source, SOURCE)
#endif
#define MPI_Status_get_source PyMPI_Status_get_source
#endif

#if !defined(PyMPI_HAVE_MPI_Status_set_source) || PyMPI_LEGACY_ABI
#undef MPI_Status_set_source
#if defined(MPIX_HAVE_MPI_STATUS_GETSET)
#define PyMPI_Status_set_source MPIX_Status_set_source
#else
#define PyMPI_Status_set_source PyMPI_Status_set_source
PyMPI_STATUS_SETATTR(source, SOURCE)
#endif
#define MPI_Status_set_source PyMPI_Status_set_source
#endif

#if !defined(PyMPI_HAVE_MPI_Status_get_tag) || PyMPI_LEGACY_ABI
#undef MPI_Status_get_tag
#if defined(MPIX_HAVE_MPI_STATUS_GETSET)
#define PyMPI_Status_get_tag MPIX_Status_get_tag
#else
#define PyMPI_Status_get_tag PyMPI_Status_get_tag
PyMPI_STATUS_GETATTR(tag, TAG)
#endif
#define MPI_Status_get_tag PyMPI_Status_get_tag
#endif

#if !defined(PyMPI_HAVE_MPI_Status_set_tag) || PyMPI_LEGACY_ABI
#undef MPI_Status_set_tag
#if defined(MPIX_HAVE_MPI_STATUS_GETSET)
#define PyMPI_Status_set_tag MPIX_Status_set_tag
#else
#define PyMPI_Status_set_tag PyMPI_Status_set_tag
PyMPI_STATUS_SETATTR(tag, TAG)
#endif
#define MPI_Status_set_tag PyMPI_Status_set_tag
#endif

#if !defined(PyMPI_HAVE_MPI_Status_get_error) || PyMPI_LEGACY_ABI
#undef MPI_Status_get_error
#if defined(MPIX_HAVE_MPI_STATUS_GETSET)
#define PyMPI_Status_get_error MPIX_Status_get_error
#else
#define PyMPI_Status_get_error PyMPI_Status_get_error
PyMPI_STATUS_GETATTR(error, ERROR)
#endif
#define MPI_Status_get_error PyMPI_Status_get_error
#endif

#if !defined(PyMPI_HAVE_MPI_Status_set_error) || PyMPI_LEGACY_ABI
#undef MPI_Status_set_error
#if defined(MPIX_HAVE_MPI_STATUS_GETSET)
#define PyMPI_Status_set_error MPIX_Status_set_error
#else
#define PyMPI_Status_set_error PyMPI_Status_set_error
PyMPI_STATUS_SETATTR(error, ERROR)
#endif
#define MPI_Status_set_error PyMPI_Status_set_error
#endif

#ifdef PyMPI_STATUS_GETATTR
#undef PyMPI_STATUS_GETATTR
#endif

#ifdef PyMPI_STATUS_SETATTR
#undef PyMPI_STATUS_SETATTR
#endif

#if !defined(PyMPI_HAVE_MPI_Type_get_value_index) || PyMPI_LEGACY_ABI
#undef MPI_Type_get_value_index
static int PyMPI_Type_get_value_index(MPI_Datatype value,
                                      MPI_Datatype index,
                                      MPI_Datatype *pair)
{
  PyMPI_WEAK_CALL(MPI_Type_get_value_index, value, index, pair);
  if (value == MPI_DATATYPE_NULL || index == MPI_DATATYPE_NULL) {
    (void) MPI_Comm_call_errhandler(MPI_COMM_SELF, MPI_ERR_TYPE);
    return MPI_ERR_TYPE;
  }
  if (!pair) {
    (void) MPI_Comm_call_errhandler(MPI_COMM_SELF, MPI_ERR_ARG);
    return MPI_ERR_ARG;
  }
  /**/ if (index != MPI_INT)          *pair = MPI_DATATYPE_NULL;
  else if (value == MPI_FLOAT)        *pair = MPI_FLOAT_INT;
  else if (value == MPI_DOUBLE)       *pair = MPI_DOUBLE_INT;
  else if (value == MPI_LONG_DOUBLE)  *pair = MPI_LONG_DOUBLE_INT;
  else if (value == MPI_LONG)         *pair = MPI_LONG_INT;
  else if (value == MPI_INT)          *pair = MPI_2INT;
  else if (value == MPI_SHORT)        *pair = MPI_SHORT_INT;
  else                                *pair = MPI_DATATYPE_NULL;
  return MPI_SUCCESS;
}
#define MPI_Type_get_value_index PyMPI_Type_get_value_index
#endif
