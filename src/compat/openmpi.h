#ifndef PyMPI_COMPAT_OPENMPI_H
#define PyMPI_COMPAT_OPENMPI_H

/* ---------------------------------------------------------------- */

#if (defined(OMPI_MAJOR_VERSION) && \
     defined(OMPI_MINOR_VERSION) && \
     defined(OMPI_RELEASE_VERSION))
#define PyMPI_OPENMPI_VERSION ((OMPI_MAJOR_VERSION   * 10000) + \
                               (OMPI_MINOR_VERSION   * 100)   + \
                               (OMPI_RELEASE_VERSION * 1))
#else
#define PyMPI_OPENMPI_VERSION 10000
#endif

/* ---------------------------------------------------------------- */

/*
 * Open MPI releases 1.2.4 and above are shipped with newer versions
 * of GNU libtool.  These libtool versions load dynamic libraries in
 * such a way that library symbols are not globally available by
 * default. This behavior do not interact well with some interal Open
 * MPI components, specifically the ones related to one-side
 * communication operations ('MPI_Win' and related). The vile hackery
 * below try to fix this issue by intercepting the calls to 'MPI_Init'
 * and 'MPI_Finalize' in order to manage preloading of the main Open
 * MPI dynamic library with appropriate flags enablig global
 * availability of library symbols.
 */

#if !defined(OPENMPI_DLOPEN_LIBMPI)
#if PyMPI_OPENMPI_VERSION < 10204
#define OPENMPI_DLOPEN_LIBMPI 0
#else
#define OPENMPI_DLOPEN_LIBMPI 1
#endif
#endif /* !defined(OPENMPI_DLOPEN_LIBMPI) */


#if OPENMPI_DLOPEN_LIBMPI

#if PyMPI_OPENMPI_VERSION < 10400

#if defined(__cplusplus)
#define LT_BEGIN_C_DECLS extern "C" {
#define LT_END_C_DECLS }
#else
#define LT_BEGIN_C_DECLS
#define LT_END_C_DECLS
#endif
#if defined(OMPI_DECLSPEC)
#define LT_SCOPE OMPI_DECLSPEC
#else
#define LT_SCOPE extern
#endif
LT_BEGIN_C_DECLS
typedef void *lt_dlhandle;
typedef void *lt_dladvise;
LT_SCOPE int         lt_dlinit           (void);
LT_SCOPE int         lt_dlexit           (void);
LT_SCOPE int         lt_dladvise_init    (lt_dladvise *advise);
LT_SCOPE int         lt_dladvise_destroy (lt_dladvise *advise);
LT_SCOPE int         lt_dladvise_ext     (lt_dladvise *advise);
LT_SCOPE int         lt_dladvise_global  (lt_dladvise *advise);
LT_SCOPE int         lt_dladvise_local   (lt_dladvise *advise);
LT_SCOPE lt_dlhandle lt_dlopenadvise     (const char *filename,
                                          lt_dladvise advise);
LT_SCOPE int         lt_dlclose          (lt_dlhandle handle);
LT_END_C_DECLS

#elif defined(HAVE_LTDL_H)

#include <ltdl.h>

#elif defined(HAVE_DLOPEN)

#ifdef HAVE_DLFCN_H
#include <dlfcn.h>
#endif
#ifndef RTLD_LAZY
#define RTLD_LAZY 1
#endif
#ifndef RTLD_NOW
#define RTLD_NOW RTLD_LAZY
#endif
#define lt_dlhandle            void*
#define lt_dladvise            int
#define lt_dlinit()            (0)
#define lt_dlexit()            (0)
#define lt_dladvise_init(a)    (*(a)=RTLD_NOW,0)
#define lt_dladvise_destroy(a) (*(a)=0,0)
#define lt_dladvise_ext(a)     (*(a)|=0,0)
#define lt_dladvise_global(a)  (*(a)|=RTLD_GLOBAL,0)
#define lt_dladvise_local(a)   (*(a)|=RTLD_LOCAL,0)
#define lt_dlopenadvise(n,a)   dlopen(n,a)
#define lt_dlclose(h)          dlclose(h)

