#------------------------------------------------------------------------------

cdef extern from "Python.h":
    enum: PY_SSIZE_T_MAX
    void *PyMem_Malloc(size_t)
    void *PyMem_Realloc(void *, size_t)
    void PyMem_Free(void *)

cdef extern from "Python.h":
    object PyLong_FromVoidPtr(void *)
    void*  PyLong_AsVoidPtr(object)

#------------------------------------------------------------------------------

cdef extern from "Python.h":
    object PyMemoryView_FromBuffer(Py_buffer *)

cdef inline object asmemory(object ob, void **base, MPI_Aint *size):
    cdef _p_buffer buf = getbuffer_w(ob, base, size)
    return buf

cdef inline object tomemory(void *base, MPI_Aint size):
    cdef _p_buffer buf = tobuffer(base, size, 0)
    return PyMemoryView_FromBuffer(&buf.view)

#------------------------------------------------------------------------------

#@cython.internal
cdef class _p_mem:
    cdef void *buf
    def __cinit__(self):
        self.buf = NULL
    def __dealloc__(self):
        PyMem_Free(self.buf)

cdef inline _p_mem allocate(Py_ssize_t m, size_t b, void **buf):
  cdef Py_ssize_t n = m * <Py_ssize_t>b
  if n > PY_SSIZE_T_MAX:
      raise MemoryError("memory allocation size too large")
  if n < 0:
      raise RuntimeError("memory allocation with negative size")
  cdef _p_mem ob = <_p_mem>_p_mem.__new__(_p_mem)
  ob.buf = PyMem_Malloc(<size_t>n)
  if ob.buf == NULL: raise MemoryError
  if buf != NULL: buf[0] = ob.buf
  return ob

cdef inline _p_mem allocate_int(int n, int **p):
     cdef _p_mem ob = allocate(n, sizeof(int), NULL)
     p[0] = <int*>ob.buf
     return ob

#------------------------------------------------------------------------------
