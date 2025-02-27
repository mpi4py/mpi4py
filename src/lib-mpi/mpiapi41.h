#if !defined(PyMPI_HAVE_MPI_Type_get_value_index) || PyMPI_WITH_LEGACY_ABI
static int PyMPI_Type_get_value_index(MPI_Datatype value,
                                      MPI_Datatype index,
                                      MPI_Datatype *pair)
{
  if (!pair) return MPI_ERR_ARG;
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
#undef  MPI_Type_get_value_index
#define MPI_Type_get_value_index PyMPI_Type_get_value_index
#endif
