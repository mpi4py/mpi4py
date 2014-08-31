/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

/* ------------------------------------------------------------------------- */

#if PY_VERSION_HEX < 0x02060000
#ifndef _PyBytes_Join
#define _PyBytes_Join _PyString_Join
#endif
#endif

#if PY_VERSION_HEX < 0x02060000

#ifndef PyExc_BufferError
#define PyExc_BufferError PyExc_TypeError
#endif/*PyExc_BufferError*/

#ifndef PyBuffer_FillInfo
static int
PyBuffer_FillInfo(Py_buffer *view, PyObject *obj,
                  void *buf, Py_ssize_t len,
                  int readonly, int flags)
{
  if (view == NULL) return 0;
  if (((flags & PyBUF_WRITABLE) == PyBUF_WRITABLE) &&
      (readonly == 1)) {
    PyErr_SetString(PyExc_BufferError,
                    "Object is not writable.");
    return -1;
  }

  view->obj = obj;
  if (obj)
    Py_INCREF(obj);

  view->buf = buf;
  view->len = len;
  view->itemsize = 1;
  view->readonly = readonly;

  view->format = NULL;
  if ((flags & PyBUF_FORMAT) == PyBUF_FORMAT)
    view->format = "B";

  view->ndim = 1;
  view->shape = NULL;
  if ((flags & PyBUF_ND) == PyBUF_ND)
    view->shape = &(view->len);
  view->strides = NULL;
  if ((flags & PyBUF_STRIDES) == PyBUF_STRIDES)
    view->strides = &(view->itemsize);
  view->suboffsets = NULL;

  view->internal = NULL;
  return 0;
}
#endif/*PyBuffer_FillInfo*/

#ifndef PyBuffer_Release
static void
PyBuffer_Release(Py_buffer *view)
{
  PyObject *obj = view->obj;
  Py_XDECREF(obj);
  view->obj = NULL;
}
#endif/*PyBuffer_Release*/

#ifndef PyObject_CheckBuffer
#define PyObject_CheckBuffer(ob) (0)
#endif/*PyObject_CheckBuffer*/

#ifndef PyObject_GetBuffer
#define PyObject_GetBuffer(ob,view,flags) \
        (PyErr_SetString(PyExc_NotImplementedError, \
                        "new buffer interface is not available"), -1)
#endif/*PyObject_GetBuffer*/

#endif

#if PY_VERSION_HEX < 0x02070000
static PyObject *
PyMemoryView_FromBuffer(Py_buffer *view)
{
  if (view->obj) {
    if (view->readonly)
      return PyBuffer_FromObject(view->obj, 0, view->len);
    else
      return PyBuffer_FromReadWriteObject(view->obj, 0, view->len);
  } else {
    if (view->readonly)
      return PyBuffer_FromMemory(view->buf,view->len);
    else
      return PyBuffer_FromReadWriteMemory(view->buf,view->len);
  }
}
#endif

/* ------------------------------------------------------------------------- */

#ifdef PYPY_VERSION

#ifndef PyByteArray_Check
#define PyByteArray_Check(self) PyObject_TypeCheck(self, &PyByteArray_Type)
#endif

#ifndef PyByteArray_AS_STRING
#define PyByteArray_GET_SIZE(self)  0
#define PyByteArray_AS_STRING(self) NULL
#endif

#ifndef _PyLong_AsByteArray
static int
_PyLong_AsByteArray(PyLongObject* v,
                    unsigned char* bytes, size_t n,
                    int little_endian, int is_signed)
{
  (void)_PyLong_AsByteArray; /* unused */
  PyErr_SetString(PyExc_RuntimeError,
                  "PyPy: _PyLong_AsByteArray() not available");
  return -1;
}
#endif

#if PY_VERSION_HEX < 0x02070300 /* PyPy < 2.0 */
#define PyCode_GetNumFree(o) PyCode_GetNumFree((PyObject *)(o))
#endif

#if PY_VERSION_HEX < 0x02070300 /* PyPy < 2.0 */
static int
PyBuffer_FillInfo_PyPy(Py_buffer *view, PyObject *obj,
                       void *buf, Py_ssize_t len,
                       int readonly, int flags)
{
  if (view == NULL) return 0;
  if ((flags & PyBUF_WRITABLE) && readonly) {
    PyErr_SetString(PyExc_BufferError, "Object is not writable.");
    return -1;
  }
  if (PyBuffer_FillInfo(view, obj, buf, len, readonly, flags) < 0)
    return -1;
  view->readonly = readonly;
  return 0;
}
#define PyBuffer_FillInfo PyBuffer_FillInfo_PyPy
#endif

#ifndef PyMemoryView_FromBuffer
static PyObject *
PyMemoryView_FromBuffer_PyPy(Py_buffer *view)
{
  if (view->obj) {
    if (view->readonly)
      return PyBuffer_FromObject(view->obj, 0, view->len);
    else
      return PyBuffer_FromReadWriteObject(view->obj, 0, view->len);
  } else {
    if (view->readonly)
      return PyBuffer_FromMemory(view->buf,view->len);
    else
      return PyBuffer_FromReadWriteMemory(view->buf,view->len);
  }
}
#define PyMemoryView_FromBuffer PyMemoryView_FromBuffer_PyPy
#endif

#endif/*PYPY_VERSION*/

/* ------------------------------------------------------------------------- */

#if !defined(WITH_THREAD)
#undef  PyGILState_Ensure
#define PyGILState_Ensure() ((PyGILState_STATE)0)
#undef  PyGILState_Release
#define PyGILState_Release(state) (state)=((PyGILState_STATE)0)
#undef  Py_BLOCK_THREADS
#define Py_BLOCK_THREADS (_save)=(PyThreadState*)0;
#undef  Py_UNBLOCK_THREADS
#define Py_UNBLOCK_THREADS (_save)=(PyThreadState*)0;
#endif

/* ------------------------------------------------------------------------- */

/*
  Local variables:
  c-basic-offset: 2
  indent-tabs-mode: nil
  End:
*/
