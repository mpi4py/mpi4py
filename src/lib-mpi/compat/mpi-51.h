#if PyMPI_NUMVERSION < 51 || PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI

#ifndef PyMPI_HAVE_MPI_TYPECLASS_LOGICAL
#  if defined(MPI_ABI_VERSION)
#    undef  MPI_TYPECLASS_LOGICAL
#    define MPI_TYPECLASS_LOGICAL 191
#  elif defined(MPICH)
#    undef  MPI_TYPECLASS_LOGICAL
#    define MPI_TYPECLASS_LOGICAL 4
#  elif defined(OPEN_MPI)
#    undef  MPI_TYPECLASS_LOGICAL
#    define MPI_TYPECLASS_LOGICAL 4
#  endif
#endif

static int PyMPI_51_MPI_Type_match_size(int          typeclass,
                                        int          size,
                                        MPI_Datatype *datatype)
{
#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
  if(pympi_numversion() < 51)
#endif
  if (MPI_TYPECLASS_LOGICAL != MPI_UNDEFINED &&
      typeclass == MPI_TYPECLASS_LOGICAL &&
      size > 0 && datatype) {
    MPI_Datatype logical = MPI_DATATYPE_NULL;
    switch (size) {
    case  1: logical = MPI_LOGICAL1;  break;
    case  2: logical = MPI_LOGICAL2;  break;
    case  4: logical = MPI_LOGICAL4;  break;
    case  8: logical = MPI_LOGICAL8;  break;
    case 16: logical = MPI_LOGICAL16; break;
    }
    if (logical != MPI_DATATYPE_NULL) {
      MPI_Count logical_size = MPI_UNDEFINED;
      int ierr = MPI_Type_size_c(logical, &logical_size);
      if (ierr) return ierr;
      if (size != logical_size)
        logical = MPI_DATATYPE_NULL;
    } else {
      MPI_Count logical_size = MPI_UNDEFINED;
      int ierr = MPI_Type_size_c(MPI_LOGICAL, &logical_size);
      if (ierr) return ierr;
      if (size == logical_size)
        logical = MPI_LOGICAL;
    }
    if (logical != MPI_DATATYPE_NULL) {
      *datatype = logical;
      return MPI_SUCCESS;
    }
  }
  return MPI_Type_match_size(typeclass, size, datatype);
}
#undef  MPI_Type_match_size
#define MPI_Type_match_size PyMPI_51_MPI_Type_match_size

#endif /* MPI < 5.1 || PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI */
