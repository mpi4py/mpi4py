# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    enum: PY_SSIZE_T_MAX

    void *PyMem_Malloc(size_t) noexcept
    void *PyMem_Calloc(size_t, size_t) noexcept
    void *PyMem_Realloc(void*, size_t) noexcept
    void  PyMem_Free(void*) noexcept

    void *PyMem_RawMalloc(size_t) noexcept nogil
    void *PyMem_RawCalloc(size_t, size_t) noexcept nogil
    void *PyMem_RawRealloc(void*, size_t) noexcept nogil
    void  PyMem_RawFree(void*) noexcept nogil

# -----------------------------------------------------------------------------

@cython.final
@cython.internal
cdef class _PyMem:

    cdef void *buf
    cdef Py_ssize_t len
    cdef void (*free)(void*) noexcept

    def __cinit__(self):
        self.buf = NULL
        self.len = 0
        self.free = NULL

    def __dealloc__(self):
        if self.free:
            self.free(self.buf)

    def __getbuffer__(self, Py_buffer *view, int flags):
        PyBuffer_FillInfo(view, self, self.buf, self.len, 0, flags)


cdef inline _PyMem allocate(Py_ssize_t m, size_t b, void *buf):
  if m > PY_SSIZE_T_MAX // <Py_ssize_t>b:
      raise MemoryError("memory allocation size too large")  #~> uncovered
  elif m < 0:
      raise RuntimeError("memory allocation with negative size")  #~> uncovered
  cdef _PyMem ob = <_PyMem>New(_PyMem)
  ob.len  = m * <Py_ssize_t>b
  ob.free = PyMem_Free
  ob.buf  = PyMem_Malloc(<size_t>m * b)
  if ob.buf == NULL: raise MemoryError
  if buf != NULL: (<void**>buf)[0] = ob.buf
  return ob


cdef inline _PyMem rawalloc(Py_ssize_t m, size_t b, bint clear, void *buf):
  if m > PY_SSIZE_T_MAX // <Py_ssize_t>b:
      raise MemoryError("memory allocation size too large")  #~> uncovered
  elif m < 0:
      raise RuntimeError("memory allocation with negative size")  #~> uncovered
  cdef _PyMem ob = <_PyMem>New(_PyMem)
  ob.len = m * <Py_ssize_t>b
  ob.free = PyMem_RawFree
  if clear:
      ob.buf = PyMem_RawCalloc(<size_t>m, b)
  else:
      ob.buf = PyMem_RawMalloc(<size_t>m * b)
  if ob.buf == NULL: raise MemoryError
  if buf != NULL: (<void**>buf)[0] = ob.buf
  return ob

# -----------------------------------------------------------------------------
