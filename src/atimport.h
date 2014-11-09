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

static MPI_Errhandler PyMPI_ERRHDL_COMM_WORLD = (MPI_Errhandler)0;
static MPI_Errhandler PyMPI_ERRHDL_COMM_SELF  = (MPI_Errhandler)0;

static int PyMPI_StartUp(void)
{
  if (PyMPI_ERRHDL_COMM_WORLD == (MPI_Errhandler)0)
    PyMPI_ERRHDL_COMM_WORLD = MPI_ERRHANDLER_NULL;
  if (PyMPI_ERRHDL_COMM_WORLD == MPI_ERRHANDLER_NULL) {
    (void)MPI_Comm_get_errhandler(MPI_COMM_WORLD, &PyMPI_ERRHDL_COMM_WORLD);
    (void)MPI_Comm_set_errhandler(MPI_COMM_WORLD, MPI_ERRORS_RETURN);
  }
  if (PyMPI_ERRHDL_COMM_SELF == (MPI_Errhandler)0)
    PyMPI_ERRHDL_COMM_SELF = MPI_ERRHANDLER_NULL;
  if (PyMPI_ERRHDL_COMM_SELF == MPI_ERRHANDLER_NULL) {
    (void)MPI_Comm_get_errhandler(MPI_COMM_SELF, &PyMPI_ERRHDL_COMM_SELF);
    (void)MPI_Comm_set_errhandler(MPI_COMM_SELF, MPI_ERRORS_RETURN);
  }
  return MPI_SUCCESS;
}

static int PyMPI_CleanUp(void)
{
  if (PyMPI_ERRHDL_COMM_SELF != MPI_ERRHANDLER_NULL) {
    (void)MPI_Comm_set_errhandler(MPI_COMM_SELF, PyMPI_ERRHDL_COMM_SELF);
    (void)MPI_Errhandler_free(&PyMPI_ERRHDL_COMM_SELF);
    PyMPI_ERRHDL_COMM_SELF = MPI_ERRHANDLER_NULL;
  }
  if (PyMPI_ERRHDL_COMM_WORLD != MPI_ERRHANDLER_NULL) {
    (void)MPI_Comm_set_errhandler(MPI_COMM_WORLD, PyMPI_ERRHDL_COMM_WORLD);
    (void)MPI_Errhandler_free(&PyMPI_ERRHDL_COMM_WORLD);
    PyMPI_ERRHDL_COMM_WORLD = MPI_ERRHANDLER_NULL;
  }
  return MPI_SUCCESS;
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
