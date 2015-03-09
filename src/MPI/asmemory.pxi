#------------------------------------------------------------------------------

cdef extern from "Python.h":
    enum: PY_SSIZE_T_MAX
    void *PyMem_Malloc(size_t)
    void *PyMem_Realloc(void*, size_t)
    void PyMem_Free(void*)

cdef extern from "Python.h":
    object PyLong_FromVoidPtr(void*)
    void*  PyLong_AsVoidPtr(object)

cdef extern from "Python.h":
    enum: PyBUF_READ
    enum: PyBUF_WRITE
    object PyMemoryView_FromMemory(char*,Py_ssize_t,int)

#------------------------------------------------------------------------------

@cython.final
cdef class memory:

    cdef void*      buf
    cdef Py_ssize_t len

    # buffer interface (PEP 3118)
    def __getbuffer__(self, Py_buffer *view, int flags):
        if view == NULL: return
        if view.obj == <void*>None: Py_CLEAR(view.obj)
        PyBuffer_FillInfo(view, <object>NULL, self.buf, self.len, 0, flags)

    def __releasebuffer__(self, Py_buffer *view):
        if view == NULL: return
        PyBuffer_Release(view)

    # buffer interface (legacy)
    def __getsegcount__(self, Py_ssize_t *lenp):
        if lenp != NULL:
            lenp[0] = self.len
        return 1
    def __getreadbuffer__(self, Py_ssize_t idx, void **p):
        if idx != 0: raise SystemError(
            "accessing non-existent buffer segment")
        p[0] = self.buf
        return self.len
    def __getwritebuffer__(self, Py_ssize_t idx, void **p):
        if idx != 0: raise SystemError(
            "accessing non-existent buffer segment")
        p[0] = self.buf
        return self.len

    # basic sequence interface
    def __len__(self):
        return self.len
    def __getitem__(self, Py_ssize_t i):
        cdef unsigned char *buf = <unsigned char *>self.buf
        if i < 0: i += self.len
        if i < 0 or i >= self.len:
            raise IndexError("index out of range")
        return <long>buf[i]
    def __setitem__(self, Py_ssize_t i, unsigned char v):
        cdef unsigned char *buf = <unsigned char*>self.buf
        if i < 0: i += self.len
        if i < 0 or i >= self.len:
            raise IndexError("index out of range")
        buf[i] = v


cdef inline memory newmemory(void *buf, Py_ssize_t len):
    cdef memory mem = <memory>memory.__new__(memory)
    mem.buf = buf
    mem.len = len
    return mem

cdef extern from *:
    void *emptymemory '((void*)"")'

cdef inline object asmemory(object ob, void **base, MPI_Aint *size):
    cdef _p_buffer buf = getbuffer_w(ob, base, size)
    return buf

cdef inline object tomemory(void *base, MPI_Aint size):
    if base == NULL and size == 0: base = emptymemory
    if PYPY and PY3: return newmemory(base, size)
    return PyMemoryView_FromMemory(<char*>base, size, PyBUF_WRITE)

#------------------------------------------------------------------------------

@cython.final
@cython.internal
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
