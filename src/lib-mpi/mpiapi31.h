#if !defined(PyMPI_HAVE_MPI_Aint_add) || PyMPI_WITH_LEGACY_ABI
static MPI_Aint PyMPI_Aint_add(MPI_Aint base, MPI_Aint disp)
{
  return (MPI_Aint) ((char*)base + disp);
}
#undef  MPI_Aint_add
#define MPI_Aint_add PyMPI_Aint_add
#endif

#if !defined(PyMPI_HAVE_MPI_Aint_diff) || PyMPI_WITH_LEGACY_ABI
static MPI_Aint PyMPI_Aint_diff(MPI_Aint addr1, MPI_Aint addr2)
{
  return (MPI_Aint) ((char*)addr1 - (char*)addr2);
}
#undef  MPI_Aint_diff
#define MPI_Aint_diff PyMPI_Aint_diff
#endif
