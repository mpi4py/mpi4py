/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

/* ------------------------------------------------------------------------- */

#include "Python.h"
#include "mpi.h"

/* ------------------------------------------------------------------------- */

#include "config.h"
#include "missing.h"
#include "fallback.h"
#include "compat.h"

/* ------------------------------------------------------------------------- */

#include "pycompat.h"

#ifdef PYPY_VERSION
  #define PyMPI_RUNTIME_PYPY    1
  #define PyMPI_RUNTIME_CPYTHON 0
#else
  #define PyMPI_RUNTIME_PYPY    0
  #define PyMPI_RUNTIME_CPYTHON 1
#endif

/* ------------------------------------------------------------------------- */

/*
  It could be a good idea to implement the startup and cleanup phases
  employing PMPI_Xxx calls, thus MPI profilers would not notice.

  1) The MPI calls at the startup phase could be (a bit of initial)
     junk for users trying to profile the calls for their own code.

  2) Some (naive?) MPI profilers could get confused if MPI_Xxx routines
     are called inside MPI_Finalize during the cleanup phase.

  If for whatever reason you need it, just change the values of the
  defines below to the corresponding PMPI_Xxx symbols.
*/

#define P_MPI_Comm_get_errhandler MPI_Comm_get_errhandler
#define P_MPI_Comm_set_errhandler MPI_Comm_set_errhandler
#define P_MPI_Errhandler_free     MPI_Errhandler_free
#define P_MPI_Comm_create_keyval  MPI_Comm_create_keyval
#define P_MPI_Comm_free_keyval    MPI_Comm_free_keyval
#define P_MPI_Comm_set_attr       MPI_Comm_set_attr
#define P_MPI_Win_free_keyval     MPI_Win_free_keyval

static MPI_Errhandler PyMPI_ERRHDL_COMM_WORLD = (MPI_Errhandler)0;
static MPI_Errhandler PyMPI_ERRHDL_COMM_SELF  = (MPI_Errhandler)0;
static int PyMPI_KEYVAL_MPI_ATEXIT = MPI_KEYVAL_INVALID;
static int PyMPI_KEYVAL_WIN_MEMORY = MPI_KEYVAL_INVALID;

static int PyMPI_StartUp(void);
static int PyMPI_CleanUp(void);
static int MPIAPI PyMPI_AtExitMPI(MPI_Comm,int,void*,void*);

static int PyMPI_STARTUP_DONE = 0;
static int PyMPI_StartUp(void)
{
  if (PyMPI_STARTUP_DONE) return MPI_SUCCESS;
  PyMPI_STARTUP_DONE = 1;
  /* change error handlers for predefined communicators */
  if (PyMPI_ERRHDL_COMM_WORLD == (MPI_Errhandler)0)
    PyMPI_ERRHDL_COMM_WORLD = MPI_ERRHANDLER_NULL;
  if (PyMPI_ERRHDL_COMM_WORLD == MPI_ERRHANDLER_NULL) {
    (void)P_MPI_Comm_get_errhandler(MPI_COMM_WORLD, &PyMPI_ERRHDL_COMM_WORLD);
    (void)P_MPI_Comm_set_errhandler(MPI_COMM_WORLD, MPI_ERRORS_RETURN);
  }
  if (PyMPI_ERRHDL_COMM_SELF == (MPI_Errhandler)0)
    PyMPI_ERRHDL_COMM_SELF = MPI_ERRHANDLER_NULL;
  if (PyMPI_ERRHDL_COMM_SELF == MPI_ERRHANDLER_NULL) {
    (void)P_MPI_Comm_get_errhandler(MPI_COMM_SELF, &PyMPI_ERRHDL_COMM_SELF);
    (void)P_MPI_Comm_set_errhandler(MPI_COMM_SELF, MPI_ERRORS_RETURN);
  }
  /* make the call to MPI_Finalize() run a cleanup function */
  if (PyMPI_KEYVAL_MPI_ATEXIT == MPI_KEYVAL_INVALID) {
    int keyval = MPI_KEYVAL_INVALID;
    (void)P_MPI_Comm_create_keyval(MPI_COMM_NULL_COPY_FN,
                                   PyMPI_AtExitMPI, &keyval, 0);
    (void)P_MPI_Comm_set_attr(MPI_COMM_SELF, keyval, 0);
    PyMPI_KEYVAL_MPI_ATEXIT = keyval;
  }
  return MPI_SUCCESS;
}