#endif

static int         OPENMPI_ltdlup = 0;
static lt_dlhandle OPENMPI_libmpi = 0;

static void OPENMPI_dlopen_libmpi(void)
{
  int         ltdlup = OPENMPI_ltdlup;
  lt_dlhandle libmpi = OPENMPI_libmpi;
  if (!ltdlup)
    ltdlup = (lt_dlinit() == 0);
  if (ltdlup) {
    lt_dladvise advise;
    (void)lt_dladvise_init(&advise);
    (void)lt_dladvise_global(&advise);
    if (!libmpi) /* GNU/Linux */
      libmpi = lt_dlopenadvise("libmpi.so.1", advise);
    if (!libmpi)
      libmpi = lt_dlopenadvise("libmpi.so.0", advise);
    if (!libmpi)
      libmpi = lt_dlopenadvise("libmpi.so", advise);
    if (!libmpi) /* Mac OS X */
      libmpi = lt_dlopenadvise("libmpi.1.dylib", advise);
    if (!libmpi)
      libmpi = lt_dlopenadvise("libmpi.0.dylib", advise);
    if (!libmpi)
      libmpi = lt_dlopenadvise("libmpi.dylib", advise);
    (void)lt_dladvise_ext(&advise);
    if (!libmpi) /* Others */
      libmpi = lt_dlopenadvise("libmpi", advise);
    (void)lt_dladvise_destroy(&advise);
  }
  OPENMPI_libmpi = libmpi;
  OPENMPI_ltdlup = ltdlup;
}

static void OPENMPI_dlclose_libmpi(void)
{
  int         ltdlup = OPENMPI_ltdlup;
  lt_dlhandle libmpi = OPENMPI_libmpi;
  if (libmpi && ltdlup) {
    (void)lt_dlclose(libmpi);
    libmpi = 0;
  }
  if (ltdlup) {
    (void)lt_dlexit();
    ltdlup = 0;
  }
  OPENMPI_libmpi = libmpi;
  OPENMPI_ltdlup = ltdlup;
}

static int PyMPI_OPENMPI_MPI_Init(int *argc, char ***argv)
{
  int ierr = MPI_SUCCESS;
  OPENMPI_dlopen_libmpi();
  ierr = MPI_Init(argc, argv);
  return ierr;
}
#undef  MPI_Init
#define MPI_Init PyMPI_OPENMPI_MPI_Init

static int PyMPI_OPENMPI_MPI_Init_thread(int *argc, char ***argv,
                                         int required, int *provided)
{
  int ierr = MPI_SUCCESS;
  OPENMPI_dlopen_libmpi();
  ierr = MPI_Init_thread(argc, argv, required, provided);
  return ierr;
}
#undef  MPI_Init_thread
#define MPI_Init_thread PyMPI_OPENMPI_MPI_Init_thread

static int PyMPI_OPENMPI_MPI_Finalize(void)
{
  int ierr = MPI_SUCCESS;
  ierr = MPI_Finalize();
  OPENMPI_dlclose_libmpi();
  return ierr;
}
#undef  MPI_Finalize
#define MPI_Finalize PyMPI_OPENMPI_MPI_Finalize

#endif /* !OPENMPI_DLOPEN_LIBMPI */

/* ---------------------------------------------------------------- */

/*
 * Open MPI < 1.1.3 generates an error when MPI_File_get_errhandler()
 * is called with the predefined error handlers MPI_ERRORS_RETURN and
 * MPI_ERRORS_ARE_FATAL.
 */

#if PyMPI_OPENMPI_VERSION < 10103

static int PyMPI_OPENMPI_Errhandler_free(MPI_Errhandler *errhandler)
{
  if (errhandler && ((*errhandler == MPI_ERRORS_RETURN) ||
                     (*errhandler == MPI_ERRORS_ARE_FATAL))) {
    *errhandler = MPI_ERRHANDLER_NULL;
    return MPI_SUCCESS;
  }
  return MPI_Errhandler_free(errhandler);
}
#undef  MPI_Errhandler_free
#define MPI_Errhandler_free PyMPI_OPENMPI_Errhandler_free

