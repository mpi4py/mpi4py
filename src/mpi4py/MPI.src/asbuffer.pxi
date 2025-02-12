# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    ctypedef struct PyObject
    void Py_CLEAR(PyObject*)
    object PyLong_FromVoidPtr(void*)
    void*  PyLong_AsVoidPtr(object) except? NULL

# Python 3 buffer interface (PEP 3118)
cdef extern from "Python.h":
    ctypedef struct Py_buffer:
        PyObject *obj
        void *buf
        Py_ssize_t len
        Py_ssize_t itemsize
        bint readonly
        char *format
        int ndim
        Py_ssize_t *shape
        Py_ssize_t *strides
        Py_ssize_t *suboffsets
        void *internal
    cdef enum:
        PyBUF_SIMPLE
        PyBUF_WRITABLE
        PyBUF_FORMAT
        PyBUF_ND
        PyBUF_STRIDES
        PyBUF_ANY_CONTIGUOUS
    int  PyObject_CheckBuffer(object)
    int  PyObject_GetBuffer(object, Py_buffer *, int) except -1
    void PyBuffer_Release(Py_buffer *)
    int  PyBuffer_FillInfo(Py_buffer *, object,
                           void *, Py_ssize_t,
                           bint, int) except -1

cdef extern from "Python.h":
    enum: PyBUF_READ
    enum: PyBUF_WRITE
    object PyMemoryView_FromObject(object)
    object PyMemoryView_GetContiguous(object, int, char)


cdef inline int is_big_endian() noexcept nogil:
    cdef int i = 1
    return (<char*>&i)[0] == 0


cdef inline int is_little_endian() noexcept nogil:
    cdef int i = 1
    return (<char*>&i)[0] != 0


cdef char BYTE_FMT[2]
BYTE_FMT[0] = c'B'
BYTE_FMT[1] = 0

include "asdlpack.pxi"
include "ascaibuf.pxi"

cdef int PyMPI_GetBuffer(object obj, Py_buffer *view, int flags) except -1:
    try:
        return PyObject_GetBuffer(obj, view, flags)
    except BaseException:
        try:
            return Py_GetDLPackBuffer(obj, view, flags)
        except NotImplementedError:
            pass
        except BaseException:
            raise
        try:
            return Py_GetCAIBuffer(obj, view, flags)
        except NotImplementedError:
            pass
        except BaseException:
            raise
        raise

cdef void PyMPI_ReleaseBuffer(int kind, Py_buffer *view) noexcept:
    if kind == 0:
        # Python buffer interface
        PyBuffer_Release(view)
    else:
        # DLPack/CAI buffer interface
        Py_CLEAR(view.obj)

# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    int PyIndex_Check(object)
    int PySlice_Check(object)
    int PySlice_Unpack(object,
                       Py_ssize_t *,
                       Py_ssize_t *,
                       Py_ssize_t *) except -1
    Py_ssize_t PySlice_AdjustIndices(Py_ssize_t,
                                     Py_ssize_t *,
                                     Py_ssize_t *,
                                     Py_ssize_t) noexcept nogil
    Py_ssize_t PyNumber_AsSsize_t(object, object) except? -1

cdef inline int check_cpu_accessible(int kind) except -1:
    cdef unsigned device_type = <unsigned> kind
    if device_type == 0              : return 0
    if device_type == kDLCPU         : return 0
    if device_type == kDLCUDAHost    : return 0  # ~> uncovered
    if device_type == kDLROCMHost    : return 0  # ~> uncovered
    if device_type == kDLCUDAManaged : return 0  # ~> uncovered
    raise BufferError("buffer is not CPU-accessible")


