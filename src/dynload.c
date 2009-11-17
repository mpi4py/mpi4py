/* Author:  Lisandro Dalcin
 * Contact: dalcinl@gmail.com
 */

#include "Python.h"
#include "dynload.h"

static PyObject *
dl_dlopen(PyObject *self, PyObject *args)
{
  void *handle = NULL;
  char *filename = NULL;
  int mode = 0;
  if (!PyArg_ParseTuple(args, (char *)"zi:dlopen",
                        &filename, &mode)) return NULL;
  handle = dlopen(filename, mode);
  return PyLong_FromVoidPtr(handle);
}

static PyObject *
dl_dlsym(PyObject *self, PyObject *args)
{
  PyObject *arg0 = NULL;
  void *handle = NULL;
  char *symbol = NULL;
  void *symval = NULL;
  if (!PyArg_ParseTuple(args, (char *)"Os:dlsym",
                        &arg0, &symbol)) return NULL;
#ifdef RTLD_DEFAULT
  handle = (void *)RTLD_DEFAULT;
#endif
  if (arg0 != Py_None) {
    handle = PyLong_AsVoidPtr(arg0);
    if (!handle && PyErr_Occurred())
      return NULL;
  }
  symval = dlsym(handle, symbol);
  return PyLong_FromVoidPtr(symval);
}

static PyObject *
dl_dlclose(PyObject *self, PyObject *arg0)
{
  void *handle = NULL;
  if (arg0 != Py_None) {
    handle = PyLong_AsVoidPtr(arg0);
    if (!handle && PyErr_Occurred())
      return NULL;
  }
  if (handle)
    dlclose(handle);
  return Py_BuildValue((char *)"");
}

static PyObject *
dl_dlerror(PyObject *self, PyObject *args)
{
  char *errmsg = NULL;
  errmsg = dlerror();
  return Py_BuildValue((char *)"z", errmsg);
}

static PyMethodDef dl_methods[] = {
  { (char *)"dlopen",  dl_dlopen,  METH_VARARGS },
  { (char *)"dlsym",   dl_dlsym,   METH_VARARGS },
  { (char *)"dlclose", dl_dlclose, METH_O       },
  { (char *)"dlerror", dl_dlerror, METH_NOARGS  },
  { (char *)NULL,      NULL,       0            } /* sentinel */
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef dl_module = {
  PyModuleDef_HEAD_INIT, /* m_base    */
  (char *)"dl",          /* m_name    */
  NULL,                  /* m_doc     */
  -1,                    /* m_size    */
  dl_methods,            /* m_methods */
  NULL,
};
#endif

#if !defined(PyModule_AddIntMacro)
#define PyModule_AddIntMacro(m, c) \
  PyModule_AddIntConstant(m, (char *)#c, c)
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_dl(void)
#else
PyMODINIT_FUNC initdl(void)
#endif
{
  PyObject *m = NULL;

#if PY_MAJOR_VERSION >= 3
  m = PyModule_Create(&dl_module);
#else
  m = Py_InitModule((char *)"dl", dl_methods);
#endif
  if (!m) goto bad;

  if (PyModule_AddIntMacro(m, RTLD_LAZY     ) < 0) goto bad;
  if (PyModule_AddIntMacro(m, RTLD_NOW      ) < 0) goto bad;
  if (PyModule_AddIntMacro(m, RTLD_LOCAL    ) < 0) goto bad;
  if (PyModule_AddIntMacro(m, RTLD_GLOBAL   ) < 0) goto bad;
#ifdef RTLD_NOLOAD
  if (PyModule_AddIntMacro(m, RTLD_NOLOAD   ) < 0) goto bad;
#endif
#ifdef RTLD_NODELETE
  if (PyModule_AddIntMacro(m, RTLD_NODELETE ) < 0) goto bad;
#endif
#ifdef RTLD_DEEPBIND
  if (PyModule_AddIntMacro(m, RTLD_DEEPBIND ) < 0) goto bad;
#endif
#ifdef RTLD_FIRST
  if (PyModule_AddIntMacro(m, RTLD_FIRST    ) < 0) goto bad;
#endif

#ifdef RTLD_DEFAULT
  {
    PyObject *a = PyLong_FromVoidPtr((void *)RTLD_DEFAULT);
    if (!a) goto bad;
    if (PyModule_AddObject(m, (char *)"RTLD_DEFAULT", a) < 0)
      { Py_DECREF(a); goto bad; }
  }
#endif
#ifdef RTLD_NEXT
  {
    PyObject *a = PyLong_FromVoidPtr((void *)RTLD_NEXT);
    if (!a) goto bad;
    if (PyModule_AddObject(m, (char *)"RTLD_NEXT", a) < 0)
      { Py_DECREF(a); goto bad; }
  }
#endif

 finally:
#if PY_MAJOR_VERSION >= 3
  return m;
#else
  return;
#endif

 bad:
  Py_XDECREF(m);
  m = NULL;
  goto finally;
}

/*
  Local variables:
  c-basic-offset: 2
  indent-tabs-mode: nil
  End:
*/
