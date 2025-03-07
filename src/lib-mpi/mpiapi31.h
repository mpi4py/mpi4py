#if !defined(PyMPI_HAVE_MPI_Aint_add) || PyMPI_LEGACY_ABI
#undef MPI_Aint_add
static MPI_Aint PyMPI_Aint_add(MPI_Aint base, MPI_Aint disp)
{
  PyMPI_WEAK_CALL(MPI_Aint_add, base, disp);
  return (MPI_Aint) ((char*)base + disp);
}
#define MPI_Aint_add PyMPI_Aint_add
#endif

#if !defined(PyMPI_HAVE_MPI_Aint_diff) || PyMPI_LEGACY_ABI
#undef MPI_Aint_diff
static MPI_Aint PyMPI_Aint_diff(MPI_Aint addr1, MPI_Aint addr2)
{
  PyMPI_WEAK_CALL(MPI_Aint_diff, addr1, addr2);
  return (MPI_Aint) ((char*)addr1 - (char*)addr2);
}
#define MPI_Aint_diff PyMPI_Aint_diff
#endif
