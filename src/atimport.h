/* ---------------------------------------------------------------- */

#include "Python.h"

#include "mpi.h"

/* ---------------------------------------------------------------- */

/* Hack for DeinoMPI */
#if defined(DEINO_MPI)
#undef MPICH2
#endif

/* Hack for MS MPI */
#if defined(MS_MPI)
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
#elif defined(MS_MPI)
#include "config/msmpi.h"
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
#elif defined(MS_MPI)
#include "compat/msmpi.h"
#elif defined(MPICH_NAME) && MPICH_NAME==1
#include "compat/mpich1.h"
#elif defined(LAM_MPI)
#include "compat/lammpi.h"
#elif defined(SGI_MPI)
#include "compat/sgimpi.h"
#endif

/* ---------------------------------------------------------------- */

static int PyMPI_KEYVAL_MPI_ATEXIT = MPI_KEYVAL_INVALID;
static int PyMPI_KEYVAL_WIN_MEMORY = MPI_KEYVAL_INVALID;

static MPI_Errhandler PyMPI_ERRHDL_COMM_WORLD = MPI_ERRHANDLER_NULL;
static MPI_Errhandler PyMPI_ERRHDL_COMM_SELF  = MPI_ERRHANDLER_NULL;

static int PyMPI_API_CALL PyMPI_AtExitMPI(MPI_Comm,int,void*,void*);

static int PyMPI_STARTUP_DONE = 0;
static int PyMPI_StartUp(void)
{
  int ierr = MPI_SUCCESS;
  if (PyMPI_STARTUP_DONE) return MPI_SUCCESS;
  PyMPI_STARTUP_DONE = 1;
  /* change error handlers for predefined communicators */
  if (PyMPI_ERRHDL_COMM_WORLD == MPI_ERRHANDLER_NULL) {
    ierr = MPI_Comm_get_errhandler(MPI_COMM_WORLD,
				   &PyMPI_ERRHDL_COMM_WORLD);
    ierr = MPI_Comm_set_errhandler(MPI_COMM_WORLD,
				   MPI_ERRORS_RETURN);
  }
  if (PyMPI_ERRHDL_COMM_SELF == MPI_ERRHANDLER_NULL) {
    ierr = MPI_Comm_get_errhandler(MPI_COMM_SELF,
				   &PyMPI_ERRHDL_COMM_SELF);
    ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF,
				   MPI_ERRORS_RETURN);
  }
  /* make the call to MPI_Finalize() run a cleanup function */
  if (PyMPI_KEYVAL_MPI_ATEXIT == MPI_KEYVAL_INVALID) {
    int keyval = MPI_KEYVAL_INVALID;
    ierr = MPI_Comm_create_keyval(MPI_COMM_NULL_COPY_FN,
				  PyMPI_AtExitMPI, &keyval, 0);
    ierr = MPI_Comm_set_attr(MPI_COMM_SELF, keyval, 0);
    PyMPI_KEYVAL_MPI_ATEXIT = keyval;
  }
  return MPI_SUCCESS;
}

static int PyMPI_CLEANUP_DONE = 0;
static int PyMPI_CleanUp(void)
{
  int ierr = MPI_SUCCESS;
  if (PyMPI_CLEANUP_DONE) return MPI_SUCCESS;
  PyMPI_CLEANUP_DONE = 1;
  /* free atexit keyval */
  if (PyMPI_KEYVAL_MPI_ATEXIT != MPI_KEYVAL_INVALID) {
    ierr = MPI_Comm_free_keyval(&PyMPI_KEYVAL_MPI_ATEXIT);
    PyMPI_KEYVAL_MPI_ATEXIT = MPI_KEYVAL_INVALID;
  }
  /* free windows keyval */
  if (PyMPI_KEYVAL_WIN_MEMORY != MPI_KEYVAL_INVALID) {
    ierr = MPI_Win_free_keyval(&PyMPI_KEYVAL_WIN_MEMORY);
    PyMPI_KEYVAL_WIN_MEMORY = MPI_KEYVAL_INVALID;
  }
  /* restore default error handlers for predefined communicators */
  if (PyMPI_ERRHDL_COMM_SELF != MPI_ERRHANDLER_NULL) {
    ierr = MPI_Comm_set_errhandler(MPI_COMM_SELF,
				   PyMPI_ERRHDL_COMM_SELF);
    ierr = MPI_Errhandler_free(&PyMPI_ERRHDL_COMM_SELF);
    PyMPI_ERRHDL_COMM_SELF = MPI_ERRHANDLER_NULL;
  }
  if (PyMPI_ERRHDL_COMM_WORLD != MPI_ERRHANDLER_NULL) {
    ierr = MPI_Comm_set_errhandler(MPI_COMM_WORLD,
				   PyMPI_ERRHDL_COMM_WORLD);
    ierr = MPI_Errhandler_free(&PyMPI_ERRHDL_COMM_WORLD);
    PyMPI_ERRHDL_COMM_WORLD = MPI_ERRHANDLER_NULL;
  }
  return MPI_SUCCESS;
}

static int PyMPI_AtExitMPI(MPI_Comm comm, int k, void *v, void *xs)
{ return PyMPI_CleanUp(); }

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
  PyObject *b = PyUnicode_AsUTF8String(ob);
  if (b != NULL && PyBytes_AsStringAndSize(b, (char **)s, n) < 0) {
    Py_DECREF(b); b = NULL;
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

/* Enable the block below if for any
   reason you want to disable threads */

#if 0

#define PyGILState_Ensure() (PyGILState_STATE)0)
#define PyGILState_Release(state) (state)=(PyGILState_STATE)0)
#undef  Py_BLOCK_THREADS
#define Py_BLOCK_THREADS (_save)=(PyThreadState*)0;
#undef  Py_UNBLOCK_THREADS
#define Py_UNBLOCK_THREADS (_save)=(PyThreadState*)0;

#endif

/* ---------------------------------------------------------------- */