#endif /* !(PyMPI_OPENMPI_VERSION < 10103) */

/* ---------------------------------------------------------------- */

/*
 * Open MPI 1.1 generates an error when MPI_File_get_errhandler() is
 * called with the MPI_FILE_NULL handle.  The code below try to fix
 * this bug by intercepting the calls to the functions setting and
 * getting the error handlers for MPI_File's.
 */

#if PyMPI_OPENMPI_VERSION < 10200

static MPI_Errhandler PyMPI_OPENMPI_FILE_NULL_ERRHANDLER = (MPI_Errhandler)0;

static int PyMPI_OPENMPI_File_get_errhandler(MPI_File file,
                                             MPI_Errhandler *errhandler)
{
  if (file == MPI_FILE_NULL) {
    if (PyMPI_OPENMPI_FILE_NULL_ERRHANDLER == (MPI_Errhandler)0) {
      PyMPI_OPENMPI_FILE_NULL_ERRHANDLER = MPI_ERRORS_RETURN;
    }
    *errhandler = PyMPI_OPENMPI_FILE_NULL_ERRHANDLER;
    return MPI_SUCCESS;
  }
  return MPI_File_get_errhandler(file, errhandler);
}
#undef  MPI_File_get_errhandler
#define MPI_File_get_errhandler PyMPI_OPENMPI_File_get_errhandler

static int PyMPI_OPENMPI_File_set_errhandler(MPI_File file,
                                             MPI_Errhandler errhandler)
{
  int ierr = MPI_File_set_errhandler(file, errhandler);
  if (ierr != MPI_SUCCESS) return ierr;
  if (file == MPI_FILE_NULL) {
    PyMPI_OPENMPI_FILE_NULL_ERRHANDLER = errhandler;
  }
  return ierr;
}
#undef  MPI_File_set_errhandler
#define MPI_File_set_errhandler PyMPI_OPENMPI_File_set_errhandler

#endif /* !(PyMPI_OPENMPI_VERSION < 10200) */

/* ---------------------------------------------------------------- */

#if PyMPI_OPENMPI_VERSION < 10301

static MPI_Fint PyMPI_OPENMPI_File_c2f(MPI_File file)
{
  if (file == MPI_FILE_NULL) return (MPI_Fint)0;
  return MPI_File_c2f(file);
}
#define MPI_File_c2f PyMPI_OPENMPI_File_c2f

#endif /* !(PyMPI_OPENMPI_VERSION < 10301) */

/* ---------------------------------------------------------------- */

#if PyMPI_OPENMPI_VERSION < 10400

static int PyMPI_OPENMPI_Win_get_errhandler(MPI_Win win,
                                            MPI_Errhandler *errhandler)
{
  if (win == MPI_WIN_NULL) {
    MPI_Comm_call_errhandler(MPI_COMM_WORLD, MPI_ERR_WIN);
    return MPI_ERR_WIN;
  }
  return MPI_Win_get_errhandler(win, errhandler);
}
#undef  MPI_Win_get_errhandler
#define MPI_Win_get_errhandler PyMPI_OPENMPI_Win_get_errhandler

static int PyMPI_OPENMPI_Win_set_errhandler(MPI_Win win,
                                            MPI_Errhandler errhandler)
{
  if (win == MPI_WIN_NULL) {
    MPI_Comm_call_errhandler(MPI_COMM_WORLD, MPI_ERR_WIN);
    return MPI_ERR_WIN;
  }
  return MPI_Win_set_errhandler(win, errhandler);
}
#undef  MPI_Win_set_errhandler
#define MPI_Win_set_errhandler PyMPI_OPENMPI_Win_set_errhandler

#endif /* !(PyMPI_OPENMPI_VERSION < 10400) */

/* ---------------------------------------------------------------- */

#endif /* !PyMPI_COMPAT_OPENMPI_H */

/*
  Local variables:
  c-basic-offset: 2
  indent-tabs-mode: nil
  End:
*/
