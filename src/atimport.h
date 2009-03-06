/* ---------------------------------------------------------------- */

#include "Python.h"

#include "mpi.h"

/* Hack for DeinoMPI */
#if defined(DEINO_MPI)
#undef MPICH2
#endif

/* XXX describe */
#if defined(PyMPI_HAVE_CONFIG_H)
#include "config.h"
#elif defined(MPICH2)
#include "config/mpich2.h"
#elif defined(OPEN_MPI)
#include "config/openmpi.h"
#elif defined(DEINO_MPI)
#include "config/deinompi.h"
#elif defined(MPICH_NAME) && MPICH_NAME==1
#include "config/mpich1.h"
#elif defined(LAM_MPI)
#include "config/lammpi.h"
#elif defined(SGI_MPI)
#include "config/sgimpi.h"
#endif

/* XXX describe */
#include "missing.h"

/* XXX describe */
#include "compat/anympi.h"

/* XXX describe */
#if   defined(MPICH2)
#include "compat/mpich2.h"
#elif defined(OPEN_MPI)
#include "compat/openmpi.h"
#elif defined(DEINO_MPI)
#include "compat/deinompi.h"
#elif defined(MPICH_NAME) && MPICH_NAME==1
#include "compat/mpich1.h"
#elif defined(LAM_MPI)
#include "compat/lammpi.h"
#elif defined(SGI_MPI)
#include "compat/sgimpi.h"
#endif

/* ---------------------------------------------------------------- */

static int PyMPI_KEYVAL_ATEXIT_MPI = MPI_KEYVAL_INVALID;

/* ---------------------------------------------------------------- */

#if PY_MAJOR_VERSION >= 3
static PyObject * PyBuffer_FromReadWriteMemory(void *p, Py_ssize_t n)
{
  Py_buffer info;
  if (PyBuffer_FillInfo(&info, NULL, p, n, 0, 
			PyBUF_ND | PyBUF_STRIDES) < 0)
    return NULL;
  return PyMemoryView_FromBuffer(&info);
}
#endif

/* ---------------------------------------------------------------- */

#if PY_MAJOR_VERSION >= 3
static PyObject * PyMPIString_AsStringAndSize(PyObject *ob, 
					      const char **s,
					      Py_ssize_t *n)
{
  PyObject *b = PyUnicode_AsASCIIString(ob);
  if (b != NULL &&
      PyBytes_AsStringAndSize(b, (char **)s, n) < 0) {
    Py_DECREF(b);
    b = NULL;
  }
  return b;
}
#define PyMPIString_FromString        PyUnicode_FromString
#define PyMPIString_FromStringAndSize PyUnicode_FromStringAndSize
#else
static PyObject * PyMPIString_AsStringAndSize(PyObject *ob,
					      const char **s,
					      Py_ssize_t *n)
{
  if (PyString_AsStringAndSize(ob, (char **)s, n) < 0) return NULL;
  Py_INCREF(ob);
  return ob;
}
#define PyMPIString_FromString        PyString_FromString
#define PyMPIString_FromStringAndSize PyString_FromStringAndSize
#endif

/* ---------------------------------------------------------------- */

#if PY_MAJOR_VERSION >= 3
#define PyMPIBytes_AsString          PyBytes_AsString
#define PyMPIBytes_Size              PyBytes_Size
#define PyMPIBytes_FromStringAndSize PyBytes_FromStringAndSize
#else
#define PyMPIBytes_AsString          PyString_AsString
#define PyMPIBytes_Size              PyString_Size
#define PyMPIBytes_FromStringAndSize PyString_FromStringAndSize
#endif

/* ---------------------------------------------------------------- */
