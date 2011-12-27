#define MPICH_SKIP_MPICXX 1
#define OMPI_SKIP_MPICXX  1
#include <mpi4py/mpi4py.h>

/* -------------------------------------------------------------------------- */

static void
sayhello(MPI_Comm comm) {
  int size, rank;
  char pname[MPI_MAX_PROCESSOR_NAME]; int len;
  if (comm == MPI_COMM_NULL) {
    printf("You passed MPI_COMM_NULL !!!\n");
    return;
  }
  MPI_Comm_size(comm, &size);
  MPI_Comm_rank(comm, &rank);
  MPI_Get_processor_name(pname, &len);
  pname[len] = 0;
  printf("Hello, World! I am process %d of %d on %s.\n",
         rank, size, pname);
}

/* -------------------------------------------------------------------------- */

static PyObject *
hw_sayhello(PyObject *self, PyObject *args)
{
  PyObject *py_comm = NULL;
  MPI_Comm *comm_p  = NULL;

  if (!PyArg_ParseTuple(args, "O:sayhello", &py_comm))
    return NULL;

  comm_p = PyMPIComm_Get(py_comm);
  if (comm_p == NULL)
    return NULL;

  sayhello(*comm_p);

  Py_INCREF(Py_None);
  return Py_None;
}

static struct PyMethodDef hw_methods[] = {
  {"sayhello", (PyCFunction)hw_sayhello, METH_VARARGS, NULL},
  {NULL,       NULL,                     0,            NULL} /* sentinel */
};

#if PY_MAJOR_VERSION < 3
/* --- Python 2 --- */

PyMODINIT_FUNC inithelloworld(void)
{
  PyObject *m = NULL;

  /* Initialize mpi4py C-API */
  if (import_mpi4py() < 0) goto bad;

  /* Module initialization  */
  m = Py_InitModule("helloworld", hw_methods);
  if (m == NULL) goto bad;

  return;

 bad:
  return;
}

#else
/* --- Python 3 --- */

static struct PyModuleDef hw_module = {
  PyModuleDef_HEAD_INIT,
  "helloworld", /* m_name */
  NULL,         /* m_doc */
  -1,           /* m_size */
  hw_methods    /* m_methods */,
  NULL,         /* m_reload */
  NULL,         /* m_traverse */
  NULL,         /* m_clear */
  NULL          /* m_free */
};

PyMODINIT_FUNC
PyInit_helloworld(void)
{
  PyObject *m = NULL;

  /* Initialize mpi4py's C-API */
  if (import_mpi4py() < 0) goto bad;

  /* Module initialization  */
  m = PyModule_Create(&hw_module);
  if (m == NULL) goto bad;

  return m;

 bad:
  return NULL;
}

#endif

/* -------------------------------------------------------------------------- */

/*
  Local variables:
  c-basic-offset: 2
  indent-tabs-mode: nil
  End:
*/