static int PyMPI_CLEANUP_DONE = 0;
static int PyMPI_CleanUp(void)
{
  if (PyMPI_CLEANUP_DONE) return MPI_SUCCESS;
  PyMPI_CLEANUP_DONE = 1;
  /* free atexit keyval */
  if (PyMPI_KEYVAL_MPI_ATEXIT != MPI_KEYVAL_INVALID) {
    (void)P_MPI_Comm_free_keyval(&PyMPI_KEYVAL_MPI_ATEXIT);
    PyMPI_KEYVAL_MPI_ATEXIT = MPI_KEYVAL_INVALID;
  }
  /* free windows keyval */
  if (PyMPI_KEYVAL_WIN_MEMORY != MPI_KEYVAL_INVALID) {
    (void)P_MPI_Win_free_keyval(&PyMPI_KEYVAL_WIN_MEMORY);
    PyMPI_KEYVAL_WIN_MEMORY = MPI_KEYVAL_INVALID;
  }
  /* restore default error handlers for predefined communicators */
  if (PyMPI_ERRHDL_COMM_SELF != MPI_ERRHANDLER_NULL) {
    (void)P_MPI_Comm_set_errhandler(MPI_COMM_SELF, PyMPI_ERRHDL_COMM_SELF);
    (void)P_MPI_Errhandler_free(&PyMPI_ERRHDL_COMM_SELF);
    PyMPI_ERRHDL_COMM_SELF = MPI_ERRHANDLER_NULL;
  }
  if (PyMPI_ERRHDL_COMM_WORLD != MPI_ERRHANDLER_NULL) {
    (void)P_MPI_Comm_set_errhandler(MPI_COMM_WORLD, PyMPI_ERRHDL_COMM_WORLD);
    (void)P_MPI_Errhandler_free(&PyMPI_ERRHDL_COMM_WORLD);
    PyMPI_ERRHDL_COMM_WORLD = MPI_ERRHANDLER_NULL;
  }
  return MPI_SUCCESS;
}

static int MPIAPI PyMPI_AtExitMPI(MPI_Comm comm, int k, void *v, void *xs)
{
  (void)comm; (void)k; (void)v; (void)xs; /* unused */
  return PyMPI_CleanUp();
}

/* ------------------------------------------------------------------------- */

#if !defined(PyMPI_USE_MATCHED_RECV)
  #if defined(PyMPI_HAVE_MPI_Mprobe) && \
      defined(PyMPI_HAVE_MPI_Mrecv)
    #define PyMPI_USE_MATCHED_RECV 1
  #else
    #define PyMPI_USE_MATCHED_RECV 0
  #endif
#endif

/* ------------------------------------------------------------------------- */

static PyObject *
PyMPIString_AsStringAndSize(PyObject *ob, const char **s, Py_ssize_t *n)
{
  PyObject *b = NULL;
  if (PyUnicode_Check(ob)) {
#if PY_MAJOR_VERSION >= 3
    b = PyUnicode_AsUTF8String(ob);
#else
    b = PyUnicode_AsASCIIString(ob);
#endif
    if (!b) return NULL;
  } else {
    b = ob; Py_INCREF(ob);
  }
#if PY_MAJOR_VERSION >= 3
  if (PyBytes_AsStringAndSize(b, (char **)s, n) < 0) {
#else
  if (PyString_AsStringAndSize(b, (char **)s, n) < 0) {
#endif
    Py_DECREF(b);
    return NULL;
  }
  return b;
}

#if PY_MAJOR_VERSION >= 3
#define PyMPIString_FromString        PyUnicode_FromString
#define PyMPIString_FromStringAndSize PyUnicode_FromStringAndSize
#else
#define PyMPIString_FromString        PyString_FromString
#define PyMPIString_FromStringAndSize PyString_FromStringAndSize
#endif

/* ------------------------------------------------------------------------- */

/*
  Local variables:
  c-basic-offset: 2
  indent-tabs-mode: nil
  End:
*/
