#------------------------------------------------------------------------------

# Python 3 buffer interface (PEP 3118)
cdef extern from "Python.h":
    ctypedef struct Py_buffer:
        void *buf
        Py_ssize_t len
        Py_ssize_t itemsize
        char *format
    cdef enum:
        PyBUF_SIMPLE
        PyBUF_WRITABLE
        PyBUF_FORMAT
        PyBUF_ANY_CONTIGUOUS
    int  PyObject_CheckBuffer(object)
    int  PyObject_GetBuffer(object, Py_buffer *, int) except -1
    void PyBuffer_Release(Py_buffer *)

# Python 2 buffer interface (legacy)
cdef extern from "Python.h":
    ctypedef void const_void "const void"
    int PyObject_CheckReadBuffer(object)
    int PyObject_AsReadBuffer (object, const_void **, Py_ssize_t *) except -1
    int PyObject_AsWriteBuffer(object, void **, Py_ssize_t *) except -1

cdef extern from *:
    cdef object toString"PyMPIString_FromString"(char *)

#------------------------------------------------------------------------------

cdef class _p_buffer:
    cdef object obj
    cdef void *base
    cdef Py_ssize_t size
    cdef object format
    cdef Py_buffer view
    def __dealloc__(self):
        PyBuffer_Release(&self.view)

cdef inline int checkbuffer(object ob):
    return (PyObject_CheckBuffer(ob) or
            PyObject_CheckReadBuffer(ob))

cdef _p_buffer getbuffer(object ob, int writable, int format):
    cdef _p_buffer buf = <_p_buffer>_p_buffer.__new__(_p_buffer)
    if ob is None: return buf
    cdef Py_buffer *view = &buf.view
    cdef int flags = PyBUF_SIMPLE
    if PyObject_CheckBuffer(ob):
        # Python 3 buffer interface (PEP 3118)
        flags = PyBUF_ANY_CONTIGUOUS
        if writable:
            flags |= PyBUF_WRITABLE
        if format:
            flags |= PyBUF_FORMAT
        PyObject_GetBuffer(ob, view, flags)
        buf.obj  = ob
        buf.base = view.buf
        buf.size = view.len
        if format and view.format != NULL:
            buf.format = toString(view.format)
    else:
        # Python 2 buffer interface (legacy)
        if writable:
            PyObject_AsWriteBuffer(ob, &buf.base, &buf.size)
        else:
            PyObject_AsReadBuffer(ob, <const_void **>&buf.base, &buf.size)
        buf.obj  = ob
        if format:
            try: # numpy.ndarray
                dtype = ob.dtype
                buf.format = dtype.char
            except AttributeError:
                try: # array.array
                    buf.format = ob.typecode
                except AttributeError:
                    if isinstance(ob, bytes):
                        buf.format = "B"
                    else:
                        buf.format = None
    return buf

cdef inline _p_buffer getbuffer_r(object ob, void **base, MPI_Aint *size):
    cdef _p_buffer buf = getbuffer(ob, 0, 0)
    if base: base[0] = <void*>    buf.base
    if size: size[0] = <MPI_Aint> buf.size
    return buf

cdef inline _p_buffer getbuffer_w(object ob, void **base, MPI_Aint *size):
    cdef _p_buffer buf = getbuffer(ob, 1, 0)
    if base: base[0] = <void*>    buf.base
    if size: size[0] = <MPI_Aint> buf.size
    return buf

#------------------------------------------------------------------------------