@cython.final
cdef class buffer:
    """
    Buffer.
    """

    cdef Py_buffer view
    cdef int       kind

    def __cinit__(self, *args):
        if args:
            self.kind = PyMPI_GetBuffer(args[0], &self.view, PyBUF_SIMPLE)
        else:
            PyBuffer_FillInfo(&self.view, <object>NULL,
                              NULL, 0, 0, PyBUF_SIMPLE)

    def __dealloc__(self):
        PyMPI_ReleaseBuffer(self.kind, &self.view)

    @staticmethod
    def allocate(
        Aint nbytes: int,
        bint clear: bool = False,
    ) -> buffer:
        """Buffer allocation."""
        cdef void *addr = NULL
        cdef Py_ssize_t size = nbytes
        if size < 0:
            raise ValueError("expecting non-negative size")
        cdef object ob = rawalloc(size, 1, clear, &addr)
        cdef buffer buf = <buffer>New(buffer)
        PyBuffer_FillInfo(&buf.view, ob, addr, size, 0, PyBUF_SIMPLE)
        return buf

    @staticmethod
    def frombuffer(
        obj: Buffer,
        bint readonly: bool = False,
    ) -> buffer:
        """Buffer from buffer-like object."""
        cdef int flags = PyBUF_SIMPLE
        if not readonly: flags |= PyBUF_WRITABLE
        cdef buffer buf = <buffer>New(buffer)
        buf.kind = PyMPI_GetBuffer(obj, &buf.view, flags)
        buf.view.readonly = readonly
        return buf

    @staticmethod
    def fromaddress(
        address: int,
        Aint nbytes: int,
        bint readonly: bool = False,
    ) -> buffer:
        """Buffer from address and size in bytes."""
        cdef void *addr = PyLong_AsVoidPtr(address)
        cdef Py_ssize_t size = nbytes
        if size < 0:
            raise ValueError("expecting non-negative buffer length")
        elif size > 0 and addr == NULL:
            raise ValueError("expecting non-NULL address")
        cdef buffer buf = <buffer>New(buffer)
        PyBuffer_FillInfo(&buf.view, <object>NULL,
                          addr, size, readonly, PyBUF_SIMPLE)
        return buf

    # properties

    property address:
        """Buffer address."""
        def __get__(self) -> int:
            return PyLong_FromVoidPtr(self.view.buf)

    # memoryview properties

    property obj:
        """Object exposing buffer."""
        def __get__(self) -> Buffer | None:
            if self.view.obj == NULL: return None
            return <object>self.view.obj

    property nbytes:
        """Buffer size (in bytes)."""
        def __get__(self) -> int:
            return self.view.len

    property readonly:
        """Buffer is read-only."""
        def __get__(self) -> bool:
            return self.view.readonly

    property format:
        """Format of each element."""
        def __get__(self) -> str:
            if self.view.format != NULL:
                return pystr(self.view.format)
            return pystr(BYTE_FMT)

    property itemsize:
        """Size (in bytes) of each element."""
        def __get__(self) -> int:
            return self.view.itemsize

    # memoryview methods

    def cast(
        self,
        format: str,
        shape: list[int] | tuple[int, ...] = ...,
    ) -> memoryview:
        """
        Cast to a `memoryview` with new format or shape.
        """
        check_cpu_accessible(self.kind)
        if shape is Ellipsis:
            return PyMemoryView_FromObject(self).cast(format)
        else:
            return PyMemoryView_FromObject(self).cast(format, shape)

    def tobytes(self, order: str | None = None) -> bytes:
        """Return the data in the buffer as a byte string."""
        <void> order  # unused
        check_cpu_accessible(self.kind)
        return PyBytes_FromStringAndSize(<char*>self.view.buf, self.view.len)

    def toreadonly(self) -> buffer:
        """Return a readonly version of the buffer object."""
        cdef object obj = self
        if self.view.obj != NULL:
            obj = <object>self.view.obj
        cdef buffer buf = <buffer>New(buffer)
        buf.kind = PyMPI_GetBuffer(obj, &buf.view, PyBUF_SIMPLE)
        buf.view.readonly = 1
        return buf

    def release(self) -> None:
        """Release the underlying buffer exposed by the buffer object."""
        PyMPI_ReleaseBuffer(self.kind, &self.view)
        PyBuffer_FillInfo(&self.view, <object>NULL,
                          NULL, 0, 0, PyBUF_SIMPLE)
        self.kind = 0

    # buffer interface (PEP 3118)

    def __getbuffer__(self, Py_buffer *view, int flags):
        PyBuffer_FillInfo(view, self,
                          self.view.buf, self.view.len,
                          self.view.readonly, flags)

    # sequence interface (basic)

    def __len__(self):
        return self.view.len

    def __getitem__(self, object item):
        check_cpu_accessible(self.kind)
        cdef Py_ssize_t start=0, stop=0, step=1, slen=0
        cdef unsigned char *buf = <unsigned char*>self.view.buf
        cdef Py_ssize_t blen = self.view.len
        if PyIndex_Check(item):
            start = PyNumber_AsSsize_t(item, IndexError)
            if start < 0: start += blen
            if start < 0 or start >= blen:
                raise IndexError("index out of range")
            return <long>buf[start]
        elif PySlice_Check(item):
            PySlice_Unpack(item, &start, &stop, &step)
            slen = PySlice_AdjustIndices(blen, &start, &stop, step)
            if step != 1: raise IndexError("slice with step not supported")
            return tobuffer(self, buf+start, slen, self.view.readonly)
        else:
            raise TypeError("index must be integer or slice")

    def __setitem__(self, object item, object value):
        check_cpu_accessible(self.kind)
        if self.view.readonly:
            raise TypeError("buffer is read-only")
        cdef Py_ssize_t start=0, stop=0, step=1, slen=0
        cdef unsigned char *buf = <unsigned char*>self.view.buf
        cdef Py_ssize_t blen = self.view.len
        cdef buffer inbuf
        if PyIndex_Check(item):
            start = PyNumber_AsSsize_t(item, IndexError)
            if start < 0: start += blen
            if start < 0 or start >= blen:
                raise IndexError("index out of range")
            buf[start] = <unsigned char>value
        elif PySlice_Check(item):
            PySlice_Unpack(item, &start, &stop, &step)
            slen = PySlice_AdjustIndices(blen, &start, &stop, step)
            if step != 1: raise IndexError("slice with step not supported")
            if PyIndex_Check(value):
                <void>memset(buf+start, <unsigned char>value, <size_t>slen)
            else:
                inbuf = getbuffer(value, 1, 0)
                if inbuf.view.len != slen:
                    raise ValueError("slice length does not match buffer")
                <void>memmove(buf+start, inbuf.view.buf, <size_t>slen)
        else:
            raise TypeError("index must be integer or slice")


