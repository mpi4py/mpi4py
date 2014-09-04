/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

/* ------------------------------------------------------------------------- */

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

#ifndef PyMemoryView_FromBuffer
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
