#------------------------------------------------------------------------------

# Python 3 buffer interface (PEP 3118)
cdef extern from "Python.h":
    ctypedef struct Py_buffer:
        void *buf
        Py_ssize_t len
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


#------------------------------------------------------------------------------

cdef extern from *:
    cdef object toString"PyMPIString_FromString"(char *)

cdef inline int is_buffer(object ob):
    return (PyObject_CheckBuffer(ob) or
            PyObject_CheckReadBuffer(ob))

cdef object asbuffer(object ob,
                     int writable, int format,
                     void **base, MPI_Aint *size):

    cdef void *bptr = NULL
    cdef Py_ssize_t blen = 0
    cdef object bfmt = None
    cdef Py_buffer view
    cdef int flags = PyBUF_SIMPLE
    if PyObject_CheckBuffer(ob):
        flags = PyBUF_ANY_CONTIGUOUS
        if writable:
            flags |= PyBUF_WRITABLE
        if format:
            flags |= PyBUF_FORMAT
        PyObject_GetBuffer(ob, &view, flags)
        bptr = view.buf
        blen = view.len
        if format:
            if view.format != NULL:
                bfmt = toString(view.format)
        PyBuffer_Release(&view)
    else:
        if writable:
            PyObject_AsWriteBuffer(ob, &bptr, &blen)
        else:
            PyObject_AsReadBuffer(ob, <const_void **>&bptr, &blen)
        if format:
            try: # numpy.ndarray
                bfmt = ob.dtype.char
            except AttributeError:
                try: # array.array
                    bfmt = ob.typecode
                except AttributeError:
                    # nothing found
                    bfmt = None
    if base: base[0] = <void *>bptr
    if size: size[0] = <MPI_Aint>blen
    return bfmt

cdef inline object asbuffer_r(object ob, void **base, MPI_Aint *size):
    asbuffer(ob, 0, 0, base, size)
    return ob

cdef inline object asbuffer_w(object ob, void **base, MPI_Aint *size):
    asbuffer(ob, 1, 0, base, size)
    return ob

#------------------------------------------------------------------------------