memory = buffer  # Backward compatibility alias

# -----------------------------------------------------------------------------

cdef inline buffer newbuffer():
    return <buffer>New(buffer)

cdef inline buffer getbuffer(object ob, bint readonly, bint format):
    cdef buffer buf = newbuffer()
    cdef int flags = PyBUF_ANY_CONTIGUOUS
    if not readonly:
        flags |= PyBUF_WRITABLE
    if format:
        flags |= PyBUF_FORMAT
    buf.kind = PyMPI_GetBuffer(ob, &buf.view, flags)
    return buf

cdef inline buffer asbuffer(object ob, void **base, MPI_Aint *size, bint ro):
    cdef buffer buf
    if type(ob) is buffer:
        buf = <buffer> ob
        if buf.view.readonly and not ro:
            raise BufferError("Object is not writable")
    else:
        buf = getbuffer(ob, ro, 0)
    if base != NULL: base[0] = buf.view.buf
    if size != NULL: size[0] = buf.view.len
    return buf

cdef inline buffer asbuffer_r(object ob, void **base, MPI_Aint *size):
    return asbuffer(ob, base, size, 1)

cdef inline buffer asbuffer_w(object ob, void **base, MPI_Aint *size):
    return asbuffer(ob, base, size, 0)

cdef inline buffer tobuffer(object ob, void *base, MPI_Aint size, bint ro):
    if size < 0: raise ValueError("expecting non-negative buffer length")
    cdef buffer buf = newbuffer()
    PyBuffer_FillInfo(&buf.view, ob, base, size, ro, PyBUF_SIMPLE)
    return buf

cdef inline buffer mpibuf(void *base, MPI_Count count):
    cdef MPI_Aint size = <MPI_Aint>count
    cdef int neq = (count != <MPI_Count>size)
    if neq: raise OverflowError("length {count} does not fit in 'MPI_Aint'")
    return tobuffer(<object>NULL, base, size, 0)

cdef inline object aspybuffer(
    object obj,
    void **base,
    MPI_Aint *size,
    bint readonly,
    const char format[],
):
    cdef int buftype = PyBUF_READ if readonly else PyBUF_WRITE
    obj = PyMemoryView_GetContiguous(obj, buftype, c'A')
    cdef Py_buffer view
    cdef int flags = PyBUF_ANY_CONTIGUOUS
    if not readonly:
        flags |= PyBUF_WRITABLE
    if format != NULL:
        flags |= PyBUF_FORMAT
    PyObject_GetBuffer(obj, &view, flags)
    if format != NULL and view.format != NULL:
        if strncmp(format, view.format, 4) != 0:
            PyBuffer_Release(&view)
            raise ValueError(
                f"expecting buffer with format {pystr(format)!r}, "
                f"got {pystr(view.format)!r}")
    if base != NULL: base[0] = view.buf
    if size != NULL: size[0] = view.len // view.itemsize
    PyBuffer_Release(&view)
    return obj

# -----------------------------------------------------------------------------
