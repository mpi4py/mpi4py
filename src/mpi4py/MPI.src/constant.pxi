# -----------------------------------------------------------------------------


@cython.final
cdef class BottomType:
    """
    Type of `BOTTOM`.
    """

    cdef inline str as_str(self):
        return 'BOTTOM'
    cdef inline void* as_buf(self) noexcept nogil:
        return MPI_BOTTOM
    cdef inline MPI_Aint as_int(self) noexcept nogil:
        return <MPI_Aint>MPI_BOTTOM

    def __bool__(self) -> bool:
        return self.as_int() != 0

    def __int__(self) -> int:
        return self.as_int()

    def __index__(self) -> int:
        return self.as_int()

    def __hash__(self) -> int:
        return <Py_hash_t>self.as_int()

    def __eq__(self, object value) -> bool:
        if isinstance(value, type(self)): return True
        if not is_integral(value): return NotImplemented
        return self.as_int() == <MPI_Aint>value

    def __ne__(self, object value) -> bool:
        if isinstance(value, type(self)): return False
        if not is_integral(value): return NotImplemented
        return self.as_int() != <MPI_Aint>value

    def __getbuffer__(self, Py_buffer *view, int flags):
        PyBuffer_FillInfo(view, <object>NULL, self.as_buf(), 0, 0, flags)

    def __repr__(self) -> str:
        return self.as_str()

    def __reduce__(self) -> str:
        return self.as_str()


cdef object __BOTTOM__ = BottomType()

cdef inline bint is_BOTTOM(object obj):
    return obj is None or is_constant(obj, __BOTTOM__)

# -----------------------------------------------------------------------------


@cython.final
cdef class InPlaceType:
    """
    Type of `IN_PLACE`.
    """

    cdef inline str as_str(self):
        return 'IN_PLACE'
    cdef inline void* as_buf(self) noexcept nogil:
        return MPI_IN_PLACE
    cdef inline MPI_Aint as_int(self) noexcept nogil:
        return <MPI_Aint>MPI_IN_PLACE

    def __bool__(self) -> bool:
        return self.as_int() != 0

    def __int__(self) -> int:
        return self.as_int()

    def __hash__(self) -> int:
        return <Py_hash_t>self.as_int()

    def __eq__(self, object value) -> bool:
        if isinstance(value, type(self)): return True
        if not is_integral(value): return NotImplemented
        return self.as_int() == <MPI_Aint>value

    def __ne__(self, object value) -> bool:
        if isinstance(value, type(self)): return False
        if not is_integral(value): return NotImplemented
        return self.as_int() != <MPI_Aint>value

    def __getbuffer__(self, Py_buffer *view, int flags):
        PyBuffer_FillInfo(view, <object>NULL, self.as_buf(), 0, 0, flags)

    def __repr__(self) -> str:
        return self.as_str()

    def __reduce__(self) -> str:
        return self.as_str()


cdef object __IN_PLACE__ = InPlaceType()

cdef inline bint is_IN_PLACE(object obj):
    return obj is None or is_constant(obj, __IN_PLACE__)

# -----------------------------------------------------------------------------


@cython.final
cdef class BufferAutomaticType:
    """
    Type of `BUFFER_AUTOMATIC`.
    """

    cdef inline object as_str(self):
        return 'BUFFER_AUTOMATIC'
    cdef inline void* as_buf(self) noexcept nogil:
        return MPI_BUFFER_AUTOMATIC
    cdef inline MPI_Aint as_int(self) noexcept nogil:
        return <MPI_Aint>MPI_BUFFER_AUTOMATIC

    def __bool__(self) -> bool:
        return self.as_int() != 0

    def __int__(self) -> int:
        return self.as_int()

    def __hash__(self) -> int:
        return <Py_hash_t>self.as_int()

    def __eq__(self, object value) -> bool:
        if isinstance(value, type(self)): return True
        if not is_integral(value): return NotImplemented
        return self.as_int() == <MPI_Aint>value

    def __ne__(self, object value) -> bool:
        if isinstance(value, type(self)): return False
        if not is_integral(value): return NotImplemented
        return self.as_int() != <MPI_Aint>value

    def __getbuffer__(self, Py_buffer *view, int flags):
        PyBuffer_FillInfo(view, <object>NULL, self.as_buf(), 0, 0, flags)

    def __repr__(self) -> str:
        return self.as_str()

    def __reduce__(self) -> str:
        return self.as_str()


cdef object __BUFFER_AUTOMATIC__ = BufferAutomaticType()

cdef inline bint is_BUFFER_AUTOMATIC(object obj):
    return is_constant(obj, __BUFFER_AUTOMATIC__)

# -----------------------------------------------------------------------------
