#include "mpi.h"
#include "stdio.h"

static int MPI_Get_vendor(const char **vendor_name,
			  int         *version_major,
			  int         *version_minor,
			  int         *version_micro)
{
  const char* name="unknown";
  int major=0, minor=0, micro=0;

  /* MPICH2 */
#if defined(MPICH2)
  name = "MPICH2";
  #if defined(MPICH2_VERSION)
  sscanf(MPICH2_VERSION,"%d.%d.%d",&major,&minor,&micro);
  #endif
#endif

  /* Open MPI */
#if defined(OPEN_MPI)
  name = "Open MPI";
  #if defined(OMPI_MAJOR_VERSION)
  major = OMPI_MAJOR_VERSION;
  #endif
  #if defined(OMPI_MINOR_VERSION)
  minor = OMPI_MINOR_VERSION;
  #endif
  #if defined(OMPI_RELEASE_VERSION)
  micro = OMPI_RELEASE_VERSION;
  #endif
#endif

  /* HP MPI */
#if defined(HP_MPI)
  name = "HP MPI";
  major = HP_MPI/100;
  minor = HP_MPI%100;
  #if defined(HP_MPI_MINOR)
  micro = HP_MPI_MINOR;
  #endif
#endif

  /* DeinoMPI */
#if defined(DEINO_MPI)
  name = "DeinoMPI";
#endif

  /* MPICH1 */
#if defined(MPICH_NAME) && MPICH_NAME==1
  name = "MPICH1";
  #if defined(MPICH_VERSION)
  sscanf(MPICH_VERSION,"%d.%d.%d",&major,&minor,&micro);
  #endif
#endif

  /* LAM/MPI */
#if defined(LAM_MPI)
  name = "LAM/MPI";
  #if defined(LAM_MAJOR_VERSION)
  major = LAM_MAJOR_VERSION;
  #endif
  #if defined(LAM_MINOR_VERSION)
  minor = LAM_MINOR_VERSION;
  #endif
  #if defined(LAM_RELEASE_VERSION)
  micro = LAM_RELEASE_VERSION;
  #endif
#endif

  if (vendor_name)   *vendor_name   = name;
  if (version_major) *version_major = major;
  if (version_minor) *version_minor = minor;
  if (version_micro) *version_micro = micro;

  return 0;
}
