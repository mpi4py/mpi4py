/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

#include <stdlib.h>

/* -------------------------------------------------------------------------- */

#if defined(Py_LIMITED_API)
#if !defined(Py_GETENV)
#define Py_GETENV Py_GETENV_311
static char* Py_GETENV(const char *name)
{
  static int ignore_environment = -1;
  if (ignore_environment < 0 && Py_IsInitialized()) {
    PyGILState_STATE save = PyGILState_Ensure();
    PyObject *obj, *attr;
    if ((obj = PySys_GetObject("flags")))
      if ((attr = PyObject_GetAttrString(obj, "ignore_environment")))
        { ignore_environment = PyObject_IsTrue(attr); Py_DecRef(attr); }
    if (PyErr_Occurred()) PyErr_Clear();
    PyGILState_Release(save);
  }
  return ignore_environment == 1 ? NULL : getenv(name);
}
#endif
#endif

#if PY_VERSION_HEX < 0x030B0000 && !defined(Py_GETENV)
#define Py_GETENV(name) (Py_IgnoreEnvironmentFlag ? NULL : getenv(name))
#endif

/* -------------------------------------------------------------------------- */

#if defined(Py_LIMITED_API) && Py_LIMITED_API+0 < 0x030D0000
#if !defined(PyMem_RawMalloc)
PyAPI_FUNC(void *) PyMem_RawMalloc(size_t);
PyAPI_FUNC(void *) PyMem_RawCalloc(size_t, size_t);
PyAPI_FUNC(void *) PyMem_RawRealloc(void *, size_t);
PyAPI_FUNC(void)   PyMem_RawFree(void *);
#endif
#endif

/* -------------------------------------------------------------------------- */

#if defined(Py_LIMITED_API) && Py_LIMITED_API+0 < 0x030C0000
#if !defined(PyErr_DisplayException)
#define PyErr_DisplayException(exc) PyErr_Display(NULL, exc, NULL)
#endif
#endif

#if PY_VERSION_HEX < 0x30C00A7 && !defined(PyErr_DisplayException)
#define PyErr_DisplayException(exc) PyErr_Display(NULL, exc, NULL)
#if defined(PYPY_VERSION)
#undef  PyErr_DisplayException
#define PyErr_DisplayException(exc) do {           \
    PyObject *et = PyObject_Type(exc);             \
    PyObject *tb = PyException_GetTraceback(exc);  \
    PyErr_Display(et, exc, tb);                    \
    Py_DecRef(et);                                 \
    Py_DecRef(tb);                                 \
  } while (0)
#endif
#endif

/* -------------------------------------------------------------------------- */

#if defined(Py_LIMITED_API) && Py_LIMITED_API+0 < 0x030B0000

#define Py_bf_getbuffer 1
#define Py_bf_releasebuffer 2

typedef struct {
  void *buf;
  PyObject *obj;
  Py_ssize_t len;
  Py_ssize_t itemsize;
  int readonly;
  int ndim;
  char *format;
  Py_ssize_t *shape;
  Py_ssize_t *strides;
  Py_ssize_t *suboffsets;
  void *internal;
} Py_buffer;

PyAPI_FUNC(int)  PyObject_CheckBuffer(PyObject *);
PyAPI_FUNC(int)  PyObject_GetBuffer(PyObject *, Py_buffer *, int);
PyAPI_FUNC(void) PyBuffer_Release(Py_buffer *);
PyAPI_FUNC(int)  PyBuffer_FillInfo(Py_buffer *, PyObject *,
                                   void *, Py_ssize_t, int, int);

#define PyBUF_SIMPLE 0
#define PyBUF_WRITABLE 0x0001

#define PyBUF_FORMAT 0x0004
#define PyBUF_ND 0x0008
#define PyBUF_STRIDES (0x0010 | PyBUF_ND)
#define PyBUF_C_CONTIGUOUS (0x0020 | PyBUF_STRIDES)
#define PyBUF_F_CONTIGUOUS (0x0040 | PyBUF_STRIDES)
#define PyBUF_ANY_CONTIGUOUS (0x0080 | PyBUF_STRIDES)

#define PyBUF_READ  0x100
#define PyBUF_WRITE 0x200

#endif

/* -------------------------------------------------------------------------- */

/*
   Local variables:
   c-basic-offset: 2
   indent-tabs-mode: nil
   End:
*/
